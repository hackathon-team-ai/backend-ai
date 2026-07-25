from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    role: str = "farmer"  # farmer, agronomist, admin
    state: Optional[str] = "Maharashtra"
    district: Optional[str] = "Pune"
    soil_type: Optional[str] = "Alluvial"
    farm_size_acres: Optional[float] = 2.5
    preferred_language: str = "en"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    soil_type: Optional[str] = None
    farm_size_acres: Optional[float] = None
    preferred_language: Optional[str] = None

class UserInDB(UserBase):
    id: str = Field(..., alias="_id")
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None

class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str
