# app/models/conversation.py
"""
会話関連モデル（conversation_sessions, conversation_logs, chat_sessions テーブル）
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class ConversationSession(Base):
    """会話セッション"""
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=False)
    session_id = Column(String(100), unique=True, nullable=False)
    total_turns = Column(Integer)
    end_reason = Column(String(50))
    final_match_percentage = Column(Float)
    presented_jobs = Column(JSON)
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, server_default=func.now())


class ConversationLog(Base):
    """会話ログ"""
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    turn_number = Column(Integer, nullable=False)
    user_message = Column(Text)
    ai_response = Column(Text)
    extracted_intent = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())


class ChatSession(Base):
    """チャットセッション（JSON格納）"""
    __tablename__ = "chat_sessions"

    session_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
