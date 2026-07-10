"""Centralized Supabase Storage service layer.

Every upload/delete/signed-URL operation in the platform must go through
this module rather than calling the Supabase Storage REST API directly
from views — this is what keeps bucket privacy rules, MIME/size
validation, and safe path generation consistent everywhere (assignment
submissions, avatars, course thumbnails, certificate assets, resource
assets).

SUPABASE_SERVICE_ROLE_KEY is required for any privileged operation
(uploading to a private bucket, deleting, signing URLs) and is read only
from settings/env — it must never be sent to a template, to JavaScript,
or logged. If it isn't configured yet (no live Supabase project wired up),
every method here raises StorageNotConfiguredError instead of silently
no-opping, so callers can surface a clear error rather than pretending
an upload succeeded.
"""
import mimetypes
import uuid

import requests
from django.conf import settings

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp",
    "application/zip",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


class StorageError(Exception):
    """Base class for all storage service errors."""


class StorageNotConfiguredError(StorageError):
    """Raised when SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are missing."""


class InvalidBucketError(StorageError):
    pass


class InvalidFileError(StorageError):
    pass


def _require_config():
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise StorageNotConfiguredError(
            "Supabase Storage is not configured yet — set SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY in your environment. See "
            "docs/supabase-setup.md."
        )


def _validate_bucket(bucket: str):
    if bucket not in settings.SUPABASE_STORAGE_BUCKETS:
        raise InvalidBucketError(f"Unknown storage bucket: {bucket!r}")


def validate_mime_type(content_type: str):
    if content_type not in ALLOWED_MIME_TYPES:
        raise InvalidFileError(f"File type '{content_type}' is not permitted.")


def validate_file_size(size_bytes: int):
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise InvalidFileError(
            f"File is too large ({size_bytes} bytes). Maximum allowed is {MAX_FILE_SIZE_BYTES} bytes."
        )


def generate_safe_path(*segments: str, original_filename: str) -> str:
    """Builds a storage path from trusted segments (course/assignment/
    student UUIDs, etc.) plus a regenerated filename — the original
    filename is never trusted directly (spec 62), only its extension."""
    ext = ""
    if "." in original_filename:
        ext = "." + original_filename.rsplit(".", 1)[-1].lower()
        ext = "".join(ch for ch in ext if ch.isalnum() or ch == ".")[:10]
    safe_segments = [str(s).strip("/") for s in segments if s]
    generated_name = f"{uuid.uuid4().hex}{ext}"
    return "/".join(safe_segments + [generated_name])


class StorageService:
    """Thin wrapper over the Supabase Storage REST API. Uses `requests`
    directly rather than a full Supabase SDK to keep the dependency
    surface small and this module easy to mock in tests."""

    def __init__(self):
        self.base_url = settings.SUPABASE_URL.rstrip("/")
        self.service_role_key = settings.SUPABASE_SERVICE_ROLE_KEY

    def _headers(self, content_type=None):
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def upload(self, bucket: str, path: str, file_obj, content_type: str = None) -> str:
        _require_config()
        _validate_bucket(bucket)
        content_type = content_type or mimetypes.guess_type(path)[0] or "application/octet-stream"
        validate_mime_type(content_type)

        data = file_obj.read() if hasattr(file_obj, "read") else file_obj
        validate_file_size(len(data))

        url = f"{self.base_url}/storage/v1/object/{bucket}/{path}"
        response = requests.post(url, headers=self._headers(content_type), data=data, timeout=30)
        if response.status_code not in (200, 201):
            raise StorageError(f"Upload failed ({response.status_code}): {response.text}")
        return path

    def delete(self, bucket: str, path: str):
        _require_config()
        _validate_bucket(bucket)
        url = f"{self.base_url}/storage/v1/object/{bucket}/{path}"
        response = requests.delete(url, headers=self._headers(), timeout=30)
        if response.status_code not in (200, 204):
            raise StorageError(f"Delete failed ({response.status_code}): {response.text}")

    def public_url(self, bucket: str, path: str) -> str:
        _validate_bucket(bucket)
        if not settings.SUPABASE_STORAGE_BUCKETS[bucket].get("public"):
            raise InvalidBucketError(f"Bucket {bucket!r} is private — use signed_url() instead.")
        return f"{self.base_url}/storage/v1/object/public/{bucket}/{path}"

    def signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        """Generates a time-limited signed URL for a private bucket object
        — this is the only way authorized users should ever access
        assignment submissions or other private files."""
        _require_config()
        _validate_bucket(bucket)
        url = f"{self.base_url}/storage/v1/object/sign/{bucket}/{path}"
        response = requests.post(
            url, headers=self._headers("application/json"),
            json={"expiresIn": expires_in}, timeout=30,
        )
        if response.status_code != 200:
            raise StorageError(f"Signed URL generation failed ({response.status_code}): {response.text}")
        signed_path = response.json().get("signedURL")
        if not signed_path:
            raise StorageError("Supabase did not return a signed URL.")
        return f"{self.base_url}/storage/v1{signed_path}"


def get_storage_service() -> StorageService:
    return StorageService()
