from fastapi import APIRouter, Query

from landora_backend.vector.search import search_parcels


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/parcels")
def semantic_search_parcels(
    q: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=20),
):
    results = search_parcels(q, limit)

    return [
        {
            "score": result.score,
            "parcel_id": result.payload.get("parcel_id"),
            "district_en": result.payload.get("district_en"),
            "district_ar": result.payload.get("district_ar"),
            "land_type": result.payload.get("land_type"),
            "listing_type": result.payload.get("listing_type"),
            "status": result.payload.get("status"),
            "text": result.payload.get("text"),
        }
        for result in results
    ]