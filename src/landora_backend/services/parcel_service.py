from sqlalchemy import func, select
from sqlalchemy.orm import Session

from landora_backend.models.parcel import Parcel
from landora_backend.schemas.parcel import ParcelCreate, ParcelUpdate


def get_parcels(db: Session) -> list[Parcel]:
    statement = select(Parcel)
    return list(db.scalars(statement).all())


def get_parcel(db: Session, parcel_id: str) -> Parcel | None:
    return db.get(Parcel, parcel_id)


def create_parcel(db: Session, parcel_data: ParcelCreate) -> Parcel:
    parcel = Parcel(**parcel_data.model_dump())

    db.add(parcel)
    db.commit()
    db.refresh(parcel)

    return parcel


def update_parcel(
    db: Session,
    parcel: Parcel,
    parcel_data: ParcelUpdate,
) -> Parcel:
    update_data = parcel_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(parcel, field, value)

    db.commit()
    db.refresh(parcel)

    return parcel


def delete_parcel(db: Session, parcel: Parcel) -> None:
    db.delete(parcel)
    db.commit()

def search_parcels_exact(
    db,
    land_type: str | None = None,
    area_of_city: str | None = None,
    listing_type: str | None = None,
    status: str | None = None,
    max_total_price: float | None = None,
):
    query = select(Parcel)

    if land_type:
        query = query.where(
            func.lower(Parcel.land_type) == land_type.lower()
        )

    if area_of_city:
        query = query.where(
            func.lower(Parcel.area_of_city) == area_of_city.lower()
        )

    if listing_type:
        query = query.where(
            func.lower(Parcel.listing_type) == listing_type.lower()
        )

    if status:
        query = query.where(
            func.lower(Parcel.status) == status.lower()
        )

    if max_total_price is not None:
        query = query.where(
            Parcel.total_price_sar.is_not(None),
            Parcel.total_price_sar <= max_total_price,
        )

    return list(db.scalars(query).all())