import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Auth ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Feedback ---

class FeedbackCreate(BaseModel):
    rating: int = Field(ge=-1, le=1)
    comment: str | None = None


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    rating: int
    comment: str | None
    created_at: datetime


# --- Messages / conversations ---

class MessageCreate(BaseModel):
    question: str = Field(min_length=1)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question: str
    reasoning: str
    answer: str
    created_at: datetime
    feedback: FeedbackOut | None = None


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    created_at: datetime


class ConversationDetailOut(ConversationOut):
    messages: list[MessageOut] = []
