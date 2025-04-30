from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from ninja import Router
from .auth import generate_jwt, decode_jwt

from . import models, schemas


router = Router()


@router.post("/register", response={201: schemas.TokenSchema})
def register(request, data: schemas.RegisterSchema):
    user = models.User.objects.create_user(
        username=data.username,
        password=data.password,
        is_instructor=data.is_instructor
    )
    token = generate_jwt(user)
    user.jwt_token = token
    user.save()
    return {"token": token}


@router.post("/login", response={200: schemas.TokenSchema, 401: dict})
def login(request, data: schemas.LoginSchemaIn):
    user = authenticate(username=data.username, password=data.password)
    if not user:
        return 401, {"detail": "Invalid credentials"}

    token = generate_jwt(user)
    user.jwt_token = token
    user.save()
    return {"token": token}


@router.post(
    "/regenerate-token",
    response=schemas.TokenSchema,
)
def regenerate_token(request, data: schemas.TokenSchema):
    payload = decode_jwt(data.token, False)
    user = models.User.objects.get(id=payload["id"])

    token = generate_jwt(user)
    user.jwt_token = token
    user.save()
    return {"token": token}


@router.get(
    "/{int:user_id}",
    response=schemas.UserSchema,
)
def get_user(request, user_id: int):
    user = get_object_or_404(models.User, pk=user_id)
    return user
