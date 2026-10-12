from fastapi import APIRouter

from landora_backend.api.parcels import router as parcels_router
from landora_backend.api.inquiries import router as inquiries_router
from landora_backend.api.search import router as search_router
from landora_backend.api.chat import router as chat_router
from landora_backend.api.dashboard import router as dashboard_router
api_router = APIRouter()

api_router.include_router(parcels_router)
api_router.include_router(inquiries_router)
api_router.include_router(search_router)
api_router.include_router(chat_router)
api_router.include_router(dashboard_router)