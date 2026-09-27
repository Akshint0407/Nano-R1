import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user
from ..inference_client import InferenceServiceError, solve

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[schemas.ConversationOut])
def list_conversations(
    db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
) -> list[models.Conversation]:
    return (
        db.query(models.Conversation)
        .filter(models.Conversation.user_id == user.id)
        .order_by(models.Conversation.created_at.desc())
        .all()
    )


@router.get("/{conversation_id}", response_model=schemas.ConversationDetailOut)
def get_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> models.Conversation:
    conversation = _get_owned_conversation(db, user, conversation_id)
    return conversation


@router.post("", response_model=schemas.ConversationDetailOut, status_code=201)
def create_conversation_with_first_message(
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> models.Conversation:
    """Starts a new conversation and immediately solves the first question."""
    conversation = models.Conversation(
        user_id=user.id, title=payload.question[:60] or "Untitled"
    )
    db.add(conversation)
    db.flush()  # get conversation.id without a full commit

    message = _solve_and_store(db, conversation.id, payload.question)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.post("/{conversation_id}/messages", response_model=schemas.MessageOut, status_code=201)
def add_message(
    conversation_id: uuid.UUID,
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> models.Message:
    _get_owned_conversation(db, user, conversation_id)  # ownership check
    message = _solve_and_store(db, conversation_id, payload.question)
    db.commit()
    db.refresh(message)
    return message


def _get_owned_conversation(
    db: Session, user: models.User, conversation_id: uuid.UUID
) -> models.Conversation:
    conversation = db.get(models.Conversation, conversation_id)
    if conversation is None or conversation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


def _solve_and_store(db: Session, conversation_id: uuid.UUID, question: str) -> models.Message:
    try:
        result = solve(question)
    except InferenceServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    message = models.Message(
        conversation_id=conversation_id,
        question=question,
        reasoning=result.get("reasoning", ""),
        answer=result.get("answer", ""),
    )
    db.add(message)
    db.flush()
    return message
