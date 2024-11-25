# models.py
from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP,Text, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
Base = declarative_base()

user_roles = Table('user_roles', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.user_id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.role_id'), primary_key=True)
)


class User(Base):
    __tablename__="users"
    user_id = Column(UUID(as_uuid=True), primary_key=True,index=True,unique=True,nullable=False, default=uuid.uuid4)  
    employee_id=Column(String,unique=True,nullable=False, index=True)
    user_name = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    password = Column(String, nullable=False)  # Store hashed passwords!
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # This defines the reverse relationship to chat_sessions
    chat_sessions = relationship("ChatSession", back_populates="user")
    messages = relationship("Message", back_populates="sender")
    roles = relationship("Role", secondary=user_roles, back_populates="users")  # Define the roles relationship
    def __repr__(self):
        return f"<User(user_id={self.user_id}, user_name={self.user_name}, full_name={self.full_name})>"
    

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    session_name = Column(String(255), nullable=True)  # Optional
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship to the User model
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="chat_session")
    
    def __repr__(self):
        return f"<ChatSession(session_id={self.session_id}, user_id={self.user_id}, is_active={self.is_active})>"
    


class Message(Base):
    __tablename__ = 'messages'
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.session_id'), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    message_content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    message_type = Column(String(50), nullable=True)  # e.g., text, image, etc.
    
    # Relationship to ChatSession and User models
    chat_session = relationship("ChatSession", back_populates="messages")
    sender = relationship("User", back_populates="messages")



class Role(Base):
    __tablename__ = 'roles'
    
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)

    # Relationship to User through the user_roles association table
    users = relationship('User', secondary=user_roles, back_populates='roles')

    def __repr__(self):
        return f"<Role(role_id={self.role_id}, role_name={self.role_name})>"


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    user_message=Column(Text,nullable=True )
    bot_messages = Column(JSON, nullable=True)
    timestamp =  Column(DateTime, default=func.now())



class Employee(Base):
    __tablename__="employee"
    # id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    employ_id = Column(String,primary_key=True, unique=True, index=True)
    full_name=Column(String, nullable=False)
    department=Column(Text, nullable=True)
