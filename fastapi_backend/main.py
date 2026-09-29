import os
import uuid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from decimal import Decimal

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from cards.models import Card
from transactions.models import Transaction


app = FastAPI()

security = HTTPBearer()


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "FastAPI backend is running"
    }


# =========================================================
# ABOUT
# =========================================================

@app.get("/about")
def about():
    return {
        "message": "Credit Card Payment System - FastAPI Backend"
    }


# =========================================================
# SIGNUP
# =========================================================

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


@app.post("/signup")
def signup(data: SignupRequest):

    if User.objects.filter(username=data.username).exists():
        return {
            "message": "Username already exists"
        }

    if User.objects.filter(email=data.email).exists():
        return {
            "message": "Email already exists"
        }

    user = User.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password
    )

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "username": user.username,
        "email": user.email
    }


# =========================================================
# SIGNIN
# =========================================================

class SigninRequest(BaseModel):
    username: str
    password: str


@app.post("/signin")
def signin(data: SigninRequest):

    user = authenticate(
        username=data.username,
        password=data.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    refresh = RefreshToken.for_user(user)

    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username,
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }


# =========================================================
# JWT AUTHENTICATION
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    try:
        token = AccessToken(credentials.credentials)

        user_id = token["user_id"]

        user = User.objects.get(id=user_id)

        return user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# =========================================================
# PROFILE
# =========================================================

@app.get("/profile/{user_id}")
def profile(
    user_id: int,
    current_user: User = Depends(get_current_user)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own profile"
        )

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }


# =========================================================
# EDIT PROFILE
# =========================================================

class EditProfileRequest(BaseModel):
    username: str
    email: str


@app.put("/edit-profile/{user_id}")
def edit_profile(
    user_id: int,
    data: EditProfileRequest,
    current_user: User = Depends(get_current_user)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own profile"
        )

    if User.objects.filter(
        username=data.username
    ).exclude(id=user_id).exists():

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    if User.objects.filter(
        email=data.email
    ).exclude(id=user_id).exists():

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    current_user.username = data.username
    current_user.email = data.email
    current_user.save()

    return {
        "message": "Profile updated successfully",
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }


# =========================================================
# CHANGE PASSWORD
# =========================================================

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@app.put("/change-password/{user_id}")
def change_password(
    user_id: int,
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only change your own password"
        )

    if not current_user.check_password(data.old_password):
        raise HTTPException(
            status_code=400,
            detail="Old password is incorrect"
        )

    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 8 characters"
        )

    current_user.set_password(data.new_password)
    current_user.save()

    return {
        "message": "Password changed successfully"
    }


# =========================================================
# DELETE ACCOUNT
# =========================================================

@app.delete("/delete-account/{user_id}")
def delete_account(
    user_id: int,
    current_user: User = Depends(get_current_user)
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own account"
        )

    current_user.delete()

    return {
        "message": "Account deleted successfully"
    }


# =========================================================
# CARD MANAGEMENT
# =========================================================

class AddCardRequest(BaseModel):
    card_type: str
    card_holder_name: str
    card_number: str
    expiry_month: int
    expiry_year: int


@app.post("/cards")
def add_card(
    data: AddCardRequest,
    current_user: User = Depends(get_current_user)
):

    if len(data.card_number) < 4:
        raise HTTPException(
            status_code=400,
            detail="Invalid card number"
        )

    last_four_digits = data.card_number[-4:]

    card = Card.objects.create(
        user=current_user,
        card_type=data.card_type,
        card_holder_name=data.card_holder_name,
        last_four_digits=last_four_digits,
        expiry_month=data.expiry_month,
        expiry_year=data.expiry_year
    )

    return {
        "message": "Card added successfully",
        "card": {
            "id": card.id,
            "card_type": card.card_type,
            "card_holder_name": card.card_holder_name,
            "masked_card_number": "************" + last_four_digits,
            "last_four_digits": last_four_digits,
            "expiry_month": card.expiry_month,
            "expiry_year": card.expiry_year,
            "created_at": card.created_at
        }
    }


@app.get("/cards")
def list_cards(
    current_user: User = Depends(get_current_user)
):

    cards = Card.objects.filter(
        user=current_user
    )

    result = []

    for card in cards:

        result.append({
            "id": card.id,
            "card_type": card.card_type,
            "card_holder_name": card.card_holder_name,
            "masked_card_number": "************" + card.last_four_digits,
            "last_four_digits": card.last_four_digits,
            "expiry_month": card.expiry_month,
            "expiry_year": card.expiry_year,
            "created_at": card.created_at
        })

    return result


@app.delete("/cards/{card_id}")
def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_user)
):

    try:

        card = Card.objects.get(
            id=card_id,
            user=current_user
        )

    except Card.DoesNotExist:

        raise HTTPException(
            status_code=404,
            detail="Card not found"
        )

    card.delete()

    return {
        "message": "Card deleted successfully"
    }


# =========================================================
# TRANSACTION / PAYMENT MANAGEMENT
# =========================================================

class CreateTransactionRequest(BaseModel):
    card_id: int
    amount: Decimal
    description: str = ""


# ---------------------------------------------------------
# CREATE TRANSACTION / PAYMENT
# ---------------------------------------------------------

@app.post("/transactions")
def create_transaction(
    data: CreateTransactionRequest,
    current_user: User = Depends(get_current_user)
):


    # Validate amount
    if data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than 0"
        )

    if data.amount > 1000000:
        raise HTTPException(
            status_code=400,
            detail="Amount cannot exceed 1000000"
        )

    # Make sure the card belongs to the logged-in user
    try:

        card = Card.objects.get(
            id=data.card_id,
            user=current_user
        )

    except Card.DoesNotExist:

        raise HTTPException(
            status_code=404,
            detail="Card not found"
        )
        # Check card expiry
    from datetime import date

    today = date.today()

    if card.expiry_year < today.year or (
        card.expiry_year == today.year
        and card.expiry_month < today.month
    ):
        raise HTTPException(
            status_code=400,
            detail="Card has expired"
        )

    # Generate unique transaction ID
    transaction_id = "TXN-" + uuid.uuid4().hex[:12].upper()

    # Create transaction
    transaction = Transaction.objects.create(
        user=current_user,
        card=card,
        amount=data.amount,
        status="PENDING",
        transaction_id=transaction_id,
        description=data.description
    )

    return {
        "message": "Payment successful",
        "transaction": {
            "id": transaction.id,
            "transaction_id": transaction.transaction_id,
            "card_id": card.id,
            "amount": str(transaction.amount),
            "status": transaction.status,
            "description": transaction.description,
            "created_at": transaction.created_at
        }
    }


# ---------------------------------------------------------
# LIST TRANSACTIONS
# ---------------------------------------------------------

@app.get("/transactions")
def list_transactions(
    current_user: User = Depends(get_current_user)
):

    transactions = Transaction.objects.filter(
        user=current_user
    ).order_by("-created_at")

    result = []

    for transaction in transactions:

        result.append({
            "id": transaction.id,
            "transaction_id": transaction.transaction_id,
            "card_id": transaction.card.id if transaction.card else None,
            "amount": str(transaction.amount),
            "status": transaction.status,
            "description": transaction.description,
            "created_at": transaction.created_at,
            "updated_at": transaction.updated_at
        })

    return result


# ---------------------------------------------------------
# GET SINGLE TRANSACTION
# ---------------------------------------------------------

@app.get("/transactions/{transaction_id}")
def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user)
):

    try:

        transaction = Transaction.objects.get(
            transaction_id=transaction_id,
            user=current_user
        )

    except Transaction.DoesNotExist:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return {
        "id": transaction.id,
        "transaction_id": transaction.transaction_id,
        "card_id": transaction.card.id if transaction.card else None,
        "amount": str(transaction.amount),
        "status": transaction.status,
        "description": transaction.description,
        "created_at": transaction.created_at,
        "updated_at": transaction.updated_at
    }
@app.post("/transactions/{transaction_id}/process")
def process_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        transaction = Transaction.objects.get(
            transaction_id=transaction_id,
            user=current_user
        )
    except Transaction.DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    if transaction.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Transaction is already {transaction.status}"
        )

    transaction.status = "SUCCESS"
    transaction.save()

    return {
        "message": "Payment processed successfully",
        "transaction_id": transaction.transaction_id,
        "status": transaction.status
    }