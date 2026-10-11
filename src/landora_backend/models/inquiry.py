from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from landora_backend.core.database import Base


class Inquiry(Base):
    __tablename__ = "inquiries"

    inquiry_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        index=True,
    )

    date: Mapped[date] = mapped_column(Date)

    investor_name: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)

    wants_to: Mapped[str] = mapped_column(String)

    land_type_wanted: Mapped[str] = mapped_column(String)
    area_of_city_wanted: Mapped[str] = mapped_column(String)

    prefers: Mapped[str] = mapped_column(String)

    budget_sar: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    budget_basis: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    intent: Mapped[str] = mapped_column(String)
    channel: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)