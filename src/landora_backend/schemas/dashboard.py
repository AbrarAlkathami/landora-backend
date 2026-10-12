from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    total_parcels: int
    available_parcels: int
    total_inquiries: int