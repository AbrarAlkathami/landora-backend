from datetime import date

from pydantic import BaseModel, ConfigDict


class ParcelBase(BaseModel):
    district_en: str
    district_ar: str
    area_of_city: str
    land_type: str
    listing_type: str
    price_basis: str
    area_sqm: float
    price_per_sqm_sar: float | None = None
    total_price_sar: float | None = None
    street_width_m: float
    status: str
    listed_date: date
    days_on_market: int
    lat: float
    lng: float


class ParcelCreate(ParcelBase):
    parcel_id: str


class ParcelUpdate(BaseModel):
    district_en: str | None = None
    district_ar: str | None = None
    area_of_city: str | None = None
    land_type: str | None = None
    listing_type: str | None = None
    price_basis: str | None = None
    area_sqm: float | None = None
    price_per_sqm_sar: float | None = None
    total_price_sar: float | None = None
    street_width_m: float | None = None
    status: str | None = None
    listed_date: date | None = None
    days_on_market: int | None = None
    lat: float | None = None
    lng: float | None = None


class ParcelResponse(ParcelBase):
    parcel_id: str

    model_config = ConfigDict(from_attributes=True)

class PaginatedParcelsResponse(BaseModel):
    items: list[ParcelResponse]
    total: int
    page: int
    page_size: int
    total_pages: int