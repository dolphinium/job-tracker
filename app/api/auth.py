from datetime import timedelta
from typing import Any
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings
from app.models.database import get_database
from app.models.user import User, UserCreate, UserInDB
from app.utils.security import verify_password, get_password_hash, create_access_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str = None

async def get_user_by_email(email: str) -> UserInDB:
    db = get_database()
    user_data = await db.users.find_one({"email": email})
    if user_data:
        return UserInDB(**user_data)
    return None

async def authenticate_user(email: str, password: str) -> UserInDB:
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    db = get_database()
    user_data = await db.users.find_one({"_id": ObjectId(user_id)})
    if user_data is None:
        raise credentials_exception
    
    user = UserInDB(**user_data)
    return User(
        id=str(user.id),
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )

@router.post("/register", response_model=User)
async def register_user(user_in: UserCreate) -> Any:
    db = get_database()
    
    # Check if email already exists
    existing_user = await db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = await db.users.find_one({"username": user_in.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    user_data = UserInDB(
        **user_in.dict(),
        password_hash=get_password_hash(user_in.password)
    )
    
    result = await db.users.insert_one(user_data.dict(by_alias=True))
    
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return User(
        id=str(created_user["_id"]),
        username=created_user["username"],
        email=created_user["email"],
        created_at=created_user["created_at"]
    )

@router.post("/login", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    return current_user