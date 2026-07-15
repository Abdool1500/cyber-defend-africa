from django.core.management.base import BaseCommand

from apps.enrollments.models import Enrollment


class Command(BaseCommand):
    help = (
        "One-off backfill for the 16.Q fix to Enrollment.recalculate_progress(): "
        "before that fix, nothing in the application ever set status to COMPLETED, "
        "so any enrollment that reached 100% progress before this fix shipped is "
        "still sitting at ACTIVE. Re-running recalculate_progress() on every ACTIVE "
        "enrollment lets the new auto-completion logic catch up. Idempotent — safe "
        "to run more than once, and a no-op for enrollments below 100%."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report how many enrollments would be marked COMPLETED without saving anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        active_enrollments = Enrollment.objects.filter(status=Enrollment.Status.ACTIVE)
        total = active_enrollments.count()
        would_complete = 0

        for enrollment in active_enrollments:
            if dry_run:
                if enrollment.progress_percentage == 100:
                    would_complete += 1
                continue
            before = enrollment.status
            enrollment.recalculate_progress()
            if enrollment.status != before:
                would_complete += 1

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: {would_complete} of {total} active enrollments would be marked COMPLETED."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Backfilled {total} active enrollments — {would_complete} newly marked COMPLETED."
                )
            )
