from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(data: UserCreate, service: UserService = Depends(get_service)):
    """
    Create a new user.

    **Fields:**
    - **username**: unique, alphanumeric + underscores, 3-50 chars (auto-lowercased)
    - **email**: valid unique email address
    - **first_name** / **last_name**: 1-100 chars
    - **role**: `admin`, `user` (default), or `guest`
    - **active**: boolean, defaults to `true`

    **Example request:**
    ```
    POST /api/v1/users/
    {
        "username": "juan_perez",
        "email": "juan.perez@example.com",
        "first_name": "Juan",
        "last_name": "Perez",
        "role": "user"
    }
    ```

    **Possible errors:**
    - `409` — username or email already exists
    - `422` — invalid field value
    """
    return service.create_user(data)


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users",
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_service),
):
    """
    Returns a paginated list of all users with a total count.

    **Query parameters:**
    - **skip**: number of records to skip (default: 0)
    - **limit**: max records to return (default: 100)

    **Example request:**
    ```
    GET /api/v1/users/?skip=0&limit=10
    ```
    """
    return service.list_users(skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
)
def get_user(user_id: str, service: UserService = Depends(get_service)):
    """
    Retrieve a single user by their UUID.

    **Example request:**
    ```
    GET /api/v1/users/3fa85f64-5717-4562-b3fc-2c963f66afa6
    ```

    **Possible errors:**
    - `404` — user not found
    """
    return service.get_user(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
)
def update_user(
    user_id: str,
    data: UserUpdate,
    service: UserService = Depends(get_service),
):
    """
    Partially update a user. Only provided fields will be updated.

    **Example request:**
    ```
    PUT /api/v1/users/3fa85f64-5717-4562-b3fc-2c963f66afa6
    {
        "first_name": "Juan Carlos",
        "role": "admin"
    }
    ```

    **Possible errors:**
    - `404` — user not found
    - `409` — new username or email already taken
    - `422` — invalid field value
    """
    return service.update_user(user_id, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
def delete_user(user_id: str, service: UserService = Depends(get_service)):
    """
    Permanently delete a user by their UUID.

    **Example request:**
    ```
    DELETE /api/v1/users/3fa85f64-5717-4562-b3fc-2c963f66afa6
    ```

    **Possible errors:**
    - `404` — user not found
    """
    service.delete_user(user_id)
