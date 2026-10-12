from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from landora_backend.models.parcel import Parcel

from landora_backend.core.database import get_db
from landora_backend.schemas.inquiry import (
    InquiryCreate,
    InquiryResponse,
    InquiryUpdate,
    PaginatedInquiriesResponse,
)
from landora_backend.services import inquiry_service


router = APIRouter(
    prefix="/inquiries",
    tags=["Inquiries"],
)

DBSession = Annotated[Session, Depends(get_db)]

@router.get("/", response_model=PaginatedInquiriesResponse)
def get_inquiries(
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    area_of_city_wanted: str | None = None,
    land_type_wanted: str | None = None,
    prefers: str | None = None,
):
    return inquiry_service.get_inquiries(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        status=status_filter,
        area_of_city_wanted=area_of_city_wanted,
        land_type_wanted=land_type_wanted,
        prefers=prefers,
    )


@router.get("/{inquiry_id}", response_model=InquiryResponse)
def get_inquiry(inquiry_id: str, db: DBSession):
    inquiry = inquiry_service.get_inquiry(db, inquiry_id)

    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found",
        )

    return inquiry


@router.post(
    "/",
    response_model=InquiryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inquiry(
    inquiry_data: InquiryCreate,
    db: DBSession,
):
    if inquiry_data.selected_parcel_id and not db.get(Parcel, inquiry_data.selected_parcel_id):
        raise HTTPException(status_code=422, detail="Selected parcel does not exist")
    existing = inquiry_service.get_inquiry(
        db,
        inquiry_data.inquiry_id,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Inquiry already exists",
        )

    return inquiry_service.create_inquiry(
        db,
        inquiry_data,
    )


@router.patch(
    "/{inquiry_id}",
    response_model=InquiryResponse,
)
def update_inquiry(
    inquiry_id: str,
    inquiry_data: InquiryUpdate,
    db: DBSession,
):
    if inquiry_data.selected_parcel_id and not db.get(Parcel, inquiry_data.selected_parcel_id):
        raise HTTPException(status_code=422, detail="Selected parcel does not exist")
    inquiry = inquiry_service.get_inquiry(db, inquiry_id)

    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found",
        )

    return inquiry_service.update_inquiry(
        db,
        inquiry,
        inquiry_data,
    )


@router.delete(
    "/{inquiry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_inquiry(inquiry_id: str, db: DBSession):
    inquiry = inquiry_service.get_inquiry(db, inquiry_id)

    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found",
        )

    inquiry_service.delete_inquiry(db, inquiry)
