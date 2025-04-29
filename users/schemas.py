from ninja import Schema, ModelSchema
from pydantic import field_validator

from .models import User


class RegisterSchema(Schema):
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


class LoginSchemaOut(Schema):
    token: str


class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_instructor']
