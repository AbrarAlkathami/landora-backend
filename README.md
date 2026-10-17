# Sarj Real Estate — Backend

FastAPI service for Sarj's Riyadh land discovery and leadership intelligence product. PostgreSQL stores the portfolio and investor pipeline; real LLM endpoints answer investor and admin questions using current records.

## Features

- Parcel and inquiry CRUD, search, filters, and pagination.
- Structured investor inquiries: separate purpose, readiness, preferences, budget basis, and optional parcel reference.
- Validation of new land records, duplicate IDs, and selected parcel references.
- Investor AI discovery and comparisons grounded in current parcel facts.
- Admin AI analysis grounded in a complete SQL snapshot and computed business metrics.
- Optional Qdrant semantic retrieval for investor discovery.
- Dashboard statistics and a documented OpenAPI interface.

The public assessment demo has no authentication or permissions layer.

## Stack

Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL with psycopg, Alembic, OpenAI, and Qdrant. Python **3.12** is the tested local runtime; use `uv` to install and run the project.

The current model is `gpt-5-mini`; embeddings use `text-embedding-3-small`.

## Local setup

Run commands from this repository's root. Prepare a PostgreSQL database and a reachable Qdrant service first.

```bash
uv sync
cp .env.example .env.local
```

If `.env.local` already exists, edit it rather than replacing it. Configure:

```env
APP_NAME=Landora API
ENVIRONMENT=local
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
```

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy PostgreSQL connection URL, using the psycopg driver. |
| `OPENAI_API_KEY` | Model and embedding access. Configure before starting the API because model clients are imported at startup. |
| `QDRANT_URL` | Local or hosted Qdrant URL; required by the settings model. |
| `QDRANT_API_KEY` | Optional for local Qdrant; use the hosted service key when required. |
| `ENVIRONMENT` | Process setting used to select `.env.local` or `.env.production`. |
| `APP_NAME` | Application setting, defaulting to `Landora API`. |

Environment files and credentials are ignored by Git. Frontend environment variables contain API URLs, not database or model credentials.

## Migrations and provided data

```bash
uv run alembic upgrade head
PYTHONPATH=src uv run python src/landora_backend/scripts/seed_parcels.py
PYTHONPATH=src uv run python src/landora_backend/scripts/seed_inquiries.py
```

Seed scripts skip existing IDs. They populate missing records; they do not reset modified records to their original values.

The supplied snapshot is dated **11 August 2026**:

| Data | Count |
| --- | ---: |
| Land parcels | 120 |
| Riyadh districts | 88 |
| Available parcels | 62 |
| Sold / leased / reserved | 29 / 13 / 16 |
| Existing investor inquiries | 48 |

Source files are `data/sarj-lands-riyadh.json` and `data/investor-inquiries.json`. Keep all original parcel and inquiry IDs accounted for in the assessment demo. Null prices remain null, and days on market are the reported snapshot values.

Migration `ea8f2d41b607` adds the nullable `selected_parcel_id` foreign key. Apply it before using inquiry creation/editing with parcel references. Deleting a referenced parcel clears that reference rather than deleting the inquiry.

## Semantic retrieval setup

After seeding, create collections and index the records:

```bash
PYTHONPATH=src uv run python src/landora_backend/vector/qdrant_collections.py
PYTHONPATH=src uv run python src/landora_backend/vector/index_data.py
```

Collections: `landora_parcels` and `landora_inquiries`. Indexing calls the embedding provider and requires configured credentials.

Investor semantic discovery requires this setup. Exact selected-parcel comparisons and the current admin AI path use SQL records directly. CRUD writes do not automatically update the vector index.

## Start the API

```bash
uv run uvicorn landora_backend.main:app --reload --app-dir src --port 8000
```

- API base: `http://localhost:8000/api/v1`
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

Configure the frontend's `API_URL` as `http://localhost:8000/api/v1`. Its active investor and admin views use same-origin Next.js proxies. The backend's direct-browser CORS allowlist currently contains `http://localhost:3000`.

## API overview

All paths below are relative to `/api/v1`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET / POST | `/parcels/` | Paginated portfolio / create a parcel |
| GET / PATCH / DELETE | `/parcels/{parcel_id}` | Read, edit or delete a parcel |
| GET / POST | `/inquiries/` | Paginated pipeline / create an inquiry |
| GET / PATCH / DELETE | `/inquiries/{inquiry_id}` | Read, edit or delete an inquiry |
| POST | `/chat/investor` | Investor LLM discovery, questions and comparisons |
| POST | `/chat/admin` | Leadership LLM analysis of current business records |
| GET | `/search/parcels` | Semantic retrieval using `q` and optional `limit` |
| GET | `/dashboard/stats` | Existing dashboard aggregate endpoint |

Collection requests accept `page` and `page_size`; the maximum page size is 100. Read every page to obtain the complete original portfolio.

### Chat requests

```json
{
  "message": "Find available commercial land in East Riyadh"
}
```

For an investor question about selected lands, add one or two real IDs:

```json
{
  "message": "Compare these two parcels",
  "parcel_ids": ["SRE-041", "SRE-104"]
}
```

Responses contain `answer`, `parcels`, and `inquiries`. Investor responses do not expose the inquiry pipeline.

### How the AI is grounded

**Investor:** the model extracts filters; SQL applies factual constraints, and semantic retrieval can rank candidates. Current SQL records supply the facts. Explicit parcel IDs bypass semantic retrieval. Comparisons are AI-generated with authoritative residential/commercial classifications and separate purchase/annual-rent reasoning.

**Admin:** `ai/admin.py` reads the full current portfolio and pipeline, computes status and demand counts, unmatched inquiry IDs, oldest available listings, and separate budget averages. The LLM generates a structured explanation and selects up to five parcel/inquiry references. Returned IDs are checked against the snapshot. There is no scripted answer fallback.

Both advisors respond in the question's language and are instructed to avoid invented facts, returns, permissions, unsupported services, and unsolicited follow-up offers. These prompt constraints still need evaluation against live model responses.

### Inquiry fields

- `wants_to`: investment purpose.
- `intent`: `exploring`, `comparing options`, or `ready to move` for new submissions.
- `prefers`: `sale`, `lease`, or `any`.
- `budget_sar`: optional positive integer SAR amount.
- `budget_basis`: `total purchase` for buying or `annual rent` for leasing; absent when no budget is supplied.
- `selected_parcel_id`: optional parcel reference, stored separately from free text.

New inquiry phone numbers normalize Saudi local numbers and Arabic digits to international format. The API rejects unknown selected parcel IDs.

## Verification

```bash
uv run pytest tests -q
```

Tests cover inquiry structure, existing seed compatibility, land-type comparison instructions, complete admin snapshots, demand/matching logic, and generated-response wiring. Model responses are mocked; tests do not certify live generation quality.

A database-independent test configuration can use:

```bash
DATABASE_URL=sqlite:// QDRANT_URL=http://localhost:6333 uv run pytest tests -q
```

An optional local API read check:

```bash
curl 'http://localhost:8000/api/v1/parcels/?page=1&page_size=100'
```

Use disposable data for mutation checks. Verify original ID coverage in the final demo database, not just the row count.

## Deployment

The product has not yet been publicly deployed. Supply the database, model and Qdrant settings through the hosting platform's environment. If using `.env.production`, set `ENVIRONMENT=production` in the process environment **before** running migrations or starting the API; file selection happens before dotenv values are loaded.

```bash
ENVIRONMENT=production uv run alembic upgrade head
ENVIRONMENT=production uv run uvicorn landora_backend.main:app --app-dir src --host 0.0.0.0 --port 8000
```

Set the server port to the hosting platform's assigned port. Deploy the frontend with the publicly reachable `/api/v1` URL. Keep hosting, database, model access and required retrieval services available for at least two weeks after the assessment deadline.

## Project structure

```text
src/landora_backend/
├── api/              HTTP routes
├── ai/               Investor/admin LLM grounding, filters and embeddings
├── core/             Settings and database sessions
├── models/           SQLAlchemy parcel and inquiry models
├── schemas/          Request/response validation
├── services/         Database queries and mutations
├── scripts/          Provided-data seeding
└── vector/           Qdrant documents, collections and search
migrations/           Alembic schema history
data/                 Original assessment datasets
tests/                Automated checks
```

## Known limitations

Conversation history is not currently included in chat requests. Vector indexing is a separate operation. The API has no authentication or roles, and permanent deletion does not protect original assessment records. Historical snapshots, verified weekly trends, and conversion instrumentation are outside the current implementation. Public deployment and real model calls must be verified before submission.
