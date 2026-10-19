from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    username: str
    email: str

class CreateUser(UserBase):
    password: str

class LoginUser(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    balance: float
    created_add: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None