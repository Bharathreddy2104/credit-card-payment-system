from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(
            user=request.user
        ).order_by("-created_at")

        # Filter by status
        status_filter = request.query_params.get("status")
        if status_filter:
            transactions = transactions.filter(
                status=status_filter.upper()
            )

        # Filter by minimum amount
        min_amount = request.query_params.get("min_amount")
        if min_amount:
            transactions = transactions.filter(
                amount__gte=min_amount
            )

        # Filter by maximum amount
        max_amount = request.query_params.get("max_amount")
        if max_amount:
            transactions = transactions.filter(
                amount__lte=max_amount
            )

        # Filter by date
        date = request.query_params.get("date")
        if date:
            transactions = transactions.filter(
                created_at__date=date
            )

        serializer = TransactionSerializer(
            transactions,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
from django.db.models import Sum
from django.utils import timezone
from rest_framework.permissions import IsAdminUser


class DailyPaymentSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        today = timezone.localdate()

        transactions = Transaction.objects.filter(
            created_at__date=today
        )

        successful = transactions.filter(status="SUCCESS")
        failed = transactions.filter(status="FAILED")
        pending = transactions.filter(status="PENDING")

        total_success_amount = (
            successful.aggregate(total=Sum("amount"))["total"]
            or 0
        )

        return Response({
            "date": str(today),
            "total_transactions": transactions.count(),
            "successful_payments": successful.count(),
            "failed_payments": failed.count(),
            "pending_payments": pending.count(),
            "total_successful_amount": str(total_success_amount),
        })