# Authentication Microservice

A FastAPI-based authentication microservice providing JWT-based user authentication, registration, and user management. This service implements secure password hashing, token-based authentication, and follows clean architecture principles.

## Architecture Overview

The microservice is built using a layered architecture pattern with clear separation of concerns:

- **API Layer**: FastAPI endpoints handling HTTP requests/responses
- **Service Layer**: Business logic and orchestration
- **Repository Layer**: Data access abstraction
- **Model Layer**: SQLAlchemy ORM models and Pydantic schemas
- **Core Layer**: Configuration, database management, and security utilities

## Technology Stack

- **Framework**: FastAPI 0.116.1+
- **Database**: PostgreSQL with SQLAlchemy 2.0.41+ ORM
- **Authentication**: JWT tokens using python-jose with cryptography
- **Password Security**: bcrypt hashing via passlib
- **Validation**: Pydantic 2.11.7+ for data validation
- **Server**: Uvicorn ASGI server
- **Python**: 3.12+

## Project Structure

```
auth_service/
├── main.py                     # FastAPI application entry point
├── pyproject.toml             # Project dependencies and configuration
├── .env.example               # Environment variables template
└── src/
    ├── api/                   # API layer
    │   └── v1/
    │       ├── router.py      # Main API router (v1)
    │       └── routes/
    │           └── auth.py    # Authentication endpoints
    ├── core/                  # Core utilities and configuration
    │   ├── config.py         # Application configuration management
    │   ├── db.py             # Database connection management
    │   └── security.py       # Password hashing and JWT utilities
    ├── models/                # SQLAlchemy ORM models
    │   ├── base.py           # Base model with common fields
    │   └── user.py           # User model definition
    ├── repositories/          # Data access layer
    │   └── user.py           # User repository operations
    ├── schemas/               # Pydantic schemas
    │   ├── base.py           # Base schema configuration
    │   ├── user.py           # User-related schemas
    │   └── auth_token.py     # Token-related schemas
    └── services/              # Business logic layer
        ├── auth.py           # Authentication service
        └── user.py           # User management service
```

## Core Components

### Configuration Management (`core/config.py`)

Centralized configuration using Pydantic Settings with environment variable support:

- **PostgresConfig**: Database connection settings (host, port, user, password, database)
- **SecurityConfig**: JWT authentication settings (secret key, algorithm, token expiration)
- **Settings**: Aggregated configuration class combining all settings

Environment variables are loaded from `.env` file in the root directory.

### Database Management (`core/db.py`)

- **DBManager**: Handles SQLAlchemy engine and session lifecycle
- **Connection**: PostgreSQL with configurable connection pooling
- **Session Management**: Context-aware session handling for dependency injection

### Security (`core/security.py`)

- **Hasher**: bcrypt password hashing and verification utility
- **JWTHandler**: JWT token creation, validation, and decoding
- **Token Configuration**: Configurable expiration and signing algorithms

### Data Models

#### User Model (`models/user.py`)
```python
class User(Base):
    email: str (unique)
    password: str (hashed)
    # Inherited from Base:
    id: int (primary key)
    created_at: datetime (auto-generated)
```

#### Pydantic Schemas (`schemas/`)

- **UserCreate**: User registration input validation (email, password ≥8 chars)
- **UserRead**: Public user data for API responses (id, email, created_at)
- **UserInDB**: Internal user representation including hashed password
- **Token**: JWT token response format (access_token, token_type)
- **TokenData**: Decoded JWT claims (user_id)

### Repository Layer (`repositories/user.py`)

Data access abstraction with static methods:
- `get_user_by_id(db, id)`: Retrieve user by unique identifier
- `get_user_by_email(db, email)`: Retrieve user by email address
- `create_user(db, user_data)`: Create new user record

### Service Layer

#### UserService (`services/user.py`)
Business logic for user operations:
- `get_user_by_id(db, id)`: Retrieve user with validation and error handling
- `get_user_by_email(db, email)`: Retrieve user by email with validation
- `create_user(db, user)`: Create user with password hashing
- `get_current_user(db, id)`: Get authenticated user data

#### AuthService (`services/auth.py`)
Authentication orchestration:
- `authenticate(db, email, password)`: Verify user credentials
- `login(db, email, password)`: Authenticate and issue JWT token
- `get_current_user(db, token)`: Extract user from JWT token

## API Endpoints

Base URL: `/api/v1`

### Authentication Routes (`/auth`)

#### POST `/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Validation:**
- Email must be valid format
- Password minimum 8 characters
- Email must be unique

#### POST `/auth/login`
Authenticate user and receive JWT token.

**Request:** Form data (OAuth2PasswordRequestForm)
- `username`: User's email address
- `password`: User's password

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET `/auth/me`
Retrieve current authenticated user information.

**Authentication:** Bearer token required

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2024-01-01T12:00:00Z"
}
```

## Security Features

- **Password Security**: bcrypt hashing with configurable rounds
- **JWT Tokens**: Signed tokens with configurable expiration
- **Token Validation**: Automatic token verification for protected endpoints
- **Email Validation**: Pydantic EmailStr validation for proper email format
- **Environment-based Configuration**: Secure secret key management
- **Database Security**: Parameterized queries preventing SQL injection

## Environment Configuration

Create a `.env` file based on `.env.example`:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=your_postgres_password_here
DB_NAME=auth

# Security Configuration
SECRET_KEY=your_secret_key_here_generate_with_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Security Note**: Generate a secure secret key using:
```bash
openssl rand -hex 32
```

## Database Setup

The application automatically creates database tables on startup using SQLAlchemy's `Base.metadata.create_all()`.

### Required Database Tables

- **users**: User accounts with email and hashed passwords
  - `id` (integer, primary key, auto-increment)
  - `email` (string, unique)
  - `password` (string, hashed)
  - `created_at` (timestamp with timezone)

## Running the Service

### Development Mode
```bash
cd auth_service
python main.py
```

The service starts on `http://localhost:8000` with auto-reload enabled.

### Production Deployment
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Dependencies

Core dependencies as defined in `pyproject.toml`:

- `fastapi>=0.116.1`: Modern web framework
- `sqlalchemy>=2.0.41`: ORM and database toolkit
- `psycopg2-binary>=2.9.10`: PostgreSQL adapter
- `pydantic>=2.11.7`: Data validation library
- `pydantic-settings>=2.10.1`: Environment-based configuration
- `passlib>=1.7.4`: Password hashing utilities
- `bcrypt==3.1.7`: bcrypt hashing algorithm
- `python-jose[cryptography]>=3.5.0`: JWT implementation
- `python-multipart>=0.0.20`: Form data parsing
- `email-validator>=2.2.0`: Email validation
- `uvicorn>=0.35.0`: ASGI server

## Error Handling

The service implements comprehensive error handling:

- **HTTP 404**: User not found (by ID or email)
- **HTTP 401**: Invalid credentials or expired/invalid tokens
- **HTTP 422**: Validation errors (invalid email format, password too short)
- **HTTP 500**: Internal server errors

## Authentication Flow

1. **Registration**: User submits email/password → Password hashed → User stored in database
2. **Login**: User submits credentials → Credentials verified → JWT token issued
3. **Protected Requests**: Client includes Bearer token → Token validated → User identified → Request processed

## Token Management

- **Token Type**: Bearer tokens using JWT
- **Expiration**: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Claims**: User ID stored in `sub` claim
- **Algorithm**: Configurable signing algorithm (default: HS256)
- **Validation**: Automatic signature and expiration verification

## Database Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Development Notes

- All password storage uses secure bcrypt hashing
- JWT tokens are stateless and contain user identification
- Database sessions are automatically managed with proper cleanup
- All user inputs are validated using Pydantic schemas
- The service follows RESTful API conventions
- Environment variables provide secure configuration management
- The codebase includes comprehensive docstrings for all components