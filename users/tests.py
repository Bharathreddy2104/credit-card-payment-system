from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient


class AuthenticationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Test@12345",
        }

    def test_user_registration(self):
        response = self.client.post(
            "/api/register/",
            self.user_data,
            format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.objects.filter(username="testuser").exists()
        )

    def test_user_login(self):
        User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Test@12345"
        )

        response = self.client.post(
            "/api/login/",
            {
                "username": "testuser",
                "password": "Test@12345",
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_requires_authentication(self):
        response = self.client.get("/api/profile/")

        self.assertEqual(response.status_code, 401)