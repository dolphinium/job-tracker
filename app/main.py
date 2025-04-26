from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import connect_to_mongodb, close_mongodb_connection
from app.api import auth, applications

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown():
    await close_mongodb_connection()

# Include API routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(applications.router, prefix=f"{settings.API_V1_STR}/applications", tags=["applications"])

@app.get("/")
async def root():
    return {"message": "Welcome to Job Tracker API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}