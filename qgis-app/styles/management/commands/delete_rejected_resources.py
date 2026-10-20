"""Remove rejected resources that the author never fixed.

A reviewer who rejects a resource sets require_action on it, and the author is
emailed a grace period. When the author updates the resource the flag clears
and the resource leaves this queue, so anything still flagged after the grace
period has been abandoned.

Meant to run from a crontab through dockerize/scripts/delete-rejected-resources.sh.
"""

from datetime import timedelta

from base.models.processing_models import Resource
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


def get_resource_models():
    """Every concrete resource model, so a new resource app is covered too."""

    return sorted(
        (
            model
            for model in apps.get_models()
            if issubclass(model, Resource) and not model._meta.abstract
        ),
        key=lambda model: model._meta.label,
    )


class Command(BaseCommand):
    help = (
        "Delete rejected resources that the author has not updated within the "
        "grace period. Reports what it would delete unless --commit is given."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=settings.REJECTED_RESOURCE_GRACE_DAYS,
            help=(
                "Days an author has to fix a rejected resource. Defaults to "
                "the REJECTED_RESOURCE_GRACE_DAYS setting."
            ),
        )
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Delete the resources. Without this the command only reports.",
        )
        parser.add_argument(
            "--resource",
            type=str,
            default=None,
            help=(
                "Only look at one model, given as app_label.ModelName, for "
                "example styles.Style."
            ),
        )

    def handle(self, *args, **options):
        days = options["days"]
        commit = options["commit"]
        wanted = options["resource"]

        if days < 1:
            raise CommandError("--days must be 1 or more.")

        models = get_resource_models()
        if wanted:
            models = [
                model
                for model in models
                if model._meta.label.lower() == wanted.lower()
            ]
            if not models:
                raise CommandError(f"No resource model named {wanted}.")

        cutoff = timezone.now() - timedelta(days=days)
        total = 0

        if not commit:
            self.stdout.write(
                self.style.WARNING(
                    "Reporting only. Pass --commit to delete these resources."
                )
            )

        for model in models:
            label = model._meta.label
            count = 0
            for resource in model.requireaction_objects.all():
                review = resource.review_set.last()
                if review is None:
                    self.stdout.write(
                        self.style.WARNING(
                            f"{label} {resource.pk} {resource.name!r} has no "
                            "review, skipping."
                        )
                    )
                    continue
                if review.review_date > cutoff:
                    continue

                age = (timezone.now() - review.review_date).days
                self.stdout.write(
                    f"{label} {resource.pk} {resource.name!r} by "
                    f"{resource.creator}, rejected {age} days ago."
                )
                if commit:
                    self.delete_resource(resource)
                count += 1

            if count:
                total += count
                verb = "Deleted from" if commit else "Would delete from"
                self.stdout.write(
                    self.style.SUCCESS(f"{verb} {label}: {count} resource(s).")
                )

        if total:
            verb = "Deleted" if commit else "Would delete"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{verb} {total} resource(s) rejected more than {days} "
                    "days ago."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Nothing to delete. No resource has been waiting for a "
                    f"fix longer than {days} days."
                )
            )

    def delete_resource(self, resource):
        """Remove the uploaded files as well as the row.

        Resource.delete already removes the main file, but it leaves the
        thumbnail behind, so we clear that first to avoid orphans.
        """

        thumbnail = getattr(resource, "thumbnail_image", None)
        if thumbnail:
            try:
                thumbnail.delete(save=False)
            except OSError as error:
                self.stdout.write(
                    self.style.ERROR(
                        "Could not remove the thumbnail of "
                        f"{resource._meta.label} {resource.pk}: {error}"
                    )
                )
        resource.delete()
