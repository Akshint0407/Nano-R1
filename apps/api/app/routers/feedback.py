import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/messages", tags=["feedback"])


@router.put("/{message_id}/feedback", response_model=schemas.FeedbackOut)
def upsert_feedback(
    message_id: uuid.UUID,
    payload: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> models.Feedback:
    message = (
        db.query(models.Message)
        .join(models.Conversation)
        .filter(models.Message.id == message_id, models.Conversation.user_id == user.id)
        .first()
    )
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.feedback is None:
        message.feedback = models.Feedback(
            message_id=message.id, rating=payload.rating, comment=payload.comment
        )
        db.add(message.feedback)
    else:
        message.feedback.rating = payload.rating
        message.feedback.comment = payload.comment

    db.commit()
    db.refresh(message.feedback)
    return message.feedback
