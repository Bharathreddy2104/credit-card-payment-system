from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Transaction


class TransactionTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="transactionuser",
            email="transaction@example.com",
            password="Test@12345"
        )

        self.client.force_authenticate(user=self.user)

        self.transaction = Transaction.objects.create(
            user=self.user,
            amount="1000.00",
            status="SUCCESS",
            transaction_id="TXN-TEST-001",
            description="Test transaction"
        )

    def test_transaction_history(self):
        response = self.client.get(
            "/api/transactions/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["transaction_id"],
            "TXN-TEST-001"
        )

    def test_filter_by_status(self):
        response = self.client.get(
            "/api/transactions/?status=SUCCESS"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_amount(self):
        response = self.client.get(
            "/api/transactions/?min_amount=500&max_amount=1500"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)