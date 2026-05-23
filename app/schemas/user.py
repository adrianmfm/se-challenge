from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import UserRole


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.user
    active: bool = True

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "juan_perez",
                    "email": "juan.perez@example.com",
                    "first_name": "Juan",
                    "last_name": "Perez",
                    "role": "user",
                    "active": True,
                }
            ]
        }
    }

    @field_validator("username")
    @classmethod
    def username_lowercase(cls, v: str) -> str:
        return v.lower()


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    active: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "Juan Carlos",
                    "role": "admin",
                    "active": False,
                }
            ]
        }
    }

    @field_validator("username")
    @classmethod
    def username_lowercase(cls, v: Optional[str]) -> Optional[str]:
        return v.lower() if v else v


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "username": "juan_perez",
                    "email": "juan.perez@example.com",
                    "first_name": "Juan",
                    "last_name": "Perez",
                    "role": "user",
                    "active": True,
                    "created_at": "2026-05-22T10:00:00Z",
                    "updated_at": "2026-05-22T10:00:00Z",
                }
            ]
        },
    }


class UserListResponse(BaseModel):
    total: int
    users: list[UserResponse]
