"""
EPM — Chatbot router (F-022).

POST /api/v1/chatbot/query
  Accepts a natural-language message, matches it against known intents,
  returns a structured response, and logs the exchange to
  chatbot_conversations.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session, get_current_user
from app.models import User, ChatbotConversation
from app.services.chatbot import (
    MAX_MESSAGE_LENGTH,
    route_intent,
    extract_entities,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])


def _envelope(data, meta=None):
    return {"data": data, "meta": meta if meta is not None else {}, "error": None}


# ─── Schemas ─────────────────────────────────────────────────────────────────

class ChatbotQueryRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_length(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message cannot be empty")
        if len(stripped) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message too long ({len(stripped)} chars). Maximum is {MAX_MESSAGE_LENGTH}.")
        return stripped


# ─── Endpoint ────────────────────────────────────────────────────────────────

@router.post("/query")
async def chatbot_query(
    payload: ChatbotQueryRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    message = payload.message

    # Step 1: Extract entities (once, before intent matching)
    entities = extract_entities(message)

    # Step 2: Match and dispatch
    result, execution_status = await route_intent(session, current_user, message, entities)

    # Step 3: Log to chatbot_conversations
    log_entry = ChatbotConversation(
        user_id=current_user.id,
        message=message,
        matched_intent=result.get("matched_intent"),
        extracted_entities={
            k: str(v) if hasattr(v, "isoformat") else v
            for k, v in vars(entities).items()
            if v is not None and not k.startswith("_")
        } or None,
        execution_status=execution_status,
        response=result["response"],
    )
    session.add(log_entry)
    await session.commit()

    return _envelope(result)
