import os
import tempfile

from base.views.processing_view import resource_notify, resource_update_notify
from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from processing_scripts.forms import UploadForm
from processing_scripts.models import ProcessingScript, Review

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "processing_files")


class SetUpTest:
  """
  SetUp for all Test Class
  """

  fixtures = ["fixtures/simplemenu.json"]

  def setUp(self):
    self.thumbnail = os.path.join(SCRIPT_DIR, "thumbnail.png")
    self.thumbnail_content = open(self.thumbnail, "rb")
    self.file = os.path.join(SCRIPT_DIR, "example.py")
    self.file_content = open(self.file, "rb")
    self.invalid_script = os.path.join(SCRIPT_DIR, "invalid_script.py")
    self.invalid_script_content = open(self.invalid_script, "rb")

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
    self.file_content.close()
    self.invalid_script_content.close()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestFormValidation(SetUpTest, TestCase):
  fixtures = ["fixtures/simplemenu.json"]

  def test_form_with_valid_data(self):
    uploaded_thumbnail = SimpleUploadedFile(
      self.thumbnail_content.name, self.thumbnail_content.read()
    )
    uploaded_script = SimpleUploadedFile(
      self.file_content.name, self.file_content.read()
    )
    form = UploadForm(data={})
    self.assertFalse(form.is_valid())
    data = {
      "name": "flooded building extractor",
      "description": "Test upload with valid data",
      "dependencies": "QuickOSM"
    }
    file_data = {"thumbnail_image": uploaded_thumbnail, "file": uploaded_script}
    form = UploadForm(data, file_data)
    self.assertTrue(form.is_valid())

  def test_form_invalid_file_extension(self):
    uploaded_thumbnail = SimpleUploadedFile(
      self.thumbnail_content.name, self.thumbnail_content.read()
    )
    uploaded_script = SimpleUploadedFile(
      self.thumbnail_content.name, self.thumbnail_content.read()
    )
    data = {
      "name": "flooded buildings extractor",
      "description": "Test upload invalid script file extension",
    }
    file_data = {"thumbnail_image": uploaded_thumbnail, "file": uploaded_script}
    form = UploadForm(data, file_data)
    self.assertFalse(form.is_valid())
    self.assertEqual(form.errors, {"file": ["The submitted file is empty."]})

  def test_form_invalid_script(self):
    uploaded_thumbnail = SimpleUploadedFile(
      self.thumbnail_content.name, self.thumbnail_content.read()
    )
    uploaded_script = SimpleUploadedFile(
      self.invalid_script_content.name, self.invalid_script_content.read()
    )
    data = {
      "name": "flooded buildings extractor",
      "description": "Test upload invalid script filesize",
      "dependencies": "QuickOSM"
    }
    file_data = {"thumbnail_image": uploaded_thumbnail, "file": uploaded_script}
    form = UploadForm(data, file_data)
    self.assertFalse(form.is_valid())
    self.assertEqual(
      form.errors, {"file": ["Script must contain a class that inherits from QgsProcessingAlgorithm."]}
    )


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUpdateScript(SetUpTest, TestCase):
  """
  Test the update script view
  """
  fixtures = ["fixtures/simplemenu.json"]
  def setUp(self):
    super(TestUpdateScript, self).setUp()
    self.processing_script = ProcessingScript.objects.create(
      creator=self.creator,
      name="flooded buildings extractor",
      description="A ProcessingScript for testing purpose",
      dependencies="QuickOSM",
      thumbnail_image=self.thumbnail,
      file=self.file,
    )
    self.processing_script.save()

  def test_update_script(self):
    self.client.login(username="creator", password="password")
    url = reverse("processing_script_update", kwargs={"pk": self.processing_script.id})
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    uploaded_thumbnail = SimpleUploadedFile(
      self.thumbnail_content.name, self.thumbnail_content.read()
    )
    uploaded_file = SimpleUploadedFile(
      self.file_content.name, self.file_content.read()
    )
    data = {
      "name": "Modified Script",
      "description": "A ProcessingScript for testing purpose",
      "dependencies": "QuickOSM",
      "thumbnail_image": uploaded_thumbnail,
      "file": uploaded_file,
    }
    response = self.client.post(url, data, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertRedirects(response, reverse("processing_script_detail", kwargs={"pk": self.processing_script.id}))
    # check the processing script
    processing_script = ProcessingScript.objects.get(id=self.processing_script.id)
    self.assertEqual(processing_script.name, "Modified Script")

  def test_update_script_invalid_file(self):
    self.client.login(username="creator", password="password")
    url = reverse("processing_script_update", kwargs={"pk": self.processing_script.id})
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    uploaded_thumbnail = SimpleUploadedFile(
      self.thumbnail_content.name, self.thumbnail_content.read()
    )
    uploaded_file = SimpleUploadedFile(
      self.invalid_script_content.name, self.invalid_script_content.read()
    )
    data = {
      "name": "Modified Script",
      "description": "A ProcessingScript for testing purpose",
      "dependencies": "QuickOSM",
      "thumbnail_image": uploaded_thumbnail,
      "file": uploaded_file,
    }
    response = self.client.post(url, data, follow=True)
    self.assertEqual(response.status_code, 200)
    # check the processing script
    processing_script = ProcessingScript.objects.get(id=self.processing_script.id)
    self.assertEqual(processing_script.name, "flooded buildings extractor")


@override_settings(MEDIA_ROOT="processing_scripts/tests/processing_files/")
class TestEmailNotification(SetUpTest, TestCase):
  """
  Send the email to console
  """

  fixtures = ["fixtures/simplemenu.json"]

  @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
  def test_print_email_notification_in_console(self):
    ProcessingScript.objects.create(
      creator=self.creator,
      name="flooded buildings extractor",
      description="A ProcessingScript for testing purpose",
      dependencies="QuickOSM",
      thumbnail_image=self.thumbnail,
      file=self.file,
    )
    processing_script = ProcessingScript.objects.first()
    resource_notify(processing_script, resource_type="ProcessingScript")
    Review.objects.create(
      reviewer=self.staff, resource=processing_script, comment="Rejected for testing purpose"
    )
    processing_script.require_action = True
    processing_script.save()
    resource_update_notify(processing_script, self.creator, self.staff, resource_type="ProcessingScript")
    Review.objects.create(
      reviewer=self.staff,
      resource=processing_script,
      comment="Approved! This is for testing purpose",
    )
    processing_script.approved = True
    processing_script.save()
    resource_update_notify(processing_script, self.creator, self.staff, resource_type="ProcessingScript")

@override_settings(MEDIA_ROOT="processing_scripts/tests/processing_files/")
class TestReviewProcessingScript(SetUpTest, TestCase):
  fixtures = ["fixtures/simplemenu.json"]

  def setUp(self):
    super(TestReviewProcessingScript, self).setUp()
    self.processing_script_object = ProcessingScript.objects.create(
      creator=self.creator,
      name="flooded buildings extractor",
      description="A ProcessingScript for testing purpose",
      thumbnail_image=self.thumbnail,
      file=self.file,
    )

  def test_approve_processing_script(self):
    login = self.client.login(username="staff", password="password")
    self.assertTrue(login)
    url = reverse("processing_script_review", kwargs={"pk": self.processing_script_object.id})
    response = self.client.post(
      url, {"approval": "approve", "comment": "This should be in Approve page."}
    )
    # should send email notify
    self.assertEqual(len(mail.outbox), 1)
    url = reverse("processing_script_detail", kwargs={"pk": self.processing_script_object.id})
    self.assertRedirects(response, url)
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertNotContains(response, "This should be in Approve page.")
    self.assertContains(response, "Approved Date")
    self.client.logout()

  def test_reject_processing_script(self):
    login = self.client.login(username="staff", password="password")
    self.assertTrue(login)
    url = reverse("processing_script_review", kwargs={"pk": self.processing_script_object.id})
    response = self.client.post(
      url,
      {
        "approval": "reject",
        "comment": "This should be in requiring update page.",
      },
    )
    # should send email notify
    self.assertEqual(len(mail.outbox), 1)
    url = reverse("processing_script_detail", kwargs={"pk": self.processing_script_object.id})
    self.assertRedirects(response, url)
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "This should be in requiring update page.")
    self.assertContains(response, "Reviewed by Staff now")
    self.client.logout()
    # creator should find the rejected styles in requiring update page
    self.client.login(username="creator", password="password")
    url = reverse("processing_script_require_action")
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "1 record found.")
    self.assertContains(response, "flooded buildings extractor")
