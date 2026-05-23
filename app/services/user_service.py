from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserListResponse
from app.core.logging import logger


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_user(self, user_id: str) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> UserListResponse:
        users, total = self.repo.get_all(skip=skip, limit=limit)
        return UserListResponse(total=total, users=users)

    def create_user(self, data: UserCreate) -> User:
        if self.repo.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{data.username}' is already taken",
            )
        if self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{data.email}' is already registered",
            )
        user = self.repo.create(data)
        logger.info("Created user id=%s username=%s", user.id, user.username)
        return user

    def update_user(self, user_id: str, data: UserUpdate) -> User:
        user = self.get_user(user_id)

        if data.username and data.username != user.username:
            if self.repo.get_by_username(data.username):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Username '{data.username}' is already taken",
                )

        if data.email and data.email != user.email:
            if self.repo.get_by_email(data.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{data.email}' is already registered",
                )

        updated = self.repo.update(user, data)
        logger.info("Updated user id=%s", user_id)
        return updated

    def delete_user(self, user_id: str) -> None:
        user = self.get_user(user_id)
        self.repo.delete(user)
        logger.info("Deleted user id=%s", user_id)
