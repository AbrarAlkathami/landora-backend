from openai import OpenAI

from landora_backend.ai.filter_extractor import extract_filters
from landora_backend.core.config import settings
from landora_backend.core.database import SessionLocal
from landora_backend.services.inquiry_service import search_inquiries_exact
from landora_backend.services.parcel_service import search_parcels_exact
from landora_backend.vector.documents import inquiry_to_text, parcel_to_text
from landora_backend.vector.search import search_inquiries, search_parcels


client = OpenAI(api_key=settings.openai_api_key)


def answer_question(
    question: str,
    mode: str = "investor",
) -> dict:
    filters = extract_filters(question)

    land_type = filters.land_type
    area = filters.area_of_city

    if mode == "investor":
        # Investor chatbot only has access to parcels
        is_parcel_question = True
        is_inquiry_question = False

    else:
        # Admin chatbot can access both
        is_parcel_question = filters.target in ("parcel", "both")
        is_inquiry_question = filters.target in ("inquiry", "both")

    # Always defined
    inquiry_context = ""
    parcel_context = ""

    selected_parcels = []
    selected_inquiries = []

    # -------------------------
    # INQUIRIES
    # -------------------------
    if is_inquiry_question and (land_type or area):
        db = SessionLocal()

        try:
            exact_inquiries = search_inquiries_exact(
                db,
                land_type=land_type,
                area_of_city=area,
            )

            selected_inquiries = exact_inquiries

            inquiry_context = "\n\n".join(
                inquiry_to_text(inquiry)
                for inquiry in exact_inquiries
            )

        finally:
            db.close()

    elif is_inquiry_question:
        inquiry_results = search_inquiries(
            filters.semantic_query or question,
            limit=5,
        )

        selected_inquiries = [
            result.payload
            for result in inquiry_results
            if result.payload
        ]

        inquiry_context = "\n\n".join(
            result.payload["text"]
            for result in inquiry_results
            if result.payload and result.payload.get("text")
        )

    # -------------------------
    # PARCELS
    # -------------------------
    has_parcel_filters = (
        land_type
        or area
        or filters.listing_type
        or filters.status
        or filters.max_total_price is not None
    )

    if is_parcel_question and has_parcel_filters:
        db = SessionLocal()

        try:
            exact_parcels = search_parcels_exact(
                db,
                land_type=land_type,
                area_of_city=area,
                listing_type=filters.listing_type,
                status=filters.status,
                max_total_price=filters.max_total_price,
            )

            selected_parcels = exact_parcels

            # SQL + semantic ranking
            if filters.semantic_query and exact_parcels:
                parcel_ids = [
                    parcel.parcel_id
                    for parcel in exact_parcels
                ]

                semantic_results = search_parcels(
                    filters.semantic_query,
                    limit=5,
                    parcel_ids=parcel_ids,
                )

                selected_parcels = [
                    result.payload
                    for result in semantic_results
                    if result.payload
                ]

                parcel_context = "\n\n".join(
                    result.payload["text"]
                    for result in semantic_results
                    if result.payload and result.payload.get("text")
                )

            # SQL only
            else:
                parcel_context = "\n\n".join(
                    parcel_to_text(parcel)
                    for parcel in exact_parcels
                )

        finally:
            db.close()

    elif is_parcel_question:
        parcel_results = search_parcels(
            filters.semantic_query or question,
            limit=5,
        )

        parcel_ids = [
            result.payload.get("parcel_id")
            for result in parcel_results
            if result.payload and result.payload.get("parcel_id")
        ]

        db = SessionLocal()

        try:
            exact_parcels = search_parcels_exact(
                db,
                parcel_ids=parcel_ids,
            )

            parcels_by_id = {
                parcel.parcel_id: parcel
                for parcel in exact_parcels
            }

            selected_parcels = [
                parcels_by_id[parcel_id]
                for parcel_id in parcel_ids
                if parcel_id in parcels_by_id
            ]

        finally:
            db.close()

        parcel_context = "\n\n".join(
            result.payload["text"]
            for result in parcel_results
            if result.payload and result.payload.get("text")
        )

    # -------------------------
    # FINAL LLM ANSWER
    # -------------------------
    if mode == "investor":
        prompt = f"""
    You are Landora, an AI assistant for investors looking for land in Riyadh.

    Answer ONLY using the supplied parcel data.

    Rules:
    - Never invent data.
    - Never claim there are no matches if matching records are provided.
    - Help the user discover suitable land parcels.
    - You do NOT have access to investor inquiries or internal company pipeline data.
    - Never discuss or expose other investors or their inquiries.
    - Answer in the same language as the user.
    - Keep the answer concise and useful.

    IMPORTANT UI RULES:
    - Parcel records will be displayed separately as UI cards.
    - If parcel records are provided, DO NOT list parcel IDs, districts, prices, sizes,
    statuses, or other parcel details in the text response.
    - Only give a short natural-language summary.
    - Do not repeat information already shown in the parcel cards.

    PARCEL DATA:
    {parcel_context or "No parcel records retrieved."}

    USER QUESTION:
    {question}
    """

    else:
        prompt = f"""
    You are Landora, an AI assistant for the Sarj Real Estate admin team.

    Answer ONLY using the supplied Landora data.

    Rules:
    - Never invent data.
    - Never claim there are no matches if matching records are provided.
    - You may answer questions about parcels and investor inquiries.
    - Answer in the same language as the user.
    - Keep the answer concise and useful.

    IMPORTANT UI RULES:
    - Parcel records will be displayed separately as UI cards.
    - Investor inquiries will be displayed separately as UI cards.
    - Do not repeat individual parcel or inquiry details in the text response.
    - Only provide a concise summary.

    PARCEL DATA:
    {parcel_context or "No parcel records retrieved."}

    INVESTOR INQUIRY DATA:
    {inquiry_context or "No inquiry records retrieved."}

    USER QUESTION:
    {question}
    """

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )

    # -------------------------
    # FORMAT PARCEL RESULTS
    # -------------------------
    parcels = []

    for parcel in selected_parcels:
        if isinstance(parcel, dict):
            parcels.append(
                {
                    "parcel_id": parcel.get("parcel_id"),
                    "district_en": parcel.get("district_en"),
                    "district_ar": parcel.get("district_ar"),
                    "land_type": parcel.get("land_type"),
                    "listing_type": parcel.get("listing_type"),
                    "status": parcel.get("status"),
                    "total_price_sar": parcel.get("total_price_sar"),
                }
            )
        else:
            parcels.append(
                {
                    "parcel_id": parcel.parcel_id,
                    "district_en": parcel.district_en,
                    "district_ar": parcel.district_ar,
                    "land_type": parcel.land_type,
                    "listing_type": parcel.listing_type,
                    "status": parcel.status,
                    "total_price_sar": parcel.total_price_sar,
                }
            )

    # -------------------------
    # FORMAT INQUIRY RESULTS
    # -------------------------
    inquiries = []

    for inquiry in selected_inquiries:
        if isinstance(inquiry, dict):
            inquiries.append(
                {
                    "inquiry_id": inquiry.get("inquiry_id"),
                    "investor_name": inquiry.get("investor_name"),
                    "land_type_wanted": inquiry.get("land_type_wanted"),
                    "area_of_city_wanted": inquiry.get("area_of_city_wanted"),
                    "status": inquiry.get("status"),
                }
            )
        else:
            inquiries.append(
                {
                    "inquiry_id": inquiry.inquiry_id,
                    "investor_name": inquiry.investor_name,
                    "land_type_wanted": inquiry.land_type_wanted,
                    "area_of_city_wanted": inquiry.area_of_city_wanted,
                    "status": inquiry.status,
                }
            )

    return {
        "answer": response.output_text,
        "parcels": parcels,
        "inquiries": inquiries if mode == "admin" else [],
    }