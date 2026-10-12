import datetime
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class InquiryBase(BaseModel):
    date: datetime.date
    investor_name: str
    phone: str
    wants_to: str
    selected_parcel_id: str | None = None
    land_type_wanted: str
    area_of_city_wanted: str
    prefers: str
    budget_sar: int | None = None
    budget_basis: str | None = None
    intent: str
    channel: str
    status: str


class InquiryCreate(InquiryBase):
    model_config = ConfigDict(str_strip_whitespace=True)
    inquiry_id: str = Field(min_length=1, max_length=80)
    investor_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(pattern=r"^\+[1-9][0-9]{7,14}$")
    wants_to: str = Field(min_length=2, max_length=200)
    land_type_wanted: Literal["residential", "commercial", "any"]
    area_of_city_wanted: Literal["North", "East", "West", "South", "Central", "Any"]
    prefers: Literal["sale", "lease", "any"]
    budget_sar: int | None = Field(default=None, gt=0, le=2147483647)
    budget_basis: Literal["total purchase", "annual rent"] | None = None
    intent: Literal["exploring", "comparing options", "ready to move"]

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value):
        if not isinstance(value, str):
            return value
        value = value.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))
        value = re.sub(r"[\s()-]", "", value)
        if value.startswith("00"):
            value = "+" + value[2:]
        if re.fullmatch(r"05\d{8}", value):
            value = "+966" + value[1:]
        elif re.fullmatch(r"9665\d{8}", value):
            value = "+" + value
        return value

    @model_validator(mode="after")
    def validate_budget_basis(self):
        if self.budget_sar is not None:
            expected = {"sale": "total purchase", "lease": "annual rent"}.get(self.prefers)
            if expected is None or self.budget_basis != expected:
                raise ValueError("A budget requires a buy/lease preference and its matching basis")
        elif self.budget_basis is not None:
            raise ValueError("Budget basis requires a budget amount")
        return self


class InquiryUpdate(BaseModel):
    selected_parcel_id: str | None = None
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

class PaginatedInquiriesResponse(BaseModel):
    items: list[InquiryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
