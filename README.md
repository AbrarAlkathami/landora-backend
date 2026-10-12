# Landora Backend

Backend service for **Landora**, an AI-powered Riyadh land discovery and investor inquiry platform.

The backend provides structured parcel and inquiry management, semantic search, exact database filtering, and grounded AI responses using PostgreSQL, Qdrant, and OpenAI.

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Qdrant
- OpenAI API
- Pydantic
- uv

## Features

- Parcel management
- Investor inquiry management
- PostgreSQL-based exact filtering
- Qdrant semantic search
- Hybrid SQL + vector retrieval
- Structured filter extraction from natural language
- Arabic and English AI queries
- Grounded AI responses using actual portfolio data
- Structured chat responses with matched parcels and inquiries

## Architecture

```text
User Question
     |
     v
Filter Extraction
     |
     +--------------------+
     |                    |
     v                    v
PostgreSQL             Qdrant
Exact Filters       Semantic Search
     |                    |
     +---------+----------+
               |
               v
        Retrieved Context
               |
               v
            OpenAI
               |
               v
      Grounded AI Response
```

PostgreSQL is the source of truth for structured and numeric data.

Qdrant is used as a semantic index for meaning-based retrieval.

The LLM only answers using retrieved Landora context.

## Project Structure

```text
landora-backend/
├── data/
├── migrations/
├── src/
│   └── landora_backend/
│       ├── ai/
│       │   ├── chat.py
│       │   ├── embeddings.py
│       │   └── filter_extractor.py
│       ├── api/
│       │   ├── chat.py
│       │   ├── inquiries.py
│       │   ├── parcels.py
│       │   ├── router.py
│       │   └── search.py
│       ├── core/
│       │   ├── config.py
│       │   └── database.py
│       ├── models/
│       │   ├── inquiry.py
│       │   └── parcel.py
│       ├── schemas/
│       │   ├── chat.py
│       │   ├── inquiry.py
│       │   └── parcel.py
│       ├── scripts/
│       │   ├── seed_inquiries.py
│       │   └── seed_parcels.py
│       ├── services/
│       │   ├── inquiry_service.py
│       │   └── parcel_service.py
│       ├── vector/
│       │   ├── documents.py
│       │   ├── index_data.py
│       │   ├── qdrant.py
│       │   ├── qdrant_collections.py
│       │   └── search.py
│       └── main.py
├── .env.example
├── alembic.ini
└── pyproject.toml
```

## Environment Variables

Create:

```text
.env.local
```

Example:

```env
ENVIRONMENT=local

DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/landora

OPENAI_API_KEY=your_openai_api_key

QDRANT_URL=https://your-qdrant-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
```

Do not commit `.env.local` or production secrets.

## Installation

Install dependencies:

```bash
uv sync
```

If Python 3.12 is not installed:

```bash
uv python install 3.12
uv python pin 3.12
uv sync
```

## Database Setup

Create a PostgreSQL database named:

```text
landora
```

Run migrations:

```bash
uv run alembic upgrade head
```

## Seed Data

Seed parcels:

```bash
PYTHONPATH=src uv run python src/landora_backend/scripts/seed_parcels.py
```

Seed investor inquiries:

```bash
PYTHONPATH=src uv run python src/landora_backend/scripts/seed_inquiries.py
```

The current dataset contains:

- 120 Riyadh land parcels
- 48 investor inquiries

## Qdrant Setup

Create the required collections and payload indexes:

```bash
PYTHONPATH=src uv run python src/landora_backend/vector/qdrant_collections.py
```

Index PostgreSQL data into Qdrant:

```bash
PYTHONPATH=src uv run python src/landora_backend/vector/index_data.py
```

The current collections are:

```text
landora_parcels
landora_inquiries
```

## Running the API

Start the development server:

```bash
uv run uvicorn landora_backend.main:app --reload --app-dir src
```

API:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

## Main API Endpoints

### Parcels

```text
GET    /api/v1/parcels/
GET    /api/v1/parcels/{parcel_id}
POST   /api/v1/parcels/
PATCH  /api/v1/parcels/{parcel_id}
DELETE /api/v1/parcels/{parcel_id}
```

### Investor Inquiries

```text
GET    /api/v1/inquiries/
GET    /api/v1/inquiries/{inquiry_id}
POST   /api/v1/inquiries/
PATCH  /api/v1/inquiries/{inquiry_id}
DELETE /api/v1/inquiries/{inquiry_id}
```

### Semantic Search

```text
GET /api/v1/search/parcels
```

Example:

```text
/api/v1/search/parcels?q=commercial land suitable for a showroom
```

### AI Chat

```text
POST /api/v1/chat
```

Example request:

```json
{
  "message": "Show me commercial land in East Riyadh under 8 million suitable for a showroom"
}
```

Example response:

```json
{
  "answer": "I found several matching commercial parcels...",
  "parcels": [
    {
      "parcel_id": "SRE-001",
      "district_en": "Al Khalidiyah",
      "district_ar": "الخالدية",
      "land_type": "commercial",
      "listing_type": "sale",
      "status": "available",
      "total_price_sar": 7500000
    }
  ],
  "inquiries": []
}
```

## AI Retrieval Strategy

Landora uses hybrid retrieval.

Exact questions such as:

```text
commercial land in East Riyadh under 8 million
```

are handled using PostgreSQL filters.

Semantic questions such as:

```text
land suitable for a car showroom
```

are handled using Qdrant embeddings.

Mixed questions such as:

```text
commercial land in East Riyadh under 8 million suitable for a showroom
```

use:

```text
PostgreSQL filtering
        +
Qdrant semantic ranking
        +
OpenAI grounded response
```

This keeps numeric and structured answers accurate while still supporting natural-language search.

## Arabic Support

The AI layer supports both Arabic and English queries.

Example:

```text
أبغى أرض تجارية شرق الرياض بأقل من ٨ مليون
```

The system extracts the same structured filters as the English equivalent and returns a response in the user's language.

## Development Notes

- PostgreSQL is the source of truth.
- Qdrant should not be treated as the authoritative database.
- Parcel and inquiry IDs must never be invented by the AI.
- AI responses should only use retrieved Landora data.
- Qdrant payloads may need to be re-indexed when searchable fields change.
- Database schema changes should be managed through Alembic migrations.

## Roadmap

- Frontend integration with Next.js
- Chat UI with parcel and inquiry cards
- Map-based parcel exploration
- Admin analytics dashboard
- Better ranking and relevance evaluation
- Automated vector synchronization after database updates
- Production deployment

## License

This project is currently maintained as a personal portfolio and experimental AI real-estate platform.
# Structured website inquiries

Admin Sarj Intelligence now uses the LLM through `/api/v1/chat/admin`. `ai/admin.py` reads a complete current SQL snapshot, computes portfolio/demand counts, unmatched inquiries, oldest available parcels, and separate purchase/lease budget averages, then requests a structured AI-generated answer. Returned record IDs are checked against the snapshot. No vector retrieval or scripted answer fallback is used for admin leadership questions. Existing `OPENAI_API_KEY` configuration is required; restart the API after updating. Automated tests mock model responses, so they verify grounding and wiring rather than live generation quality.

Explicit two-parcel investor comparisons are AI-generated using current SQL records and authoritative land-type instructions. Residential lands require housing/development reasoning; commercial lands require commercial space/access reasoning; mixed comparisons explain each type separately. The selected order is retained. Other AI answers receive land-type-specific instructions, and parcel search context is rebuilt from current database records rather than potentially stale vector text. No comparison answer is templated. Zoning approval and investment returns must not be inferred from land type.

Website submissions separate investment purpose (`wants_to`) from readiness (`intent`: `exploring`, `comparing options`, `ready to move`). They capture canonical land type, area, transaction, and optional integer SAR budget. A budget requires a matching basis: `total purchase` for sale or `annual rent` for lease. New phone values normalize to international format, including local Saudi mobiles and Arabic digits.

The nullable `selected_parcel_id` foreign key records the chosen land independently of purpose. Unknown parcel references are rejected by the API. Existing inquiry records remain unchanged.

Before deploying these changes, run `alembic upgrade head` in the backend environment and restart the API. Migration `ea8f2d41b607` adds the parcel reference and index. It has been tested with existing records on a temporary SQLite database; it has not been applied to the live database by the coding agent.
