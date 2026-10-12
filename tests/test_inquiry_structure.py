import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from landora_backend.schemas.inquiry import InquiryCreate, InquiryResponse


def payload(**changes):
    return dict(inquiry_id="INQ-test", date="2026-10-12", investor_name=" Sara ",
                phone="٠٥٥١٢٣٤٥٦٧", wants_to="open a showroom", intent="ready to move",
                land_type_wanted="commercial", area_of_city_wanted="East", prefers="sale",
                budget_sar=10000000, budget_basis="total purchase", selected_parcel_id="SRE-001",
                channel="website", status="new") | changes


def test_clean_fields_and_phone():
    inquiry = InquiryCreate.model_validate(payload())
    assert inquiry.phone == "+966551234567"
    assert inquiry.investor_name == "Sara"
    assert inquiry.intent == "ready to move"
    assert inquiry.wants_to == "open a showroom"
    assert inquiry.selected_parcel_id == "SRE-001"


@pytest.mark.parametrize("changes", [dict(budget_sar=-1), dict(prefers="lease"),
    dict(prefers="any"), dict(intent="open a showroom"), dict(phone="1234"),
    dict(budget_sar=None)])
def test_invalid_or_ambiguous_inputs_rejected(changes):
    with pytest.raises(ValidationError):
        InquiryCreate.model_validate(payload(**changes))


def test_optional_budget_and_parcel():
    inquiry = InquiryCreate.model_validate(payload(budget_sar=None, budget_basis=None, selected_parcel_id=None))
    assert inquiry.budget_sar is None
    assert inquiry.selected_parcel_id is None


def test_existing_seed_records_remain_importable():
    records = json.loads((Path(__file__).resolve().parents[1] / "data/investor-inquiries.json").read_text())
    for record in records:
        assert InquiryCreate.model_validate(record).selected_parcel_id is None
        assert InquiryResponse.model_validate(record).phone == record["phone"]
