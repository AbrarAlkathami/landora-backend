from qdrant_client.models import (
    Distance,
    PayloadSchemaType,
    VectorParams,
)

from landora_backend.vector.qdrant import client


PARCELS_COLLECTION = "landora_parcels"
INQUIRIES_COLLECTION = "landora_inquiries"

VECTOR_SIZE = 1536


def create_collections():
    existing = {
        collection.name
        for collection in client.get_collections().collections
    }

    if PARCELS_COLLECTION not in existing:
        client.create_collection(
            collection_name=PARCELS_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print(f"Created: {PARCELS_COLLECTION}")
    else:
        print(f"Already exists: {PARCELS_COLLECTION}")

    if INQUIRIES_COLLECTION not in existing:
        client.create_collection(
            collection_name=INQUIRIES_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print(f"Created: {INQUIRIES_COLLECTION}")
    else:
        print(f"Already exists: {INQUIRIES_COLLECTION}")

    # Needed because we filter Qdrant using parcel_id
    client.create_payload_index(
        collection_name=PARCELS_COLLECTION,
        field_name="parcel_id",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    print("Created/verified parcel_id payload index")


if __name__ == "__main__":
    create_collections()