import json
from pathlib import Path

from landora_backend.core.database import SessionLocal
from landora_backend.models.inquiry import Inquiry
from landora_backend.schemas.inquiry import InquiryCreate


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_FILE = BASE_DIR / "data" / "investor-inquiries.json"


def seed_inquiries():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        inquiries_data = json.load(file)

    db = SessionLocal()

    try:
        inserted = 0
        skipped = 0

        for item in inquiries_data:
            existing = db.get(Inquiry, item["inquiry_id"])

            if existing:
                skipped += 1
                continue

            validated = InquiryCreate.model_validate(item)

            inquiry = Inquiry(**validated.model_dump())

            db.add(inquiry)
            inserted += 1

        db.commit()

        print(f"Inserted: {inserted}")
        print(f"Skipped: {skipped}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_inquiries()