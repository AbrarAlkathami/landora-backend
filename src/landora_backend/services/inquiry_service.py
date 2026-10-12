from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from landora_backend.models.inquiry import Inquiry
from landora_backend.schemas.inquiry import InquiryCreate, InquiryUpdate


def get_inquiries(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    status: str | None = None,
    area_of_city_wanted: str | None = None,
    land_type_wanted: str | None = None,
    prefers: str | None = None,
):
    statement = select(Inquiry)

    if search:
        search_value = f"%{search.strip()}%"

        statement = statement.where(
            or_(
                Inquiry.inquiry_id.ilike(search_value),
                Inquiry.investor_name.ilike(search_value),
                Inquiry.phone.ilike(search_value),
                Inquiry.wants_to.ilike(search_value),
                Inquiry.intent.ilike(search_value),
            )
        )

    if status:
        statement = statement.where(
            func.lower(Inquiry.status) == status.lower()
        )

    if area_of_city_wanted:
        statement = statement.where(
            func.lower(Inquiry.area_of_city_wanted)
            == area_of_city_wanted.lower()
        )

    if land_type_wanted:
        statement = statement.where(
            func.lower(Inquiry.land_type_wanted)
            == land_type_wanted.lower()
        )

    if prefers:
        statement = statement.where(
            func.lower(Inquiry.prefers) == prefers.lower()
        )

    count_statement = (
        select(func.count())
        .select_from(statement.subquery())
    )

    total = db.scalar(count_statement) or 0

    offset = (page - 1) * page_size

    statement = (
        statement
        .order_by(Inquiry.date.desc())
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


def get_inquiry(db: Session, inquiry_id: str) -> Inquiry | None:
    return db.get(Inquiry, inquiry_id)


def create_inquiry(
    db: Session,
    inquiry_data: InquiryCreate,
) -> Inquiry:
    inquiry = Inquiry(**inquiry_data.model_dump())

    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)

    return inquiry


def update_inquiry(
    db: Session,
    inquiry: Inquiry,
    inquiry_data: InquiryUpdate,
) -> Inquiry:
    update_data = inquiry_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(inquiry, field, value)

    db.commit()
    db.refresh(inquiry)

    return inquiry


def delete_inquiry(db: Session, inquiry: Inquiry) -> None:
    db.delete(inquiry)
    db.commit()

def search_inquiries_exact(
    db,
    land_type: str | None = None,
    area_of_city: str | None = None,
):
    query = select(Inquiry)

    if land_type:
        query = query.where(
            func.lower(Inquiry.land_type_wanted) == land_type.lower()
        )

    if area_of_city:
        query = query.where(
            func.lower(Inquiry.area_of_city_wanted) == area_of_city.lower()
        )

    return list(db.scalars(query).all())