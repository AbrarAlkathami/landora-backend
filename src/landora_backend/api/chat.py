from fastapi import APIRouter

from landora_backend.ai.chat import answer_question
from landora_backend.schemas.chat import ChatRequest, ChatResponse


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    return answer_question(request.message)

