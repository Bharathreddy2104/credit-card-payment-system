from django.contrib import admin
from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "card_type",
        "card_holder_name",
        "last_four_digits",
        "expiry_month",
        "expiry_year",
        "created_at",
    )

    search_fields = (
        "card_holder_name",
        "last_four_digits",
        "user__username",
    )

    list_filter = (
        "card_type",
        "expiry_year",
    )