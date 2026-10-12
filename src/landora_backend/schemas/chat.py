from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    parcel_ids: list[str] | None = Field(default=None, min_length=1, max_length=2)


class ParcelChatResult(BaseModel):
    parcel_id: str
    district_en: str
    district_ar: str
    land_type: str
    listing_type: str
    status: str
    total_price_sar: float | None = None


class InquiryChatResult(BaseModel):
    inquiry_id: str
    investor_name: str
    land_type_wanted: str
    area_of_city_wanted: str
    status: str


class ChatResponse(BaseModel):
    answer: str
    parcels: list[ParcelChatResult]
    inquiries: list[InquiryChatResult]
