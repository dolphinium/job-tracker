from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId
from app.models.user import PyObjectId # Assuming PyObjectId is defined in user.py


class StatusHistory(BaseModel):
    status: str
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class Document(BaseModel):
    name: str
    type: str  # "Resume", "Cover Letter"
    content: str # Consider if storing full content here is wise, maybe path?
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
    user_id: PyObjectId # Add user_id here if needed on creation

class ApplicationUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_description: Optional[str] = None
    date_posted: Optional[datetime] = None
    applied_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    # You might want to add fields here to update status_history, documents, contacts

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
        populate_by_name = True # UPDATED from allow_population_by_field_name
        arbitrary_types_allowed = True # Keep this
        json_encoders = {
            ObjectId: str,
            PyObjectId: str # Explicitly add PyObjectId too if needed
        }

class Application(ApplicationBase):
    id: str # Expose ID as string
    user_id: str # Expose user_id as string
    linkedin_job_id: Optional[str] = None
    status_history: List[StatusHistory] = []
    documents: List[Document] = []
    contacts: List[Contact] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # UPDATED from orm_mode