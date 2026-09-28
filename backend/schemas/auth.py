from pydantic import BaseModel, Field

from .user import UserResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(TokenResponse):
    user: UserResponse


class CurrentUserResponse(UserResponse):
    pass
