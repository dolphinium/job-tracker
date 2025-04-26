from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId
from app.models.user import PyObjectId

class StatusHistory(BaseModel):
    status: str
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class Document(BaseModel):
    name: str
    type: str  # "Resume", "Cover Letter"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Contact(BaseModel):
    name: str
    position: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None

class ApplicationBase(BaseModel):
    linkedin_url: HttpUrl
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_description: Optional[str] = None
    date_posted: Optional[datetime] = None
    applied_date: Optional[datetime] = None
    status: str = "Wishlist"
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_description: Optional[str] = None
    date_posted: Optional[datetime] = None
    applied_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class ApplicationInDB(ApplicationBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    linkedin_job_id: Optional[str] = None
    status_history: List[StatusHistory] = []
    documents: List[Document] = []
    contacts: List[Contact] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

class Application(ApplicationBase):
    id: str
    user_id: str
    linkedin_job_id: Optional[str] = None
    status_history: List[StatusHistory] = []
    documents: List[Document] = []
    contacts: List[Contact] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True