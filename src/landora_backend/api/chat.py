from fastapi import APIRouter

from landora_backend.ai.chat import answer_question
from landora_backend.schemas.chat import ChatRequest, ChatResponse


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/investor", response_model=ChatResponse)
def investor_chat(request: ChatRequest):
    return answer_question(
        question=request.message,
        mode="investor",
    )


@router.post("/admin", response_model=ChatResponse)
def admin_chat(request: ChatRequest):
    return answer_question(
        question=request.message,
        mode="admin",
    )