from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, examples=["admin"])
    password: str = Field(min_length=1, examples=["1234"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class NumberCreateRequest(BaseModel):
    value: int = Field(gt=0, examples=[42])


class NumberUpdateRequest(BaseModel):
    value: int = Field(gt=0, examples=[100])


class NumberResponse(BaseModel):
    id: str
    value: int
    created_at: datetime
    updated_at: datetime


class NumberListResponse(BaseModel):
    username: str
    total: int
    page: int
    limit: int
    numbers: list[NumberResponse]


class StatsResponse(BaseModel):
    total: int
    sum: int
    average: float | None
    maximum: int | None
    minimum: int | None


class ErrorResponse(BaseModel):
    detail: str
