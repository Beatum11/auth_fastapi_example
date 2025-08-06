
## A lightweight and flexible authentication and authorization service built with FastAPI. This project provides a solid foundation for managing users, including local email/password registration and OAuth2 flow (Google).
-----

## 🚧 Project Status: Work in Progress

This project is currently under **development**. It is intended as a foundational boilerplate for authentication services but is **not yet considered production-ready**. APIs and features are subject to change.

-----

## ✨ Key Features

  * **Native Authentication**: User registration and login with email and password.
  * **JWT-based Authorization**: Secure resource access using Access and Refresh tokens.
  * **OAuth2 Integration**: Pre-built logic for social logins via external providers (e.g., Google).
  * **Secure Password Storage**: Password hashing using modern standards (`passlib`).
  * **Background Tasks**: Post-registration actions like sending verification emails without delaying the API response.
  * **Token Blocklisting**: A proper logout mechanism that blocklists tokens using Redis.
-----

## 🛠️ Tech Stack

  * **Framework**: FastAPI
  * **Database**: PostgreSQL (async with `SQLAlchemy 2.0` & `asyncpg`)
  * **Authentication**: `python-jose` for JWTs, `passlib` for password hashing
  * **Configuration**: `pydantic-settings`
  * **Caching/Blocklisting**: Redis
  * **Logging**: Loguru
  * **Async HTTP Client**: `httpx`

-----

## 🚀 Getting Started

Follow these steps to get the project running locally.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Beatum11/auth_fastapi_example
    cd auth_fastapi_example
    ```

2.  **Install dependencies:**
    Poetry will automatically create a virtual environment and install all the required packages.
    
    ```bash
    poetry install
    ```
    
4.  **Set up environment variables:**
    Create a `.env` file in the root directory by copying the `.env.example` template. Fill in the required values.

    **Example `.env.example`:**

    ```ini
    # Database
    DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

    # Redis
    REDIS_URL=redis://localhost:6379

    # JWT
    JWT_SECRET=your_super_secret_key
    JWT_ALGO=HS256

    # Google OAuth2
    GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    GOOGLE_CALLBACK_REDIRECT_URI=http://localhost:8000/auth/google/callback

    # Mail
    MAIL_USERNAME=user@example.com
    MAIL_PASSWORD=your_email_password
    MAIL_FROM=user@example.com
    MAIL_PORT=587
    MAIL_SERVER=smtp.example.com
    MAIL_STARTTLS=True
    MAIL_SSL_TLS=False
    ```
-----
