from qdrant_client.models import PointStruct
from sqlalchemy import select

from landora_backend.ai.embeddings import embed_text
from landora_backend.core.database import SessionLocal
from landora_backend.models.inquiry import Inquiry
from landora_backend.models.parcel import Parcel
from landora_backend.vector.documents import inquiry_to_text, parcel_to_text
from landora_backend.vector.qdrant import client
from landora_backend.vector.qdrant_collections import (
    INQUIRIES_COLLECTION,
    PARCELS_COLLECTION,
)


def index_parcels():
    db = SessionLocal()

    try:
        parcels = list(db.scalars(select(Parcel)).all())

        points = []

        for i, parcel in enumerate(parcels):
            text = parcel_to_text(parcel)
            vector = embed_text(text)

            points.append(
                PointStruct(
                    id=i,
                    vector=vector,
                    payload={
                        "parcel_id": parcel.parcel_id,
                        "district_en": parcel.district_en,
                        "district_ar": parcel.district_ar,
                        "area_of_city": parcel.area_of_city,
                        "land_type": parcel.land_type,
                        "listing_type": parcel.listing_type,
                        "status": parcel.status,
                        "text": text,
                    },
                )
            )

        client.upsert(
            collection_name=PARCELS_COLLECTION,
            points=points,
        )

        print(f"Indexed {len(points)} parcels")

    finally:
        db.close()


def index_inquiries():
    db = SessionLocal()

    try:
        inquiries = list(db.scalars(select(Inquiry)).all())

        points = []

        for i, inquiry in enumerate(inquiries):
            text = inquiry_to_text(inquiry)
            vector = embed_text(text)

            points.append(
                PointStruct(
                    id=i,
                    vector=vector,
                    payload={
                        "inquiry_id": inquiry.inquiry_id,
                        "investor_name": inquiry.investor_name,
                        "land_type_wanted": inquiry.land_type_wanted,
                        "area_of_city_wanted": inquiry.area_of_city_wanted,
                        "prefers": inquiry.prefers,
                        "intent": inquiry.intent,
                        "status": inquiry.status,
                        "text": text,
                    },
                )
            )

        client.upsert(
            collection_name=INQUIRIES_COLLECTION,
            points=points,
        )

        print(f"Indexed {len(points)} inquiries")

    finally:
        db.close()


if __name__ == "__main__":
    index_parcels()
    index_inquiries()