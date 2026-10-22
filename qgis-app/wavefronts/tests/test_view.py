import io
import os
import tempfile
import zipfile

from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from wavefronts.models import Wavefront

WAVEFRONT_DIR = os.path.join(os.path.dirname(__file__), "wavefrontfiles")


class SetUpTest:
    """
    SetUp for all Test Class
    """

    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        self.thumbnail = os.path.join(WAVEFRONT_DIR, "thumbnail.png")
        self.thumbnail_content = open(self.thumbnail, "rb")
        self.zipfile = os.path.join(WAVEFRONT_DIR, "odm_texturing_25d.zip")
        self.zipfile_content = open(self.zipfile, "rb")

        self.creator = User.objects.create(
            username="creator", email="creator@email.com"
        )
        # set creator password to password
        self.creator.set_password("password")
        self.creator.save()
        self.staff = User.objects.create(username="staff", email="staff@email.com")
        self.staff.set_password("password")
        self.staff.save()
        self.group = Group.objects.create(name="Style Managers")
        self.group.user_set.add(self.staff)

    def tearDown(self):
        self.thumbnail_content.close()
        self.zipfile_content.close()


class TestPageUserAnonymous(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def test_url(self):
        url = reverse("wavefront_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All 3D Models")
        self.assertContains(response, "No data.")

    def test_upload(self):
        url = reverse("wavefront_create")
        response = self.client.get(url)
        self.assertRedirects(response, "/accounts/login/?next=/wavefronts/add/")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestReviewWavefront(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestReviewWavefront, self).setUp()
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("wavefront_create")
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_file = SimpleUploadedFile(
            self.zipfile_content.name, self.zipfile_content.read()
        )
        data = {
            "name": "odm texturing",
            "description": "Test upload a wavefront",
            "thumbnail_image": uploaded_thumbnail,
            "file": uploaded_file,
            "tags": "3dmodel,wavefront,test"
        }
        self.client.post(url, data, follow=True)
        self.object = Wavefront.objects.first()
        self.client.logout()

    def test_tags_wavefront(self):
        # Check the tags
        self.assertEqual(
            self.object.tags.filter(
                name__in=['3dmodel', 'wavefront', 'test']).count(),
            3)

    def test_approve_wavefront(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse("wavefront_review", kwargs={"pk": self.object.id})
        response = self.client.post(
            url, {"approval": "approve", "comment": "This should be in Approve page."}
        )
        # should send email notify
        self.assertIn(
            "\n3D Model odm texturing approved by staff."
            "\nThis should be in Approve page.",
            mail.outbox[-1].body,
        )
        self.assertRedirects(response, reverse("wavefront_unapproved"))
        url = reverse("wavefront_detail", kwargs={"pk": self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<strong>staff</strong> approved these changes now </span>")
        self.assertContains(response, "Approved Date")
        self.client.logout()

    def test_reject_model(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse("wavefront_review", kwargs={"pk": self.object.id})
        response = self.client.post(
            url,
            {
                "approval": "reject",
                "comment": "This should be in requiring update page.",
            },
        )
        # should send email notify
        self.assertIn(
            "\n3D Model odm texturing rejected by staff."
            "\nThis should be in requiring update page.",
            mail.outbox[-1].body,
        )
        self.assertRedirects(response, reverse("wavefront_unapproved"))
        url = reverse("wavefront_detail", kwargs={"pk": self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This should be in requiring update page.")
        self.assertContains(response, "Reviewed by Staff now")
        self.client.logout()
        # creator should find the rejected styles in requiring update page
        self.client.login(username="creator", password="password")
        url = reverse("wavefront_require_action")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "odm texturing")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUpdateWavefront(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestUpdateWavefront, self).setUp()
        self.wavefront_object = Wavefront.objects.create(
            name="odm texturing",
            description="Test upload a wavefront",
            thumbnail_image=self.thumbnail,
            file=self.zipfile,
            creator=self.creator,
        )

    def test_update_wavefront(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("wavefront_update", kwargs={"pk": self.wavefront_object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_file = SimpleUploadedFile(
            self.zipfile_content.name, self.zipfile_content.read()
        )

        data = {
            "name": "odm texturing",
            "description": "Test update a wavefront",
            "thumbnail_image": uploaded_thumbnail,
            "file": uploaded_file,
            "tags": "3dmodel,wavefront,test"
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("wavefront_detail", kwargs={"pk": self.wavefront_object.id}))
        # check the wavefront
        wavefront = Wavefront.objects.get(id=self.wavefront_object.id)
        self.assertEqual(wavefront.name, "odm texturing")
        self.assertEqual(wavefront.description, "Test update a wavefront")

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestDownloadWavefront(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestDownloadWavefront, self).setUp()
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("wavefront_create")
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_file = SimpleUploadedFile(
            self.zipfile_content.name, self.zipfile_content.read()
        )
        data = {
            "name": "odm texturing",
            "description": "Test upload a wavefront",
            "thumbnail_image": uploaded_thumbnail,
            "file": uploaded_file,
        }
        self.client.post(url, data, follow=True)
        self.object = Wavefront.objects.first()
        self.client.logout()

    def test_download_should_return_zipfile(self):
        wavefront = Wavefront.objects.last()
        wavefront.approved = True
        wavefront.save()
        url = reverse("wavefront_download", kwargs={"pk": wavefront.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get("Content-Disposition"),
            "attachment; filename=odm-texturing.zip",
        )
        expected_filename_list = [
            "odm texturing/odm_textured_model_geo.mtl",
            "odm texturing/odm_textured_model_geo_material0000_map_Kd.png",
            "odm texturing/odm_textured_model.mtl",
            "odm texturing/odm_textured_model_geo.conf",
            "odm texturing/odm_textured_model_geo.obj",
            "odm texturing/license.txt",
        ]
        with io.BytesIO(response.content) as file:
            zip_file = zipfile.ZipFile(file, "r")
            self.assertIsNone(zip_file.testzip())
            for f in expected_filename_list:
                self.assertIn(f, zip_file.namelist())
            self.assertNotIn(
                "odm texturing/odm_textured_model_geo.zip", zip_file.namelist()
            )
            zip_file.close()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestGlbWavefront(SetUpTest, TestCase):
    """A GLB model, uploaded on its own and inside a zip file."""

    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestGlbWavefront, self).setUp()
        self.assertTrue(self.client.login(username="creator", password="password"))

    def fixture(self, name):
        """Read one of the GLB files in wavefrontfiles.

        These are real models: a tree with geometry, two materials and an
        embedded bark texture.
        """
        with open(os.path.join(WAVEFRONT_DIR, name), "rb") as model:
            return model.read()

    def upload(self, name, content):
        url = reverse("wavefront_create")
        data = {
            "name": "Apple tree",
            "description": "A tree in one GLB file",
            "thumbnail_image": SimpleUploadedFile(
                self.thumbnail_content.name, self.thumbnail_content.read()
            ),
            "file": SimpleUploadedFile(name, content),
            "tags": "3dmodel,glb",
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        return Wavefront.objects.last()

    def test_upload_a_glb_on_its_own(self):
        wavefront = self.upload("tree.glb", self.fixture("tree.glb"))
        self.assertIsNotNone(wavefront)
        self.assertTrue(wavefront.file.name.endswith(".glb"))
        self.assertEqual(wavefront.model_format, "glb")
        self.assertTrue(os.path.exists(wavefront.file.path))

    def test_upload_a_glb_inside_a_zip(self):
        wavefront = self.upload("tree-zipped.zip", self.fixture("tree-zipped.zip"))
        self.assertIsNotNone(wavefront)
        self.assertTrue(wavefront.file.name.endswith(".zip"))
        self.assertEqual(wavefront.model_format, "glb")

    def test_upload_a_broken_glb_is_refused(self):
        url = reverse("wavefront_create")
        data = {
            "name": "Broken tree",
            "description": "Not really a model",
            "thumbnail_image": SimpleUploadedFile(
                self.thumbnail_content.name, self.thumbnail_content.read()
            ),
            "file": SimpleUploadedFile(
                "broken-tree.glb", self.fixture("broken-tree.glb")
            ),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Wavefront.objects.count(), 0)
        self.assertContains(response, "This is not a GLB file")

    def test_detail_page_points_the_viewer_at_the_glb(self):
        wavefront = self.upload("tree.glb", self.fixture("tree.glb"))
        wavefront.approved = True
        wavefront.save()
        url = reverse("wavefront_detail", kwargs={"pk": wavefront.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-format="glb"')
        self.assertContains(response, wavefront.file.url)
        self.assertContains(response, "View in 3D")

    def test_review_page_shows_the_viewer(self):
        wavefront = self.upload("tree.glb", self.fixture("tree.glb"))
        self.assertFalse(wavefront.approved)
        url = reverse("wavefront_detail", kwargs={"pk": wavefront.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base/review.html")
        self.assertContains(response, 'data-format="glb"')

    def test_download_a_glb_sends_the_model_and_the_licence(self):
        wavefront = self.upload("tree.glb", self.fixture("tree.glb"))
        wavefront.approved = True
        wavefront.save()
        url = reverse("wavefront_download", kwargs={"pk": wavefront.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        with io.BytesIO(response.content) as content:
            zip_file = zipfile.ZipFile(content, "r")
            self.assertIsNone(zip_file.testzip())
            names = zip_file.namelist()
            # Two people may both upload tree.glb, so the stored name is not
            # always the name it arrived under.
            stored = os.path.basename(wavefront.file.name)
            self.assertIn(f"Apple tree/{stored}", names)
            self.assertTrue(stored.endswith(".glb"))
            self.assertIn("Apple tree/license.txt", names)
            zip_file.close()
