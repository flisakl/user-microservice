from ninja import Schema, ModelSchema, FilterSchema, Field
from pydantic import field_validator

from .models import User


class RegisterSchema(Schema):
    first_name: str | None = None
    last_name: str | None = None
    username: str
    password: str
    is_instructor: bool | None = False

    @field_validator('username', mode='after')
    @classmethod
    def username_is_unique(cls, value: str) -> str:
        try:
            User.objects.get(username=value)
            raise ValueError('Username already taken')
        except User.DoesNotExist:
            return value


class LoginSchemaIn(Schema):
    username: str
    password: str


class TokenSchema(Schema):
    token: str


class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_instructor', 'first_name', 'last_name']


class UserFilterSchema(FilterSchema):
    username: str | None = Field(None, q='username__icontains')
    ids: list[int] | None = Field(None, q='pk__in')


class UserUpdateSchema(Schema):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
