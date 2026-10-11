from sqlalchemy import func, select
from sqlalchemy.orm import Session
from landora_backend.models.inquiry import Inquiry
from landora_backend.schemas.inquiry import InquiryCreate, InquiryUpdate


def get_inquiries(db: Session) -> list[Inquiry]:
    statement = select(Inquiry)
    return list(db.scalars(statement).all())


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