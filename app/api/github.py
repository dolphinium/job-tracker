from typing import List, Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel
from bson.objectid import ObjectId
from datetime import datetime

from app.models.database import get_database
from app.models.github_project import GitHubProject, GitHubProjectResponse
from app.api.auth import get_current_user
from app.models.user import User
from app.services.github_service import GitHubService, RateLimitError

router = APIRouter()
github_service = GitHubService()


class UsernameRequest(BaseModel):
    username: str
    token: Optional[str] = None


class RateLimitResponse(BaseModel):
    limit: int
    remaining: int
    reset: str
    used: int
    error: Optional[str] = None


@router.post("/fetch", response_model=List[GitHubProjectResponse])
async def fetch_github_projects(
    data: UsernameRequest = Body(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Fetch GitHub projects for a username and store them in the database"""
    username = data.username
    github_token = data.token  # Optional token for higher rate limits

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub username is required"
        )

    db = get_database()

    try:
        # Fetch repositories from GitHub with token if provided
        repositories = await github_service.get_user_repositories(username, github_token)

        if not repositories:
            return []  # Return empty list instead of error if no repos found

        # Process and store repositories
        stored_projects = []
        for repo in repositories:
            try:
                # Get README content
                readme_content = await github_service.get_repository_readme(username, repo["name"], github_token)

                # Get latest commit date
                last_commit_date = await github_service.get_latest_commit_date(
                    username,
                    repo["name"],
                    repo.get("default_branch", "main"),
                    github_token
                )

                # Create project object
                project = GitHubProject(
                    user_id=ObjectId(current_user.id),
                    github_id=repo["id"],
                    name=repo["name"],
                    description=repo.get("description"),
                    html_url=repo["html_url"],
                    api_url=repo["url"],
                    clone_url=repo.get("clone_url"),
                    homepage=repo.get("homepage"),
                    language=repo.get("language"),
                    stars=repo.get("stargazers_count", 0),
                    forks=repo.get("forks_count", 0),
                    watchers=repo.get("watchers_count", 0),
                    open_issues=repo.get("open_issues_count", 0),
                    default_branch=repo.get("default_branch", "main"),
                    readme_content=readme_content,
                    readme_url=f"https://github.com/{username}/{repo['name']}/blob/{repo.get('default_branch', 'main')}/README.md" if readme_content else None,
                    last_commit_date=last_commit_date
                )

                # Check if project already exists
                existing_project = await db.github_projects.find_one({
                    "user_id": ObjectId(current_user.id),
                    "github_id": repo["id"]
                })

                if existing_project:
                    # Update existing project
                    await db.github_projects.update_one(
                        {"_id": existing_project["_id"]},
                        {"$set": project.dict_for_mongodb_update()}
                    )
                    project.id = existing_project["_id"]
                else:
                    # Insert new project
                    result = await db.github_projects.insert_one(project.dict_for_mongodb())
                    project.id = result.inserted_id

                stored_projects.append(project)
            except Exception as e:
                # Log error but continue with other repos
                print(
                    f"Error processing repository {repo.get('name', 'unknown')}: {str(e)}")

        # Convert to response models
        response_projects = []
        for project in stored_projects:
            project_dict = {
                "id": str(project.id),
                "user_id": str(project.user_id),
                "github_id": project.github_id,
                "name": project.name,
                "description": project.description,
                "html_url": str(project.html_url),
                "language": project.language,
                "stars": project.stars,
                "forks": project.forks,
                "readme_content": project.readme_content,
                "last_commit_date": project.last_commit_date,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            }
            response_projects.append(GitHubProjectResponse(**project_dict))

        return response_projects

    except RateLimitError as e:
        # Handle rate limit errors specifically
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": str(e),
                "rate_limit": {
                    "limit": e.limit,
                    "remaining": e.remaining,
                    "reset": e.reset_time.isoformat()
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch GitHub projects: {str(e)}"
        )


@router.get("/", response_model=List[GitHubProjectResponse])
async def list_github_projects(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all GitHub projects for the current user"""
    db = get_database()

    try:
        # Find all projects for the current user
        cursor = db.github_projects.find({
            "user_id": ObjectId(current_user.id)
        }).sort("last_commit_date", -1)  # Sort by most recent commit

        projects = await cursor.to_list(length=100)

        # Convert to response models
        response_projects = []
        for project in projects:
            project["id"] = str(project["_id"])
            project["user_id"] = str(project["user_id"])
            project["html_url"] = str(project["html_url"])
            response_projects.append(GitHubProjectResponse(**project))

        return response_projects

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list GitHub projects: {str(e)}"
        )


@router.get("/rate-limit", response_model=RateLimitResponse)
async def get_github_rate_limit(
    token: str = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current GitHub API rate limit information"""
    try:
        return await github_service.get_rate_limit_info(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rate limit info: {str(e)}"
        )
