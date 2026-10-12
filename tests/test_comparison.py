from types import SimpleNamespace
from landora_backend.ai.comparison import comparison_instructions


def parcel(kind="residential", **changes):
    return SimpleNamespace(**(dict(parcel_id="SRE-1", land_type=kind, listing_type="sale") | changes))


def test_residential_classifications_are_authoritative():
    instructions = comparison_instructions([parcel(), parcel(parcel_id="SRE-2")])
    assert instructions.count('"land_type": "residential"') == 2
    assert "If both lands are residential" in instructions
    assert "do not introduce commercial benefits" in instructions
    assert "Generate your own comparison" in instructions
    assert "Do not append follow-up questions" in instructions
    assert "unsolicited offers" in instructions


def test_mixed_types_and_transaction_basis_stay_separate():
    instructions = comparison_instructions([parcel(), parcel("commercial", parcel_id="SRE-2", listing_type="lease")])
    assert '"land_type": "residential"' in instructions
    assert '"land_type": "commercial"' in instructions
    assert '"listing_type": "lease"' in instructions
    assert "Keep purchase prices and annual lease costs separate" in instructions


def test_selected_order_and_missing_data_rules():
    instructions = comparison_instructions([parcel(parcel_id="SRE-2"), parcel(parcel_id="SRE-1")])
    assert instructions.index('"parcel_id": "SRE-2"') < instructions.index('"parcel_id": "SRE-1"')
    assert "If fewer than two records were retrieved" in instructions
    assert "do not invent differentiators or a winner" in instructions
