from allauth.socialaccount.models import SocialLogin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from social_forms import SocialSignupForm

User = get_user_model()


class AuthConfigTest(TestCase):
    """django-allauth is wired into settings and URL config."""

    def test_allauth_apps_installed(self):
        for app in ("allauth", "allauth.account", "allauth.socialaccount"):
            self.assertIn(app, settings.INSTALLED_APPS)

    def test_allauth_backend_enabled(self):
        self.assertIn(
            "allauth.account.auth_backends.AuthenticationBackend",
            settings.AUTHENTICATION_BACKENDS,
        )

    def test_account_urls_resolve(self):
        self.assertEqual(reverse("account_login"), "/accounts/login/")
        self.assertEqual(reverse("account_logout"), "/accounts/logout/")
        # allauth social signup endpoint is available
        self.assertTrue(reverse("socialaccount_signup"))


class LoginPageTest(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def test_login_page_renders(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")

    def test_login_page_has_local_form(self):
        content = self.client.get(reverse("account_login")).content.decode()
        self.assertIn('name="login"', content)
        self.assertIn('name="password"', content)


class LocalLoginTest(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        self.password = "s3cr3t-p4ss"
        self.user = User.objects.create_user(
            username="localuser",
            email="local@example.com",
            password=self.password,
        )

    def test_local_login_succeeds(self):
        response = self.client.post(
            reverse("account_login"),
            {"login": "localuser", "password": self.password},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            int(self.client.session["_auth_user_id"]), self.user.pk
        )

    def test_local_login_wrong_password_fails(self):
        response = self.client.post(
            reverse("account_login"),
            {"login": "localuser", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)


class SocialSignupFormTest(TestCase):
    """The OAuth-provided email must be non-editable server-side so it cannot
    be spoofed by editing the readonly attribute in the browser."""

    def test_email_field_disabled(self):
        sociallogin = SocialLogin(
            user=User(username="socialuser", email="social@example.com")
        )
        form = SocialSignupForm(sociallogin=sociallogin)
        self.assertTrue(form.fields["email"].disabled)
