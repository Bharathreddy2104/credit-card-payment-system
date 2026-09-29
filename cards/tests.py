from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Card


class CardManagementTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="cardtestuser",
            email="cardtest@example.com",
            password="Test@12345"
        )

        self.client.force_authenticate(user=self.user)

    def test_add_card(self):
        response = self.client.post(
            "/api/cards/",
            {
                "card_type": "CREDIT",
                "card_holder_name": "Test User",
                "card_number": "4111111111111111",
                "expiry_month": 12,
                "expiry_year": 2028,
                "cvv": "123"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            Card.objects.filter(user=self.user).count(),
            1
        )

    def test_list_cards(self):
        Card.objects.create(
            user=self.user,
            card_type="CREDIT",
            card_holder_name="Test User",
            masked_card_number="************1111",
            last_four_digits="1111",
            expiry_month=12,
            expiry_year=2028
        )

        response = self.client.get("/api/cards/list/")

        self.assertEqual(response.status_code, 200)

    def test_delete_card(self):
        card = Card.objects.create(
            user=self.user,
            card_type="CREDIT",
            card_holder_name="Test User",
            masked_card_number="************1111",
            last_four_digits="1111",
            expiry_month=12,
            expiry_year=2028
        )

        response = self.client.delete(
            f"/api/cards/delete/{card.id}/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Card.objects.filter(id=card.id).exists()
        )