import os

from base.models.processing_models import Resource
from django.urls import reverse


class UpdateWithoutNewFileTestMixin:
    """Edit a resource without choosing a new file.

    Mix this into a ``TestCase`` that runs with a temporary ``MEDIA_ROOT``.
    The test class names its update and detail URLs and creates a resource
    whose file is saved through storage, the way an upload saves it.
    """

    update_url_name = ""
    detail_url_name = ""

    def create_resource(self) -> Resource:
        raise NotImplementedError

    def update_data(self) -> dict[str, str]:
        return {
            "name": "Renamed resource",
            "description": "Edited without choosing a new file",
        }

    def test_update_without_new_file_keeps_file(self) -> None:
        resource = self.create_resource()
        stored_name = resource.file.name
        self.client.force_login(resource.creator)

        url = reverse(self.update_url_name, kwargs={"pk": resource.pk})
        response = self.client.post(url, self.update_data())

        self.assertRedirects(
            response,
            reverse(self.detail_url_name, kwargs={"pk": resource.pk}),
            fetch_redirect_response=False,
        )
        resource.refresh_from_db()
        self.assertEqual(resource.name, "Renamed resource")
        self.assertEqual(resource.file.name, stored_name)
        self.assertTrue(os.path.exists(resource.file.path))

    def test_author_sees_labelled_buttons_and_file_hint(self) -> None:
        resource = self.create_resource()
        self.client.force_login(resource.creator)
        update_url = reverse(self.update_url_name, kwargs={"pk": resource.pk})
        detail_url = reverse(self.detail_url_name, kwargs={"pk": resource.pk})
        delete_url = reverse(
            self.update_url_name.replace("_update", "_delete"),
            kwargs={"pk": resource.pk},
        )

        for approved in (False, True):
            resource.approved = approved
            resource.save()
            detail = self.client.get(detail_url)
            self.assertContains(detail, f'href="{update_url}"')
            self.assertContains(detail, "<span>Update</span>")
            self.assertContains(detail, f'href="{delete_url}"')
            self.assertContains(detail, "<span>Delete</span>")

        form = self.client.get(update_url)
