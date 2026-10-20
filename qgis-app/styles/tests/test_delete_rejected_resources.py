"""Tests for the delete_rejected_resources management command."""

import os
import tempfile
from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from styles.models import Review, Style

MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA, REJECTED_RESOURCE_GRACE_DAYS=7)
class TestDeleteRejectedResources(TestCase):
    fixtures = ["fixtures/auth.json"]

    def setUp(self):
        self.creator = User.objects.get(pk=2)
        self.reviewer = User.objects.get(pk=3)

    def make_style(self, name, rejected_days_ago=None, require_action=True):
        style = Style.objects.create(
            creator=self.creator,
            name=name,
            description="A style for the cleanup tests",
            approved=False,
            require_action=require_action,
        )
        style.file.save(f"{name}.xml", ContentFile(b"<qgis_style/>"), save=True)
        if rejected_days_ago is not None:
            review = Review.objects.create(
                resource=style,
                reviewer=self.reviewer,
                comment="Please add a thumbnail",
            )
            # review_date is auto_now_add, so move it back afterwards
            Review.objects.filter(pk=review.pk).update(
                review_date=timezone.now() - timedelta(days=rejected_days_ago)
            )
        return style

    def run_command(self, *args):
        out = StringIO()
        call_command("delete_rejected_resources", *args, stdout=out)
        return out.getvalue()

    def test_reports_without_deleting_by_default(self):
        self.make_style("abandoned", rejected_days_ago=8)
        output = self.run_command()
        self.assertIn("Reporting only", output)
        self.assertIn("abandoned", output)
        self.assertIn("Would delete", output)
        self.assertEqual(Style.objects.count(), 1)

    def test_deletes_with_commit(self):
        style = self.make_style("abandoned", rejected_days_ago=8)
        path = style.file.path
        self.assertTrue(os.path.exists(path))
        output = self.run_command("--commit")
        self.assertIn("Deleted", output)
        self.assertEqual(Style.objects.count(), 0)
        self.assertFalse(os.path.exists(path))

    def test_keeps_a_resource_still_inside_the_grace_period(self):
        self.make_style("recent", rejected_days_ago=3)
        output = self.run_command("--commit")
        self.assertIn("Nothing to delete", output)
        self.assertEqual(Style.objects.count(), 1)

    def test_keeps_a_resource_the_author_fixed(self):
        # an update clears require_action, which takes it out of the queue
        self.make_style("fixed", rejected_days_ago=30, require_action=False)
        self.run_command("--commit")
        self.assertEqual(Style.objects.count(), 1)

    def test_days_overrides_the_setting(self):
        self.make_style("abandoned", rejected_days_ago=3)
        self.run_command("--commit", "--days", "2")
        self.assertEqual(Style.objects.count(), 0)

    def test_skips_a_rejected_resource_with_no_review(self):
        self.make_style("never-reviewed", rejected_days_ago=None)
        output = self.run_command("--commit")
        self.assertIn("has no review, skipping", output)
        self.assertEqual(Style.objects.count(), 1)

    def test_resource_limits_the_models_looked_at(self):
        self.make_style("abandoned", rejected_days_ago=8)
        self.run_command("--commit", "--resource", "map_gallery.Map")
        self.assertEqual(Style.objects.count(), 1)

    def test_unknown_resource_is_an_error(self):
        with self.assertRaises(CommandError):
            self.run_command("--resource", "nope.Nope")

    def test_zero_days_is_an_error(self):
        with self.assertRaises(CommandError):
            self.run_command("--days", "0")
