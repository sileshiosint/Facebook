from pydantic import BaseModel, Field, EmailStr # Added EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId # Import ObjectId for validation

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v is None: # Allow None to pass through for Optional fields
            return None
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Not a valid ObjectId")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# --- Post Schemas ---
class PostBase(BaseModel):
    keyword_search_term: Optional[str] = None
    source_type: Optional[str] = None
    group_name: Optional[str] = None
    group_url: Optional[str] = None
    page_name: Optional[str] = None
    page_url: Optional[str] = None
    post_url: Optional[str] = None
    post_text: Optional[str] = None
    post_time: Optional[datetime] = None
    user_name: Optional[str] = None
    user_id: Optional[str] = None
    reactions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    comment_count: Optional[int] = 0
    language: Optional[str] = None
    ner_entities: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    hate_speech_keywords: Optional[List[str]] = Field(default_factory=list)
    extremism_keywords: Optional[List[str]] = Field(default_factory=list)
    sentiment: Optional[Dict[str, float]] = Field(default_factory=dict)
    risk_score: Optional[int] = None
    scraped_timestamp: Optional[datetime] = None
    analysis_timestamp: Optional[datetime] = None

class Post(PostBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')

    class Config:
        orm_mode = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        allow_population_by_field_name = True

# --- Profile Schemas ---
class ProfileBase(BaseModel):
    keyword_search_term: Optional[str] = None
    user_name: Optional[str] = None
    profile_url: Optional[str] = None
    scraped_timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Profile(ProfileBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')

    class Config:
        orm_mode = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat(),
        }
        allow_population_by_field_name = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None # Use EmailStr for email validation

class UserCreate(UserBase):
    password: str

class UserInDBBase(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    hashed_password: str
    disabled: Optional[bool] = False

    class Config: # Apply to UserInDBBase
        orm_mode = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        allow_population_by_field_name = True

# For returning user info from API (without password)
class User(UserBase): # Inherits username, email
    id: str # Return id as string for API responses
    disabled: Optional[bool] = None

    class Config:
        orm_mode = True
        # No need for json_encoders here if not directly encoding PyObjectId

# Model for user data stored in and retrieved from DB by auth logic
class UserInDB(UserInDBBase): # Inherits all fields from UserInDBBase
    pass

# Model for user data stored in and retrieved from DB by auth logic
class UserInDB(UserInDBBase): # Inherits all fields from UserInDBBase
    pass

class PostsResponse(BaseModel):
    data: List[Post]
    total_count: int

class ProfilesResponse(BaseModel):
    data: List[Profile]
    total_count: int

# --- Analytics Schemas ---
class RiskCategoryCount(BaseModel):
    category: str
    count: int

class EntityCount(BaseModel):
    entity: str # Could also be named 'text' to match ner_entities structure
    label: Optional[str] = None
    count: int

class LanguageCount(BaseModel):
    language: str
    count: int

class TimeSeriesDataPoint(BaseModel):
    date: Any # Can be str, or a more specific date/datetime if transformed
    count: int
