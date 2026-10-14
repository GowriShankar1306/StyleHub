# StyleHub — Fashion Mini Store Backend

## 1. Project Overview

StyleHub is a fashion e-commerce backend built with **FastAPI, SQLAlchemy, and SQLite**. It provides user authentication, product browsing, shopping cart management, order processing, and Stripe test-mode payment integration.

The project focuses on secure API development, payment processing, database operations, and validation of common e-commerce workflows.

## 2. Technology Stack

- **Backend:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Authentication:** JSON Web Tokens (JWT)
- **Password Security:** Password hashing
- **Payment Integration:** Stripe Test Mode
- **API Documentation:** Swagger UI and ReDoc
- **Configuration:** Environment variables using `python-dotenv`
- **Testing Tools:** Swagger UI, Postman, and Stripe CLI
- **Programming Language:** Python

## 3. Features

- User registration and login
- JWT-based authentication
- Secure password hashing
- Protected API endpoints
- Product listing and product details
- User-specific shopping carts
- Add, update, view, and remove cart items
- Cart quantity and product stock validation
- Order creation and order history
- Stripe PaymentIntent integration
- Payment success and failure webhook handling
- Stripe webhook signature verification
- Duplicate webhook event protection
- Product stock updates after successful payment
- Cart clearing after successful payment
- User-specific cart and order access
- Validation of empty-cart checkout attempts

## 4. Project Setup

### Prerequisites

Make sure the following are installed:

- Python
- Git
- Stripe CLI (for webhook testing)
- A Stripe account with test-mode API credentials

### Step 1: Clone the Repository

```bash
git clone https://github.com/GowriShankar1306/StyleHub.git
cd StyleHub
```

### Step 2: Create and Activate a Virtual Environment

Run these commands from the project root in Windows PowerShell:

```powershell
python -m venv stylehub_venv
& ".\stylehub_venv\Scripts\Activate.ps1"
```

If PowerShell blocks script execution, use an appropriate execution policy for your environment rather than changing system-wide security settings unnecessarily.

### Step 3: Install Dependencies

Navigate to the backend directory:

```powershell
cd backend
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file inside the `backend` directory using `.env.example` as a reference.

Configure the required values for:

- Database connection
- Application secret key
- JWT configuration
- Stripe test-mode secret key
- Stripe publishable key, if used
- Stripe webhook signing secret

Use your own valid values. Never commit your real `.env` file or expose secret keys in public repositories.

### Step 5: Start the FastAPI Server

Run the following command from the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

The API server should be available at:

`http://127.0.0.1:8000`

## 5. API Documentation

Once the server is running, access the API documentation using the following URLs:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### Main API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Log in and obtain an access token |
| GET | `/auth/me` | Retrieve the authenticated user's details |
| GET | `/products` | List available products |
| GET | `/products/{product_id}` | Retrieve product details |
| POST | `/cart/items` | Add a product to the cart |
| GET | `/cart/items` | View the user's cart |
| PUT | `/cart/items/{item_id}` | Update a cart item |
| DELETE | `/cart/items/{item_id}` | Remove a cart item |
| POST | `/orders/checkout` | Create an order and payment intent |
| GET | `/orders/my-orders` | View the authenticated user's orders |
| POST | `/orders/webhook` | Receive Stripe payment events |

**Note:** The login endpoint may accept the email address through the OAuth2 `username` field. Refer to Swagger UI for the exact request format and required fields.

## 6. Stripe Webhook Testing

Stripe webhooks are used to process payment events and update order statuses.

### Step 1: Start the FastAPI Server

Run the FastAPI server in the first terminal.

### Step 2: Start the Stripe CLI Listener

In a second terminal, run:

```powershell
stripe listen --events payment_intent.succeeded,payment_intent.payment_failed --forward-to http://127.0.0.1:8000/orders/webhook
```

### Step 3: Configure the Webhook Secret

Copy the webhook signing secret displayed by the Stripe CLI and configure it as `STRIPE_WEBHOOK_SECRET` in the backend `.env` file.

Restart the FastAPI server if necessary.

### Step 4: Test Payments

Use Stripe test-mode credentials and test payment methods to test successful and failed payment scenarios.

The webhook endpoint should verify the event signature and prevent duplicate events from being processed more than once.

**Important:** This project uses Stripe test mode. Do not use real payment credentials or real customer payment details for testing.

## 7. Security and Validation

The backend includes the following security and validation measures:

- JWT-based authentication for protected endpoints
- Password hashing instead of plain-text password storage
- User-specific cart and order queries
- Product stock and quantity validation
- Rejection of checkout attempts with an empty cart
- Stripe webhook signature verification
- Duplicate webhook event detection
- Separation of successful and failed payment handling
- Environment-based configuration for sensitive values

Never commit `.env` files, real API keys, passwords, database files containing personal data, or other sensitive information to source control.

## 8. Testing

Manual testing during development covered the following scenarios:

- User registration and login
- Access control for protected endpoints
- User cart and order isolation
- Adding and updating cart items
- Rejecting quantities greater than available stock
- Rejecting checkout with an empty cart
- Successful Stripe test payments
- Failed Stripe test payments
- Duplicate webhook event handling
- Product stock updates after successful payments
- Ensuring failed payments do not deduct stock or clear the cart

Run the relevant tests again after making code changes.

## 9. Database

The project uses SQLite with SQLAlchemy ORM for database operations.

The database contains tables for the application's core functionality, including:

- Users
- Products
- Cart items
- Orders
- Order items
- Webhook events

The database file is generated locally and should not be committed if it contains application or user data.

## 10. Frontend

The frontend is not included in this submission. StyleHub is a **backend-only project** that exposes REST APIs for integration with a future frontend.

The APIs can be explored and tested using Swagger UI, Postman, or another HTTP client.

## 11. Future Enhancements

Possible future improvements include:

- React-based frontend
- Product categories and advanced search
- Product image uploads
- Pagination and filtering
- Automated unit and integration tests
- Docker-based deployment
- Production deployment with managed database services
- Additional monitoring and logging
