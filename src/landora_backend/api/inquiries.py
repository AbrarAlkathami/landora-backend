from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from landora_backend.core.database import get_db
from landora_backend.schemas.inquiry import (
    InquiryCreate,
    InquiryResponse,
    InquiryUpdate,
)
from landora_backend.services import inquiry_service


router = APIRouter(
    prefix="/inquiries",
    tags=["Inquiries"],
)

DBSession = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[InquiryResponse])
def get_inquiries(db: DBSession):
    return inquiry_service.get_inquiries(db)


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