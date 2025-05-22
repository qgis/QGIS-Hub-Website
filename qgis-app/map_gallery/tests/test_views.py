import os
import tempfile

from base.views.processing_view import resource_notify, resource_update_notify
from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from map_gallery.forms import UploadForm
from map_gallery.models import Map, Review

MAP_DIR = os.path.join(os.path.dirname(__file__), "mapfiles")


class SetUpTest:
    """
    SetUp for all Test Class
    """

    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        self.file = os.path.join(MAP_DIR, "main-create.webp")
        self.file_content = open(self.file, "rb")

        self.invalid_file = os.path.join(MAP_DIR, "map.txt")
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

        # Map Publisher
        self.map_publisher = User.objects.create(username="map_publisher", email="map_publisher@email.com")
        self.map_publisher.set_password("password")
        self.map_publisher.save()
        self.group = Group.objects.create(name="Map Publishers")
        self.group.user_set.add(self.map_publisher)

    def tearDown(self):
        self.file_content.close()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestFormValidation(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def test_form_with_valid_data(self):
        uploaded_map = SimpleUploadedFile(
            self.file_content.name, self.file_content.read()
        )
        form = UploadForm(data={})
        self.assertFalse(form.is_valid())
        data = {"name": "Homepage Map", "description": "Test upload with valid data"}
        file_data = { "file": uploaded_map}
        form = UploadForm(data, file_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_file_extension(self):
        uploaded_map = SimpleUploadedFile(
            self.invalid_file_content.name, self.invalid_file_content.read()
        )
        data = {
            "name": "Invalid",
            "description": "Test upload invalid map file extension",
        }
        file_data = { "file": uploaded_map}
        form = UploadForm(data, file_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {"file": ["Upload a valid image. The file you uploaded was either not an image or a corrupted image."]})


@override_settings(MEDIA_ROOT="map_gallery/tests/mapfiles/")
class TestEmailNotification(SetUpTest, TestCase):
    """
    Send the email to console
    """

    fixtures = ["fixtures/simplemenu.json"]

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
    def test_print_email_notification_in_console(self):
        Map.objects.create(
            creator=self.creator,
            name="Homepage Map",
            description="A Map for testing purpose",
            file=self.file,
        )
        map = Map.objects.first()
        resource_notify(map, resource_type="Map")
        Review.objects.create(
            reviewer=self.style_manager, resource=map, comment="Rejected for testing purpose"
        )
        map.require_action = True
        map.save()
        resource_update_notify(
            map, self.creator, self.style_manager, resource_type="Map"
        )
        Review.objects.create(
            reviewer=self.style_manager,
            resource=map,
            comment="Approved! This is for testing purpose",
        )
        map.approved = True
        map.save()
        resource_update_notify(
            map, self.creator, self.style_manager, resource_type="Map"
        )


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUploadMap(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def test_upload_acceptable_size_file(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("map_create")
        uploaded_map = SimpleUploadedFile(
            self.file_content.name, self.file_content.read()
        )
        data = {
            "name": "Homepage Map",
            "description": "Test upload an acceptable map size",
            "file": uploaded_map,
            "tags": "map,project,test"
        }
        response = self.client.post(url, data, follow=True)
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "A new Resource has been created by creator."
        )
        map = Map.objects.first()
        self.assertEqual(map.name, "Homepage Map")
        # Check the tags
        self.assertEqual(
            map.tags.filter(
                name__in=['map', 'project', 'test']).count(),
            3)
        url = reverse("map_detail", kwargs={"pk": map.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUpdateMap(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestUpdateMap, self).setUp()
        self.map_object = Map.objects.create(
            creator=self.creator,
            name="Homepage Map",
            description="A Map for testing purpose",
            file=self.file,
        )

    def test_update_map(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("map_update", kwargs={"pk": self.map_object.id})
        uploaded_map = SimpleUploadedFile(
            self.file_content.name, self.file_content.read()
        )
        data = {
            "name": "Updated Map",
            "description": "Test update map",
            "file": uploaded_map,
            "tags": "map,project,test"
        }
        response = self.client.post(url, data, follow=True)
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        map = Map.objects.first()
        self.assertEqual(map.name, "Updated Map")
        # Check the tags
        self.assertEqual(
            map.tags.filter(
                name__in=['map', 'project', 'test']).count(),
            3)
        url = reverse("map_detail", kwargs={"pk": map.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

@override_settings(MEDIA_ROOT="map_gallery/tests/mapfiles/")
class TestReviewMap(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestReviewMap, self).setUp()
        self.map_object = Map.objects.create(
            creator=self.creator,
            name="Homepage Map",
            description="A Map for testing purpose",
            file=self.file,
        )

    def test_approve_map(self):
        login = self.client.login(username="style_manager", password="password")
        self.assertTrue(login)
        url = reverse("map_review", kwargs={"pk": self.map_object.id})
        response = self.client.post(
            url, {"approval": "approve", "comment": "This should be in Approve page."}
        )
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse("map_detail", kwargs={"pk": self.map_object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "This should be in Approve page.")
        self.assertContains(response, "Approved Date")
        self.client.logout()

    def test_reject_map(self):
        login = self.client.login(username="style_manager", password="password")
        self.assertTrue(login)
        url = reverse("map_review", kwargs={"pk": self.map_object.id})
        response = self.client.post(
            url,
            {
                "approval": "reject",
                "comment": "This should be in requiring update page.",
            },
        )
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse("map_detail", kwargs={"pk": self.map_object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This should be in requiring update page.")
        self.assertContains(response, "Reviewed by Style_Manager now")
        self.client.logout()
        # creator should find the rejected styles in requiring update page
        self.client.login(username="creator", password="password")
        url = reverse("map_require_action")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "Homepage Map")

@override_settings(MEDIA_ROOT="map_gallery/tests/mapfiles/")
class TestTogglePublishMap(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestTogglePublishMap, self).setUp()
        self.map_object = Map.objects.create(
            creator=self.creator,
            name="Homepage Map",
            description="A Map for testing purpose",
            file=self.file,
            is_publishable=False,
        )

    def test_toggle_publish_map(self):
        login = self.client.login(username="map_publisher", password="password")
        self.assertTrue(login)
        url = reverse("map_toggle_publish", kwargs={"pk": self.map_object.id})
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse("map_detail", kwargs={"pk": self.map_object.id}))
        self.map_object.refresh_from_db()
        self.assertTrue(self.map_object.is_publishable)
        self.client.logout()

        # Toggle back to unpublish
        self.client.login(username="map_publisher", password="password")
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse("map_detail", kwargs={"pk": self.map_object.id}))
        self.map_object.refresh_from_db()
        self.assertFalse(self.map_object.is_publishable)

    def test_toggle_publish_map_no_permission(self):
        login = self.client.login(username="style_manager", password="password")
        self.assertTrue(login)
        url = reverse("map_toggle_publish", kwargs={"pk": self.map_object.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.map_object.refresh_from_db()
        self.assertFalse(self.map_object.is_publishable)
        self.client.logout()

        self.client.login(username="style_manager", password="password")
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.map_object.refresh_from_db()
        self.assertFalse(self.map_object.is_publishable)
