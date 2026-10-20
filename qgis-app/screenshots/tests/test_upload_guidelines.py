"""Tests for the guidelines checkbox on the upload screen.

Only maps and screenshots publish upload guidelines, so only those two ask the
author to agree to them. A style upload must not be asked.
"""

import os
import tempfile

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from screenshots.models import Screenshot
from styles.forms import UploadForm as StyleUploadForm

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshot_files")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUploadGuidelines(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        self.file = os.path.join(SCREENSHOT_DIR, "main-create.webp")
        self.creator = User.objects.create(
            username="creator", email="creator@email.com"
        )
        self.creator.set_password("password")
        self.creator.save()
        self.manager = User.objects.create(
            username="style_manager", email="style_manager@email.com"
        )
        self.manager.save()
        self.group = Group.objects.create(name="Style Managers")
        self.group.user_set.add(self.manager)
        self.client.login(username="creator", password="password")

    def post_screenshot(self, **extra):
        with open(self.file, "rb") as content:
            data = {
                "name": "Homepage Screenshot",
                "description": "A screenshot for the guidelines tests",
                "tags": "screenshot,test",
                "file": SimpleUploadedFile(content.name, content.read()),
            }
        data.update(extra)
        return self.client.post(reverse("screenshot_create"), data)

    def test_the_checkbox_is_on_the_screenshot_upload_page(self):
        response = self.client.get(reverse("screenshot_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "guidelines_acknowledged")
        self.assertContains(response, "may be removed if it does not")

    def test_upload_without_the_checkbox_is_refused(self):
        response = self.post_screenshot()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Screenshot.objects.count(), 0)
        self.assertFormError(
            response.context["form"],
            "guidelines_acknowledged",
            "This field is required.",
        )

    def test_upload_with_the_checkbox_succeeds(self):
        response = self.post_screenshot(guidelines_acknowledged=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Screenshot.objects.count(), 1)

    def test_the_update_page_does_not_ask_again(self):
        self.post_screenshot(guidelines_acknowledged=True)
        screenshot = Screenshot.objects.get()
        response = self.client.get(
            reverse("screenshot_update", kwargs={"pk": screenshot.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "guidelines_acknowledged")

    def test_the_map_upload_page_asks_too(self):
        response = self.client.get(reverse("map_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "guidelines_acknowledged")

    def test_a_resource_without_guidelines_does_not_ask(self):
        response = self.client.get(reverse("style_create"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "guidelines_acknowledged")
        self.assertNotIn("guidelines_acknowledged", StyleUploadForm().fields)
