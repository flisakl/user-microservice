from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from ninja import Router
from .auth import AuthBearer, generate_jwt

from . import models, schemas


router = Router()


@router.post("/register", response={201: schemas.LoginSchemaOut})
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


@router.post("/login", response={200: schemas.LoginSchemaOut, 401: dict})
def login(request, data: schemas.LoginSchemaIn):
    user = authenticate(username=data.username, password=data.password)
    if not user:
        return 401, {"detail": "Invalid credentials"}

    token = generate_jwt(user)
    user.jwt_token = token
    user.save()
    return {"token": token}


@router.get(
    "/regenerate-token",
    response=schemas.LoginSchemaOut,
    auth=AuthBearer()
)
def regenerate_token(request):
    try:
        payload = request.auth
        user = models.User.objects.get(id=payload["user_id"])
    except Exception:
        return 401, {"detail": "Invalid token"}

    token = generate_jwt(user)
    user.jwt_token = token
    user.save()
    return {"token": token}


@router.get(
    "/{int:user_id}",
    response=schemas.UserSchema,
    auth=AuthBearer()
)
def get_user(request, user_id: int):
    user = get_object_or_404(models.User, pk=user_id)
    return user
