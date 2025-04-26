from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from bson import ObjectId
from typing import Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class PyObjectId(ObjectId):
    """Custom type for handling MongoDB ObjectIDs properly in Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Define how to validate and serialize this type"""
        return core_schema.union_schema([
            # Try to validate as ObjectId directly
            core_schema.is_instance_schema(ObjectId),
            # If not, try to convert string to ObjectId
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate)
            ])
        ])
    
    @classmethod
    def validate(cls, value):
        """Convert string to ObjectId if possible"""
        if not ObjectId.is_valid(value):
            raise ValueError(f"Invalid ObjectId: {value}")
        return ObjectId(value)
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls, _schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Custom JSON schema generation for this type"""
        return handler.resolve_ref_schema(core_schema.str_schema())

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str
        }
    }

class User(UserBase):
    id: str # This should be string when exposing via API
    created_at: datetime

    class Config:
        from_attributes = True # UPDATED from orm_mode