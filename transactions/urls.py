from django.urls import path

from .views import (
    TransactionHistoryView,
    DailyPaymentSummaryView,
)


urlpatterns = [
    path(
        "",
        TransactionHistoryView.as_view(),
        name="transaction-history",
    ),

    path(
        "daily-summary/",
        DailyPaymentSummaryView.as_view(),
        name="daily-payment-summary",
    ),
]