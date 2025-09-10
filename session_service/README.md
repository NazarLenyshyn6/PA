# Session Management Microservice

A FastAPI-based session management microservice providing user session lifecycle operations with Redis caching and PostgreSQL persistence. This service enables users to create, manage, and switch between multiple named sessions with automatic activation management and cache optimization.

## Architecture Overview

The microservice implements a layered architecture pattern with clear separation of concerns:

- **API Layer**: FastAPI endpoints handling HTTP requests/responses
- **Service Layer**: Business logic and session orchestration
- **Repository Layer**: Database access abstraction
- **Cache Layer**: Redis-based active session caching
- **Model Layer**: SQLAlchemy ORM models and Pydantic schemas
- **Core Layer**: Configuration, database management, security utilities, and custom exceptions

## Technology Stack

- **Framework**: FastAPI 0.116.1+
- **Database**: PostgreSQL with SQLAlchemy 2.0.41+ ORM
- **Cache**: Redis 6.2.0+ for active session management
- **Authentication**: JWT token validation using python-jose
- **Validation**: Pydantic 2.11.7+ for data validation
- **Server**: Uvicorn ASGI server
- **Python**: 3.12+

## Project Structure

```
session_service/
├── main.py                       # FastAPI application entry point
├── pyproject.toml               # Project dependencies and configuration
└── src/
    ├── api/                     # API layer
    │   └── v1/
    │       ├── router.py        # Main API router (v1)
    │       └── routes/
    │           └── session.py   # Session management endpoints
    ├── cache/                   # Redis caching layer
    │   └── session.py          # Redis session cache manager
    ├── core/                    # Core utilities and configuration
    │   ├── config.py           # Application configuration management
    │   ├── db.py               # Database connection management
    │   ├── exceptions.py       # Custom session-related exceptions
    │   └── security.py         # JWT token validation utilities
    ├── models/                  # SQLAlchemy ORM models
    │   ├── base.py             # Base model with timestamp fields
    │   └── session.py          # Session model definition
    ├── repositories/            # Data access layer
    │   └── session.py          # Session repository operations
    ├── schemas/                 # Pydantic schemas
    │   ├── base.py             # Base schema configuration
    │   └── session.py          # Session-related schemas
    └── services/                # Business logic layer
        └── session.py          # Session management service
```

## Core Components

### Configuration Management (`core/config.py`)

Centralized configuration using Pydantic Settings with environment variable support:

- **PostgresConfig**: Database connection settings (host, port, user, password, database)
- **SecurityConfig**: JWT authentication settings (secret key, algorithm, token expiration)
- **RedisConfig**: Redis connection settings (host, port, database index)
- **Settings**: Aggregated configuration class combining all settings

Environment variables are loaded from `.env` file in the root directory.

### Database Management (`core/db.py`)

- **DBManager**: Handles SQLAlchemy engine and session lifecycle
- **Connection**: PostgreSQL with configurable connection pooling
- **Session Management**: Context-aware session handling for dependency injection

### Security (`core/security.py`)

- **JWTHandler**: JWT token validation and user ID extraction
- **HTTPBearer**: FastAPI security scheme for token extraction
- **get_current_user_id**: Dependency function for authenticated route protection

### Cache Management (`cache/session.py`)

- **SessionCacheManager**: Redis-based caching for active session IDs
- **Connection Management**: Automatic Redis client lifecycle handling
- **TTL Support**: Configurable time-to-live for cached sessions (default: 3600 seconds)
- **Error Handling**: Graceful handling of Redis connection issues

### Custom Exceptions (`core/exceptions.py`)

Specialized exceptions for precise error handling:
- **SessionNotFoundError**: Session not found in database
- **ActiveSessionNotFoundError**: No active session exists for user
- **ActiveSessionDeletionError**: Attempted deletion of active session
- **DuplicateSessionTitleError**: Session title already exists for user

### Data Models

#### Session Model (`models/session.py`)
```python
class Session(Base):
    id: UUID (primary key, auto-generated)
    user_id: int (foreign key reference)
    title: str (session name)
    active: bool (activation status, default: False)
    # Inherited from Base:
    created_at: datetime (auto-generated)
    updated_at: datetime (auto-updated)
```

#### Pydantic Schemas (`schemas/session.py`)

- **SessionCreate**: Internal session creation with user_id, title, and active flag
- **SessionRead**: Public session data for API responses (id, user_id, title, active)
- **NewSession**: Minimal session creation input requiring only title

### Repository Layer (`repositories/session.py`)

Data access abstraction with comprehensive session operations:
- `create_session(db, session_data)`: Create session with duplicate title validation
- `get_sessions(db, user_id)`: Retrieve all user sessions
- `get_session_by_title(db, user_id, title)`: Find session by title
- `get_active_session(db, user_id)`: Get currently active session
- `deactivate_active_session(db, user_id)`: Deactivate current active session
- `set_active_session(db, user_id, title)`: Activate session by title
- `delete_session(db, user_id, title)`: Delete session with business rule enforcement

### Service Layer (`services/session.py`)

Business logic orchestration with integrated caching:
- `create_session(db, session_data)`: Create and auto-activate new session
- `get_sessions(db, user_id)`: Retrieve all user sessions
- `get_active_session_id(db, user_id)`: Get active session ID (cache-first with DB fallback)
- `set_active_session(db, user_id, title)`: Switch active session with cache update
- `delete_session(db, user_id, title)`: Delete session with validation

## API Endpoints

Base URL: `/api/v1`

### Session Routes (`/sessions`)

#### GET `/sessions/`
Retrieve all sessions for the authenticated user.

**Authentication:** Bearer token required

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": 1,
    "title": "Data Analysis Project",
    "active": true
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": 1,
    "title": "Machine Learning Model",
    "active": false
  }
]
```

#### GET `/sessions/active`
Retrieve the ID of the currently active session.

**Authentication:** Bearer token required

**Response:**
```json
"550e8400-e29b-41d4-a716-446655440000"
```

**Error Responses:**
- **404**: No active session found for user

#### POST `/sessions/`
Create a new session and automatically set it as active.

**Authentication:** Bearer token required

**Request Body:**
```json
{
  "title": "New Analysis Session"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": 1,
  "title": "New Analysis Session",
  "active": true
}
```

**Error Responses:**
- **409**: Session with same title already exists

#### POST `/sessions/active/{title}`
Set a specific session as active by title.

**Authentication:** Bearer token required

**Path Parameters:**
- `title`: Title of the session to activate

**Response:**
```json
{
  "detail": "'Data Analysis Project' set as active session for user_id=1"
}
```

**Error Responses:**
- **404**: Session with specified title not found

#### DELETE `/sessions/{title}`
Delete a session by title (only if not active).

**Authentication:** Bearer token required

**Path Parameters:**
- `title`: Title of the session to delete

**Response:**
```json
{
  "detail": "Session deleted successfully"
}
```

**Error Responses:**
- **404**: Session not found
- **400**: Cannot delete active session

## Session Management Features

### Active Session Management
- **Single Active Session**: Only one session per user can be active at any time
- **Automatic Deactivation**: Setting a new active session automatically deactivates the previous one
- **Cache Optimization**: Active session IDs cached in Redis for fast retrieval
- **Fallback Strategy**: Database fallback when cache misses occur

### Session Lifecycle
- **Creation**: New sessions automatically become active
- **Title Uniqueness**: Session titles must be unique per user
- **Activation Switching**: Users can switch between existing sessions
- **Deletion Protection**: Active sessions cannot be deleted (must be deactivated first)

### Caching Strategy
- **Cache-First**: Active session lookups prioritize Redis cache
- **TTL Management**: Cached sessions expire after 3600 seconds (configurable)
- **Cache Invalidation**: Automatic cache updates on session state changes
- **Error Resilience**: Graceful fallback to database on Redis failures

## Environment Configuration

Create a `.env` file with the following variables:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=your_postgres_password_here
DB_NAME=session_db

# Security Configuration (shared with auth service)
SECRET_KEY=your_secret_key_here_generate_with_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Redis Configuration
HOST=localhost
PORT=6379
DB=0
```

**Security Note**: Generate a secure secret key using:
```bash
openssl rand -hex 32
```

## Database Setup

The application automatically creates database tables on startup using SQLAlchemy's `Base.metadata.create_all()`.

### Required Database Tables

- **sessions**: User session records
  - `id` (UUID, primary key, auto-generated via PostgreSQL `gen_random_uuid()`)
  - `user_id` (integer, foreign key reference to users)
  - `title` (string, session name)
  - `active` (boolean, activation status, default: false)
  - `created_at` (timestamp with timezone, auto-generated)
  - `updated_at` (timestamp with timezone, auto-updated)

### Database Schema

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    title VARCHAR NOT NULL,
    active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_active ON sessions(user_id, active) WHERE active = TRUE;
```

## Redis Setup

The service requires Redis for caching active session IDs:

### Redis Key Structure
- **Pattern**: `session:active:user:{user_id}`
- **Value**: Active session UUID
- **TTL**: 3600 seconds (1 hour)

### Redis Configuration
- **Connection Timeout**: 5 seconds
- **Socket Keepalive**: Enabled for persistent connections
- **Decode Responses**: Enabled for string handling

## Running the Service

### Development Mode
```bash
cd session_service
python main.py
```

The service starts on `http://localhost:8001` with auto-reload enabled.

### Production Deployment
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Application Lifespan
The service includes proper startup/shutdown handling:
- **Startup**: Redis client connection initialization
- **Shutdown**: Graceful Redis client disconnection

## Dependencies

Core dependencies as defined in `pyproject.toml`:

- `fastapi>=0.116.1`: Modern web framework
- `sqlalchemy>=2.0.41`: ORM and database toolkit
- `psycopg2-binary>=2.9.10`: PostgreSQL adapter
- `pydantic>=2.11.7`: Data validation library
- `pydantic-settings>=2.10.1`: Environment-based configuration
- `python-jose>=3.5.0`: JWT implementation (validation only)
- `python-multipart>=0.0.20`: Form data parsing
- `redis>=6.2.0`: Redis client library
- `uvicorn>=0.35.0`: ASGI server

## Error Handling

The service implements comprehensive error handling:

- **HTTP 400**: Bad request (cannot delete active session)
- **HTTP 404**: Resource not found (session or active session not found)
- **HTTP 409**: Conflict (duplicate session title)
- **HTTP 401**: Unauthorized (invalid JWT token)
- **HTTP 422**: Validation errors (invalid request data)
- **HTTP 500**: Internal server errors

## Business Rules

### Session Creation
- Session titles must be unique per user
- New sessions automatically become active
- Previous active session is deactivated

### Session Activation
- Only one session per user can be active
- Switching sessions updates both database and cache
- Non-existent sessions cannot be activated

### Session Deletion
- Active sessions cannot be deleted
- Users must deactivate session before deletion
- Deleted sessions are removed from database permanently

### Cache Management
- Active session IDs cached for performance
- Cache TTL automatically refreshed on access
- Database serves as authoritative source

## Integration Points

### Authentication Service Integration
- Validates JWT tokens from auth service
- Extracts user ID from token claims
- Shares security configuration (SECRET_KEY, ALGORITHM)

### Token Requirements
- All endpoints require valid Bearer token
- Token must contain valid `sub` claim with user ID
- Token validation uses shared secret key

## Performance Considerations

### Caching Strategy
- **Cache Hit**: Active session lookup ~1ms (Redis)
- **Cache Miss**: Fallback to database ~10-50ms
- **Cache Refresh**: Automatic TTL extension on access

### Database Optimization
- Indexed queries on `user_id` and `active` fields
- Minimal database round trips per operation
- Proper connection pooling via SQLAlchemy

### Redis Optimization
- Connection keepalive for persistent connections
- Automatic connection timeout handling
- Graceful error handling for Redis failures

## Development Notes

- All session operations are atomic with proper transaction handling
- UUID primary keys provide global uniqueness across distributed systems
- Redis cache failures don't affect core functionality (graceful degradation)
- The service follows RESTful API conventions
- Comprehensive docstrings document all components
- Environment variables provide secure configuration management
- Custom exceptions enable precise error reporting and handling