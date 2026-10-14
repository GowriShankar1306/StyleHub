# StyleHub — Fashion Mini Store Backend

## 1. Project Overview

StyleHub is a fashion e-commerce backend built with FastAPI, SQLAlchemy, and SQLite. It provides user authentication, product browsing, shopping cart management, order processing, and Stripe test-mode payment integration.

## 2. Technology Stack

- **Backend:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Authentication:** JWT
- **Password Security:** Password hashing
- **Payment Integration:** Stripe Test Mode
- **API Documentation:** Swagger UI
- **Configuration:** Environment variables using `python-dotenv`

## 3. Features

- User registration and login
- JWT-protected endpoints
- Secure password hashing
- Product listing and product details
- User-specific shopping carts
- Cart quantity and stock validation
- Order creation and order history
- Stripe PaymentIntent integration
- Payment success and failure webhook handling
- Duplicate webhook event protection
- Stock updates after successful payment
- Cart clearing after successful payment

## 4. Project Setup

### Prerequisites

- Python installed
- Stripe CLI installed for webhook testing
- A Stripe test-mode account

### Create and activate a virtual environment

Run these commands from the project root:

```powershell
python -m venv stylehub_venv
& ".\stylehub_venv\Scripts\Activate.ps1"
```

### Install dependencies

Navigate to the backend directory:

```powershell
cd backend
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the `backend` directory using `.env.example` as a reference.

Set your own secret key, database URL, Stripe test API keys, and webhook signing secret. Never commit the real `.env` file.

### Start the server

From the `backend` directory, run:

```powershell
python -m uvicorn app.main:app --reload
```

## 5. API Documentation

When the server is running, open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Main API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Log in and obtain a token |
| GET | `/auth/me` | Retrieve the authenticated user |
| GET | `/products` | List products |
| GET | `/products/{product_id}` | Retrieve product details |
| POST | `/cart/items` | Add a product to the cart |
| GET | `/cart/items` | View the user's cart |
| PUT | `/cart/items/{item_id}` | Update a cart item |
| DELETE | `/cart/items/{item_id}` | Remove a cart item |
| POST | `/orders/checkout` | Create an order and payment intent |
| GET | `/orders/my-orders` | View the authenticated user's orders |
| POST | `/orders/webhook` | Receive Stripe payment events |

## 6. Stripe Webhook Testing

Start the FastAPI server in one terminal. In another terminal, run:

```powershell
stripe listen --events payment_intent.succeeded,payment_intent.payment_failed --forward-to http://127.0.0.1:8000/orders/webhook
```

Configure `STRIPE_WEBHOOK_SECRET` with the signing secret provided by the Stripe CLI listener.

Use Stripe test-mode credentials and test payment methods only. Do not use real payment credentials for testing.

## 7. Security and Validation

The backend includes JWT authentication, password hashing, user-specific cart and order queries, product stock validation, Stripe webhook signature verification, and duplicate event detection.

Never commit `.env`, real API keys, passwords, database files containing personal data, or other secrets to source control.

## 8. Testing

Manual tests performed during development include:

- Rejecting unauthenticated access to protected endpoints
- Preventing duplicate webhook processing
- Handling declined test payments
- Checking user cart and order isolation
- Rejecting checkout with an empty cart
- Rejecting cart quantities exceeding available stock
- Checking that failed payments do not deduct stock or clear the cart

Re-run the relevant tests after code changes.

## 9. Frontend

The frontend is not included in this backend-only submission. The API can be tested through Swagger UI or an HTTP client.

## 10. Status

Backend implementation and manual security testing are done. Complete the final regression checks before treating the project as ready for submission.
