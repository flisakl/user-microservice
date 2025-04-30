from django.test import TestCase
from ninja.testing import TestClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
import jwt
import datetime

from .api import router  # Import your Ninja router

User = get_user_model()
client = TestClient(router)


class UserAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass", is_instructor=False
        )

    def generate_token(self, user, iat_delta: datetime.timedelta = None):
        now = timezone.now()
        payload = {
            "id": user.pk,
            "username": user.username,
            "is_instructor": user.is_instructor,
            "exp": now + datetime.timedelta(hours=2),
            "iat": now
        }
        if iat_delta:
            payload["exp"] += iat_delta
        return jwt.encode(payload, settings.RSA_PRIVATE_KEY, algorithm="RS256")

    def test_guest_can_create_account(self):
        response = client.post("/register", json={
            "username": "newuser",
            "password": "newpass",
            "is_instructor": True
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.json())

    def test_guest_can_log_in_with_valid_credentials(self):
        response = client.post("/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_guest_can_not_login_with_invalid_data(self):
        response = client.post("/login", json={
            "username": "testuser",
            "password": "wrongpass"
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())

    def test_user_can_regenerate_token(self):
        offset = datetime.timedelta(hours=-10)
        token = self.generate_token(self.user, offset)
        response = client.post("/regenerate-token", json={"token": token})
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())
        self.assertNotEqual(response.json()["token"], token)

    def test_user_can_fetch_another_user_info(self):
        token = self.generate_token(self.user)
        response = client.get(f"/{self.user.pk}", headers={
            "Authorization": f"Bearer {token}"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "testuser")

    def test_guest_can_not_get_user_info(self):
        response = client.get(f"/{self.user.id}", headers={
            "Authorization": "Bearer bad.token"
        })
        self.assertEqual(response.status_code, 401)

    def test_authentication_fails_when_token_is_expired(self):
        offset = datetime.timedelta(hours=-10)
        token = self.generate_token(self.user, offset)
        response = client.get(f"/{self.user.pk}", headers={
            "Authorization": f"Bearer {token}"
        })
        self.assertEqual(response.status_code, 401)
        json = response.json()["detail"]
        self.assertIn("expired", json)
