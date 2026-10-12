from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from landora_backend.models.parcel import Parcel
from landora_backend.schemas.parcel import ParcelCreate, ParcelUpdate


def get_parcels(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    status: str | None = None,
    land_type: str | None = None,
    listing_type: str | None = None,
):
    statement = select(Parcel)

    if search:
        search_value = f"%{search}%"

        statement = statement.where(
            or_(
                Parcel.parcel_id.ilike(search_value),
                Parcel.district_en.ilike(search_value),
                Parcel.district_ar.ilike(search_value),
            )
        )

    if status:
        statement = statement.where(
            func.lower(Parcel.status) == status.lower()
        )

    if land_type:
        statement = statement.where(
            func.lower(Parcel.land_type) == land_type.lower()
        )

    if listing_type:
        statement = statement.where(
            func.lower(Parcel.listing_type) == listing_type.lower()
        )

    count_statement = select(func.count()).select_from(
        statement.subquery()
    )

    total = db.scalar(count_statement) or 0

    offset = (page - 1) * page_size

    statement = (
        statement
        .order_by(Parcel.parcel_id)
        .offset(offset)
        .limit(page_size)
    )

    items = list(db.scalars(statement).all())

    total_pages = (
        (total + page_size - 1) // page_size
        if total > 0
        else 0
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


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
    db: Session,
    land_type: str | None = None,
    area_of_city: str | None = None,
    listing_type: str | None = None,
    status: str | None = None,
    max_total_price: float | None = None,
    parcel_ids: list[str] | None = None,
):
    query = select(Parcel)

    if parcel_ids:
        query = query.where(
            Parcel.parcel_id.in_(parcel_ids)
        )

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