import os
import tempfile

from base.views.processing_view import resource_notify, resource_update_notify
from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from screenshots.forms import UploadForm
from screenshots.models import Screenshot, Review

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshot_files")


class SetUpTest:
    """
    SetUp for all Test Class
    """

    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        self.file = os.path.join(SCREENSHOT_DIR, "main-create.webp")
        self.file_content = open(self.file, "rb")

        self.invalid_file = os.path.join(SCREENSHOT_DIR, "screenshot.txt")
        self.invalid_file_content = open(self.invalid_file, "rb")

        self.creator = User.objects.create(
            username="creator", email="creator@email.com"
        )
        # set creator password to password
        self.creator.set_password("password")
        self.creator.save()
        # Style manager
        self.style_manager = User.objects.create(username="style_manager", email="style_manager@email.com")
        self.style_manager.set_password("password")
        self.style_manager.save()
        self.group = Group.objects.create(name="Style Managers")
        self.group.user_set.add(self.style_manager)

        # Screenshot Publisher
        self.screenshot_publisher = User.objects.create(username="screenshot_publisher", email="screenshot_publisher@email.com")
        self.screenshot_publisher.set_password("password")
        self.screenshot_publisher.save()
        self.group = Group.objects.create(name="Map Publishers")
        self.group.user_set.add(self.screenshot_publisher)

    def tearDown(self):
        self.file_content.close()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestFormValidation(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def test_form_with_valid_data(self):
        uploaded_screenshot = SimpleUploadedFile(
            self.file_content.name, self.file_content.read()
        )
        form = UploadForm(data={})
        self.assertFalse(form.is_valid())
        data = {"name": "Homepage Screenshot", "description": "Test upload with valid data"}
        file_data = { "file": uploaded_screenshot}
        form = UploadForm(data, file_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_file_extension(self):
        uploaded_screenshot = SimpleUploadedFile(
            self.invalid_file_content.name, self.invalid_file_content.read()
        )
        data = {
            "name": "Invalid",
            "description": "Test upload invalid screenshot file extension",
        }
        file_data = { "file": uploaded_screenshot}
        form = UploadForm(data, file_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {"file": ["File extension “txt” is not allowed. Allowed extensions are: png, jpg, jpeg, gif, svg, webp, tiff, bmp."]})


@override_settings(MEDIA_ROOT="screenshots/tests/screenshot_files/")
class TestEmailNotification(SetUpTest, TestCase):
    """
    Send the email to console
    """

    fixtures = ["fixtures/simplemenu.json"]

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
    def test_print_email_notification_in_console(self):
        Screenshot.objects.create(
            creator=self.creator,
            name="Homepage Screenshot",
            description="A Screenshot for testing purpose",
            file=self.file,
        )
        screenshot = Screenshot.objects.first()
        resource_notify(screenshot, resource_type="Screenshot")
        Review.objects.create(
            reviewer=self.style_manager, resource=screenshot, comment="Rejected for testing purpose"
        )
        screenshot.require_action = True
        screenshot.save()
        resource_update_notify(
            screenshot, self.creator, self.style_manager, resource_type="Screenshot"
        )
        Review.objects.create(
            reviewer=self.style_manager,
            resource=screenshot,
            comment="Approved! This is for testing purpose",
        )
        screenshot.approved = True
        screenshot.save()
        resource_update_notify(
            screenshot, self.creator, self.style_manager, resource_type="Screenshot"
        )


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUploadScreenshot(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def test_upload_acceptable_size_file(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("screenshot_create")
        uploaded_screenshot = SimpleUploadedFile(
            self.file_content.name, self.file_content.read()
        )
        data = {
            "name": "Homepage Screenshot",
            "description": "Test upload an acceptable screenshot size",
            "file": uploaded_screenshot,
            "tags": "screenshot,project,test"
        }
        response = self.client.post(url, data, follow=True)
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "A new Resource has been created by creator."
        )
        screenshot = Screenshot.objects.first()
        self.assertEqual(screenshot.name, "Homepage Screenshot")
        # Check the tags
        self.assertEqual(
            screenshot.tags.filter(
                name__in=['screenshot', 'project', 'test']).count(),
            3)
        url = reverse("screenshot_detail", kwargs={"pk": screenshot.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUpdateScreenshot(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestUpdateScreenshot, self).setUp()
        self.screenshot_object = Screenshot.objects.create(
            creator=self.creator,
            name="Homepage Screenshot",
            description="A Screenshot for testing purpose",
            file=self.file,
        )

    def test_update_screenshot(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("screenshot_update", kwargs={"pk": self.screenshot_object.id})
        uploaded_screenshot = SimpleUploadedFile(
            self.file_content.name, self.file_content.read()
        )
        data = {
            "name": "Updated Screenshot",
            "description": "Test update screenshot",
            "file": uploaded_screenshot,
            "tags": "screenshot,project,test"
        }
        response = self.client.post(url, data, follow=True)
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        screenshot = Screenshot.objects.first()
        self.assertEqual(screenshot.name, "Updated Screenshot")
        # Check the tags
        self.assertEqual(
            screenshot.tags.filter(
                name__in=['screenshot', 'project', 'test']).count(),
            3)
        url = reverse("screenshot_detail", kwargs={"pk": screenshot.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

@override_settings(MEDIA_ROOT="screenshots/tests/screenshot_files/")
class TestReviewScreenshot(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestReviewScreenshot, self).setUp()
        self.screenshot_object = Screenshot.objects.create(
            creator=self.creator,
            name="Homepage Screenshot",
            description="A Screenshot for testing purpose",
            file=self.file,
        )

    def test_approve_screenshot(self):
        login = self.client.login(username="style_manager", password="password")
        self.assertTrue(login)
        url = reverse("screenshot_review", kwargs={"pk": self.screenshot_object.id})
        response = self.client.post(
            url, {"approval": "approve", "comment": "This should be in Approve page."}
        )
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse("screenshot_detail", kwargs={"pk": self.screenshot_object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This should be in Approve page.")
        self.assertContains(response, "Approved Date")
        self.client.logout()

    def test_reject_screenshot(self):
        login = self.client.login(username="style_manager", password="password")
        self.assertTrue(login)
        url = reverse("screenshot_review", kwargs={"pk": self.screenshot_object.id})
        response = self.client.post(
            url,
            {
                "approval": "reject",
                "comment": "This should be in requiring update page.",
            },
        )
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse("screenshot_detail", kwargs={"pk": self.screenshot_object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This should be in requiring update page.")
        self.assertContains(response, "Reviewed by Style_Manager now")
        self.client.logout()
        # creator should find the rejected styles in requiring update page
        self.client.login(username="creator", password="password")
        url = reverse("screenshot_require_action")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "Homepage Screenshot")

@override_settings(MEDIA_ROOT="screenshots/tests/screenshot_files/")
class TestTogglePublishScreenshot(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestTogglePublishScreenshot, self).setUp()
        self.screenshot_object = Screenshot.objects.create(
            creator=self.creator,
            name="Homepage Screenshot",
            description="A Screenshot for testing purpose",
            file=self.file,
            is_publishable=False,
        )

    def test_toggle_publish_screenshot(self):
        login = self.client.login(username="screenshot_publisher", password="password")
        self.assertTrue(login)
        url = reverse("screenshot_toggle_publish", kwargs={"pk": self.screenshot_object.id})
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse("screenshot_detail", kwargs={"pk": self.screenshot_object.id}))
        self.screenshot_object.refresh_from_db()
        self.assertTrue(self.screenshot_object.is_publishable)
        self.client.logout()

        # Toggle back to unpublish
        self.client.login(username="screenshot_publisher", password="password")
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse("screenshot_detail", kwargs={"pk": self.screenshot_object.id}))
        self.screenshot_object.refresh_from_db()
        self.assertFalse(self.screenshot_object.is_publishable)

    def test_toggle_publish_screenshot_no_permission(self):
        login = self.client.login(username="style_manager", password="password")
        self.assertTrue(login)
        url = reverse("screenshot_toggle_publish", kwargs={"pk": self.screenshot_object.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.screenshot_object.refresh_from_db()
        self.assertFalse(self.screenshot_object.is_publishable)
        self.client.logout()

        self.client.login(username="style_manager", password="password")
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.screenshot_object.refresh_from_db()
        self.assertFalse(self.screenshot_object.is_publishable)