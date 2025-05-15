from typing import List, Any, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body
from bson.objectid import ObjectId
from pydantic import BaseModel

from app.models.database import get_database
from app.models.application import Application, ApplicationCreate, ApplicationUpdate, ApplicationInDB, StatusHistory
from app.api.auth import get_current_user
from app.models.user import User
from app.services.linkedin_crawler import LinkedInCrawler
from app.services.gemini_service import GeminiService

router = APIRouter()
linkedin_crawler = LinkedInCrawler()
gemini_service = GeminiService()

class EmailGenerationRequest(BaseModel):
    project_ids: List[str]
    language: str = "english"

class EmailGenerationResponse(BaseModel):
    email_text: str

@router.post("/", response_model=Application)
async def create_application(
    application_in: ApplicationCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    db = get_database()
    
    # Log the creation attempt
    print(f"Attempting to create application for URL: {application_in.linkedin_url}")
    
    # Extract job details from LinkedIn
    job_details = await linkedin_crawler.get_job_details(str(application_in.linkedin_url))
    
    # Combine provided data with crawled data
    application_data = {**application_in.dict(), **job_details}
    
    # Create application object
    application = ApplicationInDB(
        **application_data,
        user_id=ObjectId(current_user.id),
        status_history=[
            StatusHistory(
                status=application_data.get("status", "Wishlist"),
                notes="Application created"
            )
        ]
    )
    
    # Use the new method that properly handles HttpUrl
    result = await db.applications.insert_one(application.dict_for_mongodb())
    
    print(f"Application created with ID: {result.inserted_id}")
    
    created_app = await db.applications.find_one({"_id": result.inserted_id})
    return _map_application_to_response(created_app)

@router.get("/", response_model=List[Application])
async def list_applications(
    current_user: User = Depends(get_current_user)
) -> Any:
    db = get_database()
    
    cursor = db.applications.find({"user_id": ObjectId(current_user.id)})
    applications = await cursor.to_list(length=100)  # Limit to 100 for now
    
    return [_map_application_to_response(app) for app in applications]

@router.get("/{application_id}", response_model=Application)
async def get_application(
    application_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    db = get_database()
    
    application = await db.applications.find_one({
        "_id": ObjectId(application_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return _map_application_to_response(application)

@router.put("/{application_id}", response_model=Application)
async def update_application(
    application_id: str,
    application_update: ApplicationUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    db = get_database()
    
    # Get existing application
    existing_app = await db.applications.find_one({
        "_id": ObjectId(application_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if not existing_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Prepare update data
    update_data = {k: v for k, v in application_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Add to status history if status changed
    if "status" in update_data and update_data["status"] != existing_app["status"]:
        status_history_entry = StatusHistory(
            status=update_data["status"],
            notes=f"Status changed from {existing_app['status']} to {update_data['status']}"
        )
        
        # Use $push to add to status_history array
        await db.applications.update_one(
            {"_id": ObjectId(application_id)},
            {"$push": {"status_history": status_history_entry.dict()}}
        )
    
    # Update application
    await db.applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": update_data}
    )
    
    # Get updated application
    updated_app = await db.applications.find_one({"_id": ObjectId(application_id)})
    return _map_application_to_response(updated_app)

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    db = get_database()
    
    # Check application exists and belongs to user
    existing_app = await db.applications.find_one({
        "_id": ObjectId(application_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if not existing_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Delete application
    await db.applications.delete_one({"_id": ObjectId(application_id)})

@router.post("/{application_id}/generate_email", response_model=EmailGenerationResponse)
async def generate_email(
    application_id: str,
    request: EmailGenerationRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate a personalized email for HR using the Gemini API,
    leveraging stored job descriptions and user-selected relevant projects.
    """
    db = get_database()
    
    # Validate language
    if request.language.lower() not in ["english", "turkish"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Language must be 'english' or 'turkish'"
        )
    
    # Get the application
    application = await db.applications.find_one({
        "_id": ObjectId(application_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if job description exists
    if not application.get("job_description"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application has no job description"
        )
    
    # Get the selected GitHub projects
    project_ids = [ObjectId(pid) for pid in request.project_ids]
    if not project_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one project must be selected"
        )
    
    cursor = db.github_projects.find({
        "_id": {"$in": project_ids},
        "user_id": ObjectId(current_user.id)
    })
    
    projects = await cursor.to_list(length=100)
    
    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching GitHub projects found"
        )
    
    # Prepare user info
    user_info = {
        "username": current_user.username,
        "email": current_user.email
    }
    
    # Generate the email
    email_text = await gemini_service.generate_email(
        job_description=application["job_description"],
        projects=projects,
        user_info=user_info,
        language=request.language.lower()
    )
    
    return EmailGenerationResponse(email_text=email_text)

def _map_application_to_response(app_dict: dict) -> Application:
    """Map MongoDB document to Pydantic model for response."""
    app_dict["id"] = str(app_dict["_id"])
    app_dict["user_id"] = str(app_dict["user_id"])
    return Application(**app_dict)
