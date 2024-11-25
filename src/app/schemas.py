# schemas.py
# from pydantic import BaseModel
# from typing import List
# from datetime import datetime

from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

class Message(BaseModel):
    user_message: str
    bot_messages: str

class ChatHistoryBase(BaseModel):
    user_id: str
    user_message: str
    bot_messages: str

class ChatHistoryResponse(ChatHistoryBase):
    id: int
    timestamp: datetime
    class Config:
        orm_mode = True

# Pydantic Models for User
class UserBase(BaseModel):
    user_name: str
    password: str  # This should be a hashed password!
    
    

class UserCreate(UserBase):
    employee_id:str
    full_name: str


class UserOut(UserBase):
    user_id:  uuid.UUID
    timestamp: datetime
    full_name: str

    class Config:
        orm_mode = True  # This tells Pydantic to treat the SQLAlchemy model as a dict

class UserUpdate(BaseModel):
    user_name: Optional[str]
    full_name: Optional[str]
    password: Optional[str]  # This should be a hashed password!

    class Config:
        orm_mode = True
class UserResponses(BaseModel):
    message:str
    data: Optional[UserCreate] = None

class UserResponse(BaseModel):
    detail : UserResponses

class UserLogin(BaseModel):
    message:str
    data: Optional[UserOut] = None

class UserLoginRespnse(BaseModel):
    detail : UserLogin

    

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_name: Optional[str] = None

# Pydantic Models for ChatSession
class ChatSessionBase(BaseModel):
    session_name: Optional[str]  # Optional field for session name

class ChatSessionCreate(ChatSessionBase):
    user_id:  uuid.UUID

class ChatSessionOut(ChatSessionBase):
    session_id:  uuid.UUID
    user_id:  uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True

# Pydantic Models for Message
class MessageBase(BaseModel):
    message_content: str
    message_type: Optional[str]  # e.g., text, image, etc.

class MessageCreate(MessageBase):
    session_id:  uuid.UUID
    sender_id:  uuid.UUID

class MessageOut(MessageBase):
    message_id:  uuid.UUID
    session_id:  uuid.UUID
    sender_id:  uuid.UUID
    timestamp: datetime

    class Config:
        orm_mode = True

# Pydantic Models for Role
class RoleBase(BaseModel):
    role_name: str

class RoleCreate(RoleBase):
    pass

class RoleOut(RoleBase):
    role_id: int

    class Config:
        orm_mode = True

# Pydantic Models for UserRole Association
class UserRoleBase(BaseModel):
    user_id:  uuid.UUID
    role_id: int

    class Config:
        orm_mode = True

# Pydantic Model for User Update Role
class UserUpdateRole(BaseModel):
    roles: List[int]  # List of role IDs to be updated for the user

    class Config:
        orm_mode = True


class PaginatedMessageOut(BaseModel):
    session_id: uuid.UUID
    page: int
    page_size: int
    total_messages: int
    messages: List[MessageOut]


class Employee(BaseModel):
    employ_id:str
    full_name:str
    department:Optional[str]

    class Config:
        orm_mode = True