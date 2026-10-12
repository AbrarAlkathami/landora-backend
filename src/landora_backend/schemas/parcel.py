from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    model_config = ConfigDict(str_strip_whitespace=True, allow_inf_nan=False)
    parcel_id: str = Field(min_length=1, max_length=80)
    district_en: str = Field(min_length=1, max_length=120)
    district_ar: str = Field(min_length=1, max_length=120)
    area_of_city: Literal["North", "East", "West", "South", "Central"]
    land_type: Literal["residential", "commercial"]
    listing_type: Literal["sale", "lease"]
    price_basis: Literal["asking price", "annual rent"]
    status: Literal["available", "reserved", "sold", "leased"]
    area_sqm: float = Field(gt=0)
    street_width_m: float = Field(ge=0)
    total_price_sar: float | None = Field(default=None, ge=0)
    price_per_sqm_sar: float | None = Field(default=None, ge=0)
    days_on_market: int = Field(ge=0)
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)

    @model_validator(mode="after")
    def validate_price_basis(self):
        expected = "annual rent" if self.listing_type == "lease" else "asking price"
        if self.price_basis != expected:
            raise ValueError("Price basis must match sale or annual lease")
        return self


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
