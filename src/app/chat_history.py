# main.py
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List
from models import ChatHistory, Base
from schemas import ChatHistoryBase, ChatHistoryResponse, Message
from database import engine, get_db

# Initialize FastAPI app
history_app = APIRouter()

# Create tables in the database
Base.metadata.create_all(bind=engine)

# API endpoint to save chat history
@history_app.post("/chat-history", response_model=ChatHistoryResponse)
def save_chat_history(chat_history: ChatHistoryBase, db: Session = Depends(get_db)):
    db_chat = ChatHistory(user_id=chat_history.user_id, user_message=chat_history.user_message,bot_messages=chat_history.bot_messages)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

# API endpoint to fetch chat history
@history_app.get("/chat-history/{user_id}", response_model=List[ChatHistoryResponse])
def get_chat_history(user_id: str, db: Session = Depends(get_db)):
    db_chat = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).all()
    if db_chat is None:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return db_chat