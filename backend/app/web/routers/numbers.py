from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.number_service import NumberService
from app.domain.entities import Number, User
from app.web.dependencies import get_current_user, get_number_service
from app.web.schemas import (
    NumberCreateRequest,
    NumberListResponse,
    NumberResponse,
    NumberUpdateRequest,
    StatsResponse,
)

router = APIRouter(tags=["numbers"])


def to_number_response(number: Number) -> NumberResponse:
    return NumberResponse(
        id=number.id,
        value=number.value,
        created_at=number.created_at,
        updated_at=number.updated_at,
    )


@router.post("/numbers", response_model=NumberResponse, status_code=status.HTTP_201_CREATED)
def create_number(
    request: NumberCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    number_service: Annotated[NumberService, Depends(get_number_service)],
) -> NumberResponse:
    number = number_service.create_number(current_user.id, request.value)
    return to_number_response(number)


@router.get("/numbers", response_model=NumberListResponse)
def list_numbers(
    current_user: Annotated[User, Depends(get_current_user)],
    number_service: Annotated[NumberService, Depends(get_number_service)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
) -> NumberListResponse:
    numbers, total = number_service.list_numbers(current_user.id, page, limit)
    return NumberListResponse(
        username=current_user.username,
        total=total,
        page=page,
        limit=limit,
        numbers=[to_number_response(number) for number in numbers],
    )


@router.get("/numbers/{number_id}", response_model=NumberResponse)
def get_number(
    number_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    number_service: Annotated[NumberService, Depends(get_number_service)],
) -> NumberResponse:
    number = number_service.get_number(current_user.id, number_id)
    return to_number_response(number)


@router.put("/numbers/{number_id}", response_model=NumberResponse)
def update_number(
    number_id: str,
    request: NumberUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    number_service: Annotated[NumberService, Depends(get_number_service)],
) -> NumberResponse:
    number = number_service.update_number(current_user.id, number_id, request.value)
    return to_number_response(number)


@router.delete("/numbers/{number_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_number(
    number_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    number_service: Annotated[NumberService, Depends(get_number_service)],
) -> None:
    number_service.delete_number(current_user.id, number_id)


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    number_service: Annotated[NumberService, Depends(get_number_service)],
) -> StatsResponse:
    stats = number_service.get_stats(current_user.id)
    return StatsResponse(**stats)
