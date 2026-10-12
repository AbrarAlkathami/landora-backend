"""Instructions for AI-generated comparisons grounded in current parcel records."""
import json


def comparison_instructions(parcels):
    classifications = [{"selection_order": index + 1, "parcel_id": parcel.parcel_id,
                        "land_type": parcel.land_type.strip().lower(),
                        "listing_type": parcel.listing_type.strip().lower()}
                       for index, parcel in enumerate(parcels)]
    return f"""
The user is comparing two explicitly selected lands. Generate your own comparison
using the current records, the question, and these authoritative classifications:
{json.dumps(classifications, ensure_ascii=False)}

Explain each parcel's land type accurately and give distinct reasons based on its facts.
- Residential means housing/residential development. Discuss space for a home or
  residential project, street access/frontage, location, and purchase or annual lease
  cost where supplied facts help. Never describe a residential parcel as commercial
  or recommend it for showrooms, shops, offices, or warehouses.
- Commercial means business/commercial development. Discuss business space and
  access/frontage using supplied facts, without claiming visibility, traffic, footfall,
  customer demand, permitted business activities, or profitability that are not recorded.
- If both lands are residential, keep the comparison focused on residential needs;
  do not introduce commercial benefits. If both are commercial, use commercial reasoning.
- If types differ, explain the difference and assess each separately for the user's goal.
- If the requested use conflicts with land type, explain the mismatch rather than
  presenting it as a benefit. Do not assume rezoning or use approval.
- Compare actual differences in size, street width, location, status, and price.
  If key facts are equal, say so; do not invent differentiators or a winner.
- Keep purchase prices and annual lease costs separate. Unknown prices stay unknown.
- Identify compared lands by IDs or districts when useful; you may reference recorded
  details to explain the comparison rather than merely repeat UI cards.
- General residential/commercial concepts are interpretive guidance, not confirmed
  project feasibility, zoning approval, buildable area, market demand, or investment returns.
- If fewer than two records were retrieved, explain the incomplete comparison.
- Respond in the user's language with a concise, tailored explanation.
- End after answering the question. Do not append follow-up questions, invitations,
  or unsolicited offers such as "If you want, I can..." or "إذا تريد، أقدّم...".
- Do not offer reports, checklists, viewing arrangements, verification services,
  reservations, negotiations, or other actions/services not explicitly provided by the system.
""".strip()
