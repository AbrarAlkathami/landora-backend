import datetime

from pydantic import BaseModel, ConfigDict


class InquiryBase(BaseModel):
    date: datetime.date
    investor_name: str
    phone: str
    wants_to: str
    land_type_wanted: str
    area_of_city_wanted: str
    prefers: str
    budget_sar: int | None = None
    budget_basis: str | None = None
    intent: str
    channel: str
    status: str


class InquiryCreate(InquiryBase):
    inquiry_id: str


class InquiryUpdate(BaseModel):
    date: datetime.date | None = None
    investor_name: str | None = None
    phone: str | None = None
    wants_to: str | None = None
    land_type_wanted: str | None = None
    area_of_city_wanted: str | None = None
    prefers: str | None = None
    budget_sar: int | None = None
    budget_basis: str | None = None
    intent: str | None = None
    channel: str | None = None
    status: str | None = None


class InquiryResponse(InquiryBase):
    inquiry_id: str

    model_config = ConfigDict(from_attributes=True)