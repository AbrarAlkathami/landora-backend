from qdrant_client import QdrantClient

from landora_backend.core.config import settings


client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key,
)