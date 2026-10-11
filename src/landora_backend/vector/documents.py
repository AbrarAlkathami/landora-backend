from landora_backend.models.inquiry import Inquiry
from landora_backend.models.parcel import Parcel


def parcel_to_text(parcel: Parcel) -> str:
    return f"""
    Parcel ID: {parcel.parcel_id}
    District: {parcel.district_en}
    District Arabic: {parcel.district_ar}
    Area of city: {parcel.area_of_city}
    Land type: {parcel.land_type}
    Listing type: {parcel.listing_type}
    Price basis: {parcel.price_basis}
    Area sqm: {parcel.area_sqm}
    Price per sqm SAR: {parcel.price_per_sqm_sar}
    Total price SAR: {parcel.total_price_sar}
    Street width meters: {parcel.street_width_m}
    Status: {parcel.status}
    Days on market: {parcel.days_on_market}
    """.strip()


def inquiry_to_text(inquiry: Inquiry) -> str:
    return f"""
    Inquiry ID: {inquiry.inquiry_id}
    Investor name: {inquiry.investor_name}
    Wants to: {inquiry.wants_to}
    Land type wanted: {inquiry.land_type_wanted}
    Area of city wanted: {inquiry.area_of_city_wanted}
    Prefers: {inquiry.prefers}
    Budget SAR: {inquiry.budget_sar}
    Budget basis: {inquiry.budget_basis}
    Intent: {inquiry.intent}
    Channel: {inquiry.channel}
    Status: {inquiry.status}
    """.strip()