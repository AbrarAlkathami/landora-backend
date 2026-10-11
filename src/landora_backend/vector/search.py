from landora_backend.ai.embeddings import embed_text
from landora_backend.vector.qdrant import client
from landora_backend.vector.qdrant_collections import (
    PARCELS_COLLECTION,
    INQUIRIES_COLLECTION,
)

from qdrant_client.models import FieldCondition, Filter, MatchAny



def search_parcels(
    query: str,
    limit: int = 5,
    parcel_ids: list[str] | None = None,
):
    vector = embed_text(query)

    query_filter = None

    if parcel_ids:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="parcel_id",
                    match=MatchAny(any=parcel_ids),
                )
            ]
        )

    results = client.query_points(
        collection_name=PARCELS_COLLECTION,
        query=vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
    )

    return results.points


def search_inquiries(query: str, limit: int = 5):
    vector = embed_text(query)

    results = client.query_points(
        collection_name=INQUIRIES_COLLECTION,
        query=vector,
        limit=limit,
        with_payload=True,
    )

    return results.points