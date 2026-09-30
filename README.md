# Credit Card Payment System

A backend application for managing users, credit cards, payments, and transactions.

## Tech Stack

- Django
- Django REST Framework
- FastAPI
- MySQL
- JWT Authentication
- Docker
- Postman

## Features

### User Authentication
- User Registration
- User Login
- JWT Authentication
- Protected APIs
- Password Hashing

### Card Management
- Add Credit Card
- View Credit Cards
- Delete Credit Card
- Card Number Masking
- No CVV Storage

### Payment Processing
- Create Payment
- Process Payment
- Payment Status
- Transaction ID Generation

### Transaction Management
- Create Transactions
- Process Transactions
- Transaction Status
- Transaction History

### Admin Panel
- Manage Users
- Manage Cards
- Manage Transactions

## Security

- JWT Authentication
- Password Hashing
- Protected APIs
- Card Number Masking
- CVV is not stored
- No plain-text passwords

## Project Structure

```text
credit_card_payment_system/
│
├── cards/
├── config/
├── fastapi_backend/
├── transactions/
├── users/
├── manage.py
├── credit_card_db.sql
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── Credit Card Payment System.postman_collection.json