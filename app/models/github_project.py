from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId
from app.models.user import PyObjectId

class GitHubProject(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    github_id: int
    name: str
    description: Optional[str] = None
    html_url: HttpUrl
    api_url: HttpUrl
    clone_url: Optional[str] = None
    homepage: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    default_branch: str = "main"
    readme_content: Optional[str] = None
    readme_url: Optional[str] = None
    last_commit_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            PyObjectId: str
        }

    def dict_for_mongodb(self):
        """Convert the model to a MongoDB-compatible dict"""
        data = self.dict(by_alias=True)
        
        # Convert HttpUrl to string
        if 'html_url' in data and hasattr(data['html_url'], '__str__'):
            data['html_url'] = str(data['html_url'])
        if 'api_url' in data and hasattr(data['api_url'], '__str__'):
            data['api_url'] = str(data['api_url'])
        
        return data

class GitHubProjectResponse(BaseModel):
    id: str
    user_id: str
    github_id: int
    name: str
    description: Optional[str] = None
    html_url: str
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    readme_content: Optional[str] = None
    last_commit_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True