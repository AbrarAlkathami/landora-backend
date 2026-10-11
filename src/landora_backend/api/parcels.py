from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from landora_backend.core.database import get_db
from landora_backend.schemas.parcel import (
    ParcelCreate,
    ParcelResponse,
    ParcelUpdate,
)
from landora_backend.services import parcel_service


router = APIRouter(
    prefix="/parcels",
    tags=["Parcels"],
)

DBSession = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[ParcelResponse])
def get_parcels(db: DBSession):
    return parcel_service.get_parcels(db)


@router.get("/{parcel_id}", response_model=ParcelResponse)
def get_parcel(parcel_id: str, db: DBSession):
    parcel = parcel_service.get_parcel(db, parcel_id)

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel not found",
        )

    return parcel


@router.post(
    "/",
    response_model=ParcelResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_parcel(parcel_data: ParcelCreate, db: DBSession):
    existing = parcel_service.get_parcel(db, parcel_data.parcel_id)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Parcel already exists",
        )

    return parcel_service.create_parcel(db, parcel_data)


@router.patch("/{parcel_id}", response_model=ParcelResponse)
def update_parcel(
    parcel_id: str,
    parcel_data: ParcelUpdate,
    db: DBSession,
):
    parcel = parcel_service.get_parcel(db, parcel_id)

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel not found",
        )

    return parcel_service.update_parcel(
        db,
        parcel,
        parcel_data,
    )


@router.delete(
    "/{parcel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_parcel(parcel_id: str, db: DBSession):
    parcel = parcel_service.get_parcel(db, parcel_id)

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel not found",
        )

    parcel_service.delete_parcel(db, parcel)