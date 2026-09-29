from rest_framework import serializers
from .models import Card


class CardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Card
        fields = [
            "id",
            "card_type",
            "card_holder_name",
            "masked_card_number",
            "last_four_digits",
            "expiry_month",
            "expiry_year",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "masked_card_number",
            "last_four_digits",
            "created_at",
        ]