from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Card
from .serializers import CardSerializer


class CardCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        card_number = request.data.get("card_number")
        card_holder_name = request.data.get("card_holder_name")
        card_type = request.data.get("card_type")
        expiry_month = request.data.get("expiry_month")
        expiry_year = request.data.get("expiry_year")
        cvv = request.data.get("cvv")

        # Required fields
        if not all([
            card_number,
            card_holder_name,
            card_type,
            expiry_month,
            expiry_year,
            cvv
        ]):
            return Response(
                {"error": "All card details are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate card type
        if card_type not in ["CREDIT", "DEBIT"]:
            return Response(
                {"error": "card_type must be CREDIT or DEBIT"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate card number
        card_number = str(card_number).replace(" ", "").replace("-", "")

        if not card_number.isdigit() or not 12 <= len(card_number) <= 19:
            return Response(
                {"error": "Invalid card number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate CVV
        cvv = str(cvv)

        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            return Response(
                {"error": "Invalid CVV"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate expiry month
        try:
            expiry_month = int(expiry_month)
            expiry_year = int(expiry_year)
        except (ValueError, TypeError):
            return Response(
                {"error": "Expiry month and year must be numbers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not 1 <= expiry_month <= 12:
            return Response(
                {"error": "Expiry month must be between 1 and 12"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get last 4 digits
        last_four_digits = card_number[-4:]

        # Create masked card number
        masked_card_number = (
            "*" * (len(card_number) - 4) + last_four_digits
        )

        # Save ONLY safe card information
        card = Card.objects.create(
            user=request.user,
            card_type=card_type,
            card_holder_name=card_holder_name,
            masked_card_number=masked_card_number,
            last_four_digits=last_four_digits,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
        )

        return Response(
            {
                "message": "Card added successfully",
                "card": CardSerializer(card).data
            },
            status=status.HTTP_201_CREATED
        )


class CardListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cards = Card.objects.filter(user=request.user)

        serializer = CardSerializer(cards, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CardDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, card_id):
        card = get_object_or_404(
            Card,
            id=card_id,
            user=request.user
        )

        card.delete()

        return Response(
            {"message": "Card deleted successfully"},
            status=status.HTTP_200_OK
        )