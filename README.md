# Travel Planner

REST API for travel projects and Art Institute of Chicago artworks as places (notes, visited, project completion).

## Requirements

- Python **3.11+** (Docker image uses 3.11)
- pip / virtualenv

## Setup (local)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Optional: copy `.env.example` values into `.env` (see Environment variables). If `REDIS_URL` is unset, the app uses in-memory cache.

Apply migrations, create a **Django user** for API access (HTTP Basic Auth), and run:

```bash
python manage.py migrate
python manage.py createsuperuser   # or any user with a password you choose
python manage.py runserver 127.0.0.1:8000
```

### Authentication

All **`/api/v1/`** endpoints require **HTTP Basic Authentication** (username + password of a Django `User`).

- **`/api/schema/`** and **`/api/docs/`** stay **public** (no login).
- Use `-u user:password` with **curl**, or **Postman** collection auth (variables `api_username`, `api_password`).
- Programmatic tests use `APIClient.force_authenticate`; interactive tools send the `Authorization: Basic …` header.

Run tests:

```bash
python manage.py test
```

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Dev insecure key (set in production) |
| `DEBUG` | `1`/`true` or `0`/`false` | `true` |
| `ALLOWED_HOSTS` | Comma-separated hostnames | `127.0.0.1,localhost,testserver` |
| `SQLITE_PATH` | SQLite database file path | `<project>/db.sqlite3` |
| `REDIS_URL` | If set (e.g. `redis://localhost:6379/0`), Redis cache is used | unset → LocMem cache |

## API docs (Swagger UI)

After the server is running:

**http://127.0.0.1:8000/api/docs/**

OpenAPI schema: **http://127.0.0.1:8000/api/schema/**

## Docker

Build and run with Compose (web + SQLite volume + Redis for caching):

```bash
docker compose build
docker compose up
```

- API: **http://localhost:8000**
- SQLite file is stored in the `sqlite_data` Docker volume (`SQLITE_PATH=/data/db.sqlite3` inside the container).
- Create a user once (needed for Basic auth on `/api/v1/`):

  `docker compose exec web python manage.py createsuperuser`

Single-container image (same entrypoint: migrate + gunicorn):

```bash
docker build -t travel-planner .
docker run --rm -p 8000:8000 \
  -e SQLITE_PATH=/data/db.sqlite3 \
  -v travel_sqlite:/data \
  travel-planner
```

Override `SECRET_KEY` and set `DEBUG=0` for anything beyond local experiments.

## Example curl requests

Replace IDs after you create resources.

```bash
BASE=http://127.0.0.1:8000
USER=apiuser          # your Django username
PASS='your-password'

# List projects (optional: ?status=active|completed)
curl -sS -u "$USER:$PASS" "$BASE/api/v1/travel/"

# Create project (optional Art Institute artwork ids)
curl -sS -u "$USER:$PASS" -X POST "$BASE/api/v1/travel/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Weekend","description":"","start_date":null,"place_ids":["4"]}'

# Retrieve project (use returned id)
curl -sS -u "$USER:$PASS" "$BASE/api/v1/travel/1/"

# List places (optional: ?visited=true|false)
curl -sS -u "$USER:$PASS" "$BASE/api/v1/travel/1/places/"

# Add place by artwork id (validated against Art Institute API)
curl -sS -u "$USER:$PASS" -X POST "$BASE/api/v1/travel/1/places/" \
  -H "Content-Type: application/json" \
  -d '{"external_id":"5","notes":"","visited":false}'

# Patch place (notes, visited)
curl -sS -u "$USER:$PASS" -X PATCH "$BASE/api/v1/travel/1/places/1/" \
  -H "Content-Type: application/json" \
  -d '{"visited":true,"notes":"Seen"}'

# Delete project (400 if any place is visited)
curl -sS -u "$USER:$PASS" -X DELETE "$BASE/api/v1/travel/1/"
```

## Postman

Import:

- **Collection:** `postman/TravelPlanner.postman_collection.json`
- **Environment:** `postman/TravelPlanner.local.postman_environment.json`

Collection variables: `base_url`, **`api_username`**, **`api_password`** (HTTP Basic), `project_id`, `place_id`.  
Select the environment, fill credentials to match your Django user, then run requests (nested folders inherit Basic auth; Schema/docs use No Auth).

## Third-party API

Art Institute of Chicago: [API docs](https://api.artic.edu/docs/)
