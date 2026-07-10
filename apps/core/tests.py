import io
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.core.services import storage


class StorageValidationTests(TestCase):
    def test_validate_mime_type_rejects_disallowed_type(self):
        with self.assertRaises(storage.InvalidFileError):
            storage.validate_mime_type("application/x-msdownload")

    def test_validate_mime_type_allows_pdf(self):
        storage.validate_mime_type("application/pdf")  # should not raise

    def test_validate_file_size_rejects_oversized_file(self):
        with self.assertRaises(storage.InvalidFileError):
            storage.validate_file_size(storage.MAX_FILE_SIZE_BYTES + 1)

    def test_generate_safe_path_ignores_original_filename_except_extension(self):
        path = storage.generate_safe_path(
            "assignments", "course-id", "assignment-id", "student-id",
            original_filename="../../etc/passwd.pdf",
        )
        self.assertTrue(path.endswith(".pdf"))
        self.assertNotIn("passwd", path)
        self.assertNotIn("..", path)
        self.assertTrue(path.startswith("assignments/course-id/assignment-id/student-id/"))

    def test_generate_safe_path_strips_unknown_extension_characters(self):
        path = storage.generate_safe_path("bucket", original_filename="evil.php;.jpg")
        # Extension characters are alnum-only, so no shell/path metacharacters survive.
        ext = path.rsplit(".", 1)[-1]
        self.assertTrue(ext.isalnum())

    @override_settings(SUPABASE_URL="", SUPABASE_SERVICE_ROLE_KEY="")
    def test_upload_fails_gracefully_when_not_configured(self):
        """Without live Supabase credentials, the service must raise a
        clear, typed error rather than silently no-opping or crashing with
        an unrelated exception."""
        service = storage.StorageService()
        with self.assertRaises(storage.StorageNotConfiguredError):
            service.upload("assignment-submissions", "some/path.pdf", io.BytesIO(b"data"), "application/pdf")

    @override_settings(SUPABASE_URL="https://example.supabase.co", SUPABASE_SERVICE_ROLE_KEY="fake-key")
    @patch("apps.core.services.storage.requests.post")
    def test_upload_succeeds_with_mocked_supabase_response(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = ""
        service = storage.StorageService()
        path = service.upload("assignment-submissions", "some/path.pdf", io.BytesIO(b"data"), "application/pdf")
        self.assertEqual(path, "some/path.pdf")
        mock_post.assert_called_once()

    @override_settings(SUPABASE_URL="https://example.supabase.co", SUPABASE_SERVICE_ROLE_KEY="fake-key")
    @patch("apps.core.services.storage.requests.post")
    def test_signed_url_generation_with_mocked_supabase_response(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"signedURL": "/object/sign/bucket/path?token=abc"}
        service = storage.StorageService()
        url = service.signed_url("assignment-submissions", "some/path.pdf")
        self.assertTrue(url.startswith("https://example.supabase.co/storage/v1/object/sign/"))

    def test_public_url_rejected_for_private_bucket(self):
        service = storage.StorageService()
        with self.assertRaises(storage.InvalidBucketError):
            service.public_url("assignment-submissions", "some/path.pdf")

    def test_unknown_bucket_rejected(self):
        service = storage.StorageService()
        with self.assertRaises(storage.InvalidBucketError):
            service.public_url("not-a-real-bucket", "path")
