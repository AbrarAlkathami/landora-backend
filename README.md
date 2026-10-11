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