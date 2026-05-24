# User Management API

A RESTful API for managing users, built with FastAPI and PostgreSQL. Deployed on Google Cloud Run with a fully automated CI/CD pipeline via Google Cloud Build.

## Live API

| | URL |
|---|---|
| **API** | https://user-management-api-951962814924.southamerica-east1.run.app |
| **Swagger UI** | https://user-management-api-951962814924.southamerica-east1.run.app/docs |
| **Health Check** | https://user-management-api-951962814924.southamerica-east1.run.app/health |

---

## Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.12
- **ORM:** SQLAlchemy 2.x
- **Validation:** Pydantic v2
- **Database:** PostgreSQL 16 (Cloud SQL) / SQLite (tests)
- **Migrations:** Alembic
- **Testing:** pytest + httpx
- **Server:** Uvicorn
- **Containerization:** Docker
- **CI/CD:** Google Cloud Build
- **Hosting:** Google Cloud Run

---

## Architecture

```
app/
├── api/v1/users.py          # Route handlers (controllers)
├── core/
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # SQLAlchemy engine + session
│   └── logging.py           # Logging configuration
├── models/user.py           # SQLAlchemy ORM model
├── repositories/
│   └── user_repository.py   # Database access layer
├── schemas/user.py          # Pydantic schemas (request/response)
├── services/
│   └── user_service.py      # Business logic layer
└── main.py                  # FastAPI app entry point
```

The project follows a **Layered Architecture**:

```
HTTP Request → API Layer → Service Layer → Repository Layer → Database
```

---

## Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| `GET` | `/health` | Health check | 200 |
| `POST` | `/api/v1/users/` | Create a user | 201 |
| `GET` | `/api/v1/users/` | List users (paginated) | 200 |
| `GET` | `/api/v1/users/{id}` | Get user by ID | 200 |
| `PUT` | `/api/v1/users/{id}` | Update user | 200 |
| `DELETE` | `/api/v1/users/{id}` | Delete user | 204 |

### Pagination

```
GET /api/v1/users/?skip=0&limit=10
```

Response:
```json
{
  "total": 25,
  "users": [...]
}
```

---

## Running Locally

### Prerequisites

- Python 3.12+
- PostgreSQL (or use SQLite for development)

### Setup

```bash
# Clone the repository
git clone https://github.com/adrianmfm/se-challenge.git
cd se-challenge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your DATABASE_URL
```

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dbname
APP_ENV=development
LOG_LEVEL=INFO
```

> If no `.env` is provided, the app defaults to SQLite (`sqlite:///./test.db`).

### Run Migrations

```bash
alembic upgrade head
```

### Start the Server

```bash
uvicorn app.main:app --reload --port 8080
```

The API will be available at `http://localhost:8080`.

---

## Running with Docker

```bash
# Build the image
docker build -t user-management-api .

# Run the container
docker run -p 8080:8080 \
  -e DATABASE_URL="postgresql+psycopg2://user:password@host/dbname" \
  user-management-api
```

---

## Testing

Tests use **SQLite in-memory** — no PostgreSQL required.

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --tb=short
```

The test suite includes **29 tests** covering:

- User creation (success + validation errors)
- Duplicate username/email detection (409)
- Invalid input handling (422)
- Pagination
- Update (partial updates, conflict detection)
- Delete and subsequent 404
- Health check

---

## CI/CD Pipeline

Every push to `main` triggers the following pipeline in Google Cloud Build:

```
1. Build Docker image
      ↓
2. Run pytest inside the container (SQLite, no DB needed)
      ↓ (stops here if tests fail)
3. Push image to Artifact Registry
      ↓
4. Deploy to Cloud Run
      ↓
5. Container starts → Alembic migrations run → Uvicorn starts
```

### Pipeline config: `cloudbuild.yaml`

The deploy step:
- Reads `DATABASE_URL` from **Secret Manager**
- Connects to **Cloud SQL** via Unix socket (Cloud SQL Proxy)
- Runs on **Cloud Run** in `southamerica-east1`

---

## API Usage Examples

### Create a user

```bash
curl -X POST https://user-management-api-951962814924.southamerica-east1.run.app/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user"
  }'
```

### List users

```bash
curl "https://user-management-api-951962814924.southamerica-east1.run.app/api/v1/users/?skip=0&limit=10"
```

### Update a user

```bash
curl -X PUT https://user-management-api-951962814924.southamerica-east1.run.app/api/v1/users/{id} \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John Updated", "role": "admin"}'
```

### Delete a user

```bash
curl -X DELETE https://user-management-api-951962814924.southamerica-east1.run.app/api/v1/users/{id}
```

---

## User Schema

### Request (Create)

```json
{
  "username": "johndoe",       // 3-50 chars, alphanumeric + underscores, auto-lowercased
  "email": "john@example.com", // valid email, unique
  "first_name": "John",        // 1-100 chars
  "last_name": "Doe",          // 1-100 chars
  "role": "user",              // "admin" | "user" | "guest" (default: "user")
  "active": true               // default: true
}
```

### Response

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "active": true,
  "created_at": "2026-05-23T22:00:00Z",
  "updated_at": "2026-05-23T22:00:00Z"
}
```

---

## Error Responses

| Status | Meaning |
|--------|---------|
| `404 Not Found` | User does not exist |
| `409 Conflict` | Username or email already taken |
| `422 Unprocessable Entity` | Validation error (invalid email, field too short, etc.) |
| `500 Internal Server Error` | Unexpected server error |

```json
{
  "detail": "User not found"
}
```
