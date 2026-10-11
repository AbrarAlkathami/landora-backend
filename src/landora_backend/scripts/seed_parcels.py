import json
from pathlib import Path

from landora_backend.core.database import SessionLocal
from landora_backend.models.parcel import Parcel


DATA_FILE = Path("data/sarj-lands-riyadh.json")


def seed_parcels():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        parcels_data = json.load(file)

    db = SessionLocal()

    try:
        inserted = 0
        skipped = 0

        for item in parcels_data:
            existing = db.get(Parcel, item["parcel_id"])

            if existing:
                skipped += 1
                continue

            parcel = Parcel(**item)
            db.add(parcel)
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
    seed_parcels()