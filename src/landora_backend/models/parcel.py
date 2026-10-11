from datetime import date

from sqlalchemy import Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from landora_backend.core.database import Base


class Parcel(Base):
    __tablename__ = "parcels"

    parcel_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        index=True,
    )

    district_en: Mapped[str] = mapped_column(String)
    district_ar: Mapped[str] = mapped_column(String)

    area_of_city: Mapped[str] = mapped_column(String)
    land_type: Mapped[str] = mapped_column(String)
    listing_type: Mapped[str] = mapped_column(String)

    price_basis: Mapped[str] = mapped_column(String)

    area_sqm: Mapped[float] = mapped_column(Float)
    price_per_sqm_sar: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_price_sar: Mapped[float | None] = mapped_column(Float, nullable=True)

    street_width_m: Mapped[float] = mapped_column(Float)

    status: Mapped[str] = mapped_column(String)

    listed_date: Mapped[date] = mapped_column(Date)
    days_on_market: Mapped[int] = mapped_column(Integer)

    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)