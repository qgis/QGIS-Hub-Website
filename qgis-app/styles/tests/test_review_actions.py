"""Tests for reviewing a style straight from the list.

Covers the Review action in the list templates, the confirmation page, the
permission gate on the review endpoint, and returning the reviewer to the page
they started from.
"""

import os
import tempfile

from django.contrib.auth.models import Group, User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from styles.models import Review, Style

STYLE_DIR = os.path.join(os.path.dirname(__file__), "stylefiles")


class SetupReviewTest:
    """A style waiting for review, its author, a reviewer and a bystander."""

    fixtures = ["fixtures/auth.json", "fixtures/simplemenu.json"]

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def setUp(self):
        self.creator = User.objects.get(pk=2)
        self.creator.set_password("password")
        self.creator.email = "creator@email.com"
        self.creator.save()

        self.manager = User.objects.get(pk=3)
        self.manager.is_staff = False
        self.manager.set_password("password")
        self.manager.email = "manager@email.com"
        self.manager.save()
        self.group = Group.objects.create(name="Style Managers")
        self.group.user_set.add(self.manager)

        self.bystander = User.objects.create_user(
            username="bystander", password="password", email="bystander@email.com"
        )

        self.style = Style.objects.create(
            creator=self.creator,
            name="Cat Trail",
            file="cattrail.xml",
            description="A style waiting for review",
            approved=False,
            require_action=False,
        )


class TestReviewActionInList(SetupReviewTest, TestCase):
    def test_reviewer_sees_the_review_action(self):
        self.client.login(username="staff", password="password")
        response = self.client.get(reverse("style_unapproved"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, reverse("style_review_confirm", kwargs={"pk": self.style.id})
        )

    def test_bystander_does_not_see_the_review_action(self):
        self.client.login(username="bystander", password="password")
        response = self.client.get(reverse("style_list"))
        self.assertNotContains(
            response, reverse("style_review_confirm", kwargs={"pk": self.style.id})
        )

    def test_approved_style_has_no_review_action(self):
        self.style.approved = True
        self.style.save()
        self.client.login(username="staff", password="password")
        response = self.client.get(reverse("style_list"))
        self.assertNotContains(
            response, reverse("style_review_confirm", kwargs={"pk": self.style.id})
        )


class TestResourceInReviewIsPrivate(SetupReviewTest, TestCase):
    """A resource awaiting review is only for its author and the reviewers."""

    def setUp(self):
        super().setUp()
        self.url = reverse("style_detail", kwargs={"pk": self.style.id})

    def test_anonymous_is_sent_to_sign_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertIn(self.url, response.url)

    def test_another_signed_in_user_is_told_nothing(self):
        self.client.login(username="bystander", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_the_author_can_see_it(self):
        self.client.login(username="creator", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base/review.html")

    def test_a_reviewer_can_see_it(self):
        self.client.login(username="staff", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_the_comment_history_does_not_leak(self):
        Review.objects.create(
            resource=self.style,
            reviewer=self.manager,
            comment="Rejected because the thumbnail is a screenshot",
        )
        self.client.login(username="bystander", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertNotIn(
            b"the thumbnail is a screenshot", response.content
        )

    def test_an_approved_resource_stays_public(self):
        self.style.approved = True
        self.style.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base/detail.html")

    def test_a_rejected_resource_is_private_too(self):
        self.style.require_action = True
        self.style.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class TestReviewConfirmPage(SetupReviewTest, TestCase):
    def test_reviewer_gets_the_page(self):
        self.client.login(username="staff", password="password")
        url = reverse("style_review_confirm", kwargs={"pk": self.style.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base/confirm_review.html")
        self.assertContains(response, "Submit review")

    def test_bystander_is_refused(self):
        self.client.login(username="bystander", password="password")
        url = reverse("style_review_confirm", kwargs={"pk": self.style.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_anonymous_is_sent_to_login(self):
        url = reverse("style_review_confirm", kwargs={"pk": self.style.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_approved_style_redirects_to_the_detail_page(self):
        self.style.approved = True
        self.style.save()
        self.client.login(username="staff", password="password")
        url = reverse("style_review_confirm", kwargs={"pk": self.style.id})
        response = self.client.get(url)
        self.assertRedirects(
            response, reverse("style_detail", kwargs={"pk": self.style.id})
        )

    def test_the_page_shows_earlier_comments(self):
        Review.objects.create(
            resource=self.style,
            reviewer=self.manager,
            comment="Please add a thumbnail",
        )
        self.client.login(username="staff", password="password")
        url = reverse("style_review_confirm", kwargs={"pk": self.style.id})
        response = self.client.get(url)
        self.assertContains(response, "Earlier comments")
        self.assertContains(response, "Please add a thumbnail")
        self.assertContains(response, "Reviewed by Staff")

    def test_a_first_review_shows_no_comment_history(self):
        self.client.login(username="staff", password="password")
        url = reverse("style_review_confirm", kwargs={"pk": self.style.id})
        response = self.client.get(url)
        self.assertNotContains(response, "Earlier comments")

    def test_the_page_keeps_the_list_to_return_to(self):
        self.client.login(username="staff", password="password")
        queue = reverse("style_unapproved")
        confirm = reverse("style_review_confirm", kwargs={"pk": self.style.id})
        url = f"{confirm}?next={queue}"
        response = self.client.get(url)
        self.assertContains(
            response,
            f'<input type="hidden" name="next" value="{queue}">',
            html=False,
        )


class TestReviewPermission(SetupReviewTest, TestCase):
    """The review endpoint used to accept any post. It must not."""

    def test_bystander_cannot_approve(self):
        self.client.login(username="bystander", password="password")
        url = reverse("style_review", kwargs={"pk": self.style.id})
        response = self.client.post(
            url, {"approval": "approve", "comment": "Looks fine to me"}
        )
        self.assertEqual(response.status_code, 404)
        self.style.refresh_from_db()
        self.assertFalse(self.style.approved)
        self.assertEqual(Review.objects.count(), 0)

    def test_anonymous_cannot_approve(self):
        url = reverse("style_review", kwargs={"pk": self.style.id})
        response = self.client.post(
            url, {"approval": "approve", "comment": "Looks fine to me"}
        )
        self.assertEqual(response.status_code, 302)
        self.style.refresh_from_db()
        self.assertFalse(self.style.approved)

    def test_group_member_who_is_not_staff_can_approve(self):
        self.client.login(username="staff", password="password")
        url = reverse("style_review", kwargs={"pk": self.style.id})
        self.client.post(url, {"approval": "approve", "comment": "Nice work"})
        self.style.refresh_from_db()
        self.assertTrue(self.style.approved)


class TestReviewReturnsToTheQueue(SetupReviewTest, TestCase):
    def test_review_returns_to_the_page_it_came_from(self):
        self.client.login(username="staff", password="password")
        queue = reverse("style_unapproved")
        response = self.client.post(
            reverse("style_review", kwargs={"pk": self.style.id}),
            {"approval": "approve", "comment": "Nice work", "next": queue},
        )
        self.assertRedirects(response, queue)

    def test_review_falls_back_to_the_waiting_queue(self):
        self.client.login(username="staff", password="password")
        response = self.client.post(
            reverse("style_review", kwargs={"pk": self.style.id}),
            {"approval": "reject", "comment": "Please add a thumbnail"},
        )
        self.assertRedirects(response, reverse("style_unapproved"))

    def test_an_offsite_next_is_ignored(self):
        self.client.login(username="staff", password="password")
        response = self.client.post(
            reverse("style_review", kwargs={"pk": self.style.id}),
            {
                "approval": "approve",
                "comment": "Nice work",
                "next": "https://example.com/phish",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("style_unapproved"))


@override_settings(REJECTED_RESOURCE_GRACE_DAYS=7)
class TestReviewEmail(SetupReviewTest, TestCase):
    def review(self, approval):
        self.client.login(username="staff", password="password")
        self.client.post(
            reverse("style_review", kwargs={"pk": self.style.id}),
            {"approval": approval, "comment": "Please add a thumbnail"},
        )
        return mail.outbox[-1]

    def test_rejection_names_the_grace_period(self):
        message = self.review("reject")
        self.assertIn("Please update your style within 7 days", message.body)
        self.assertIn("Please add a thumbnail", message.body)
        self.assertIn("rejected by staff", message.body)

    def test_approval_does_not_name_the_grace_period(self):
        message = self.review("approve")
        self.assertNotIn("7 days", message.body)
        self.assertIn("approved by staff", message.body)

    def test_the_author_is_told(self):
        message = self.review("reject")
        self.assertIn(self.creator.email, message.recipients())


class TestDeleteReturnsToTheList(SetupReviewTest, TestCase):
    def test_delete_does_not_return_to_the_deleted_resource(self):
        self.client.login(username="creator", password="password")
        detail = reverse("style_detail", kwargs={"pk": self.style.id})
        delete = reverse("style_delete", kwargs={"pk": self.style.id})
        url = f"{delete}?next={detail}"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("style_list"))

    def test_delete_returns_to_the_queue_it_came_from(self):
        self.client.login(username="creator", password="password")
        queue = reverse("style_unapproved")
        delete = reverse("style_delete", kwargs={"pk": self.style.id})
        url = f"{delete}?next={queue}"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, queue)
