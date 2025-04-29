from ninja.security import HttpBearer
from ninja.errors import AuthenticationError
from django.utils import timezone
from django.conf import settings
import jwt

from . import models


def generate_jwt(user: models.User) -> str:
    today = timezone.datetime.now()
    payload = {
        "id": user.pk,
        "username": user.username,
        "is_instructor": user.is_instructor,
        "exp": today + timezone.timedelta(hours=settings.TOKEN_TTL),
        "iat": today
    }
    return jwt.encode(payload, settings.RSA_PRIVATE_KEY, algorithm="RS256")


def decode_jwt(token: str, check_expiration: bool = True) -> dict:
    return jwt.decode(
        token, settings.RSA_PUBLIC_KEY, algorithms=["RS256"],
        options={
            'verify_exp': check_expiration,
        }
    )


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token:
            try:
                decoded = decode_jwt(token)
                return decoded
            except jwt.exceptions.ExpiredSignatureError:
                raise AuthenticationError(401, "Token has expired")
            except jwt.exceptions.DecodeError:
                raise AuthenticationError(401, "Invalid token")
