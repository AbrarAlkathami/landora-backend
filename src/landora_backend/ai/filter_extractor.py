from typing import Literal

from openai import OpenAI
from pydantic import BaseModel

from landora_backend.core.config import settings


client = OpenAI(api_key=settings.openai_api_key)


class QueryFilters(BaseModel):
    target: Literal["parcel", "inquiry", "both"]
    land_type: str | None = None
    area_of_city: str | None = None
    listing_type: str | None = None
    status: str | None = None
    max_total_price: float | None = None
    semantic_query: str | None = None


def extract_filters(question: str) -> QueryFilters:
    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
            {
                "role": "system",
                "content": """
Extract structured filters from a Landora real-estate question.

Valid area_of_city values:
North, South, East, West, Central

Examples:
- "commercial land in east Riyadh"
  target=parcel, land_type=commercial, area_of_city=East

- "investors looking for commercial land in the east"
  target=inquiry, land_type=commercial, area_of_city=East

- "commercial land below 8 million"
  target=parcel, land_type=commercial, max_total_price=8000000

If part of the question is semantic, such as suitable for a showroom,
warehouse, school, or restaurant, put that meaning in semantic_query.

Do not invent filters that are not present in the question.
""",
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        text_format=QueryFilters,
    )

    return response.output_parsed