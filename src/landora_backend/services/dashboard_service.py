from sqlalchemy import func, select
from sqlalchemy.orm import Session

from landora_backend.models.inquiry import Inquiry
from landora_backend.models.parcel import Parcel


def get_dashboard_stats(db: Session):
    total_parcels = db.scalar(
        select(func.count()).select_from(Parcel)
    ) or 0

    available_parcels = db.scalar(
        select(func.count())
        .select_from(Parcel)
        .where(func.lower(Parcel.status) == "available")
    ) or 0

    total_inquiries = db.scalar(
        select(func.count()).select_from(Inquiry)
    ) or 0

    return {
        "total_parcels": total_parcels,
        "available_parcels": available_parcels,
        "total_inquiries": total_inquiries,
    }