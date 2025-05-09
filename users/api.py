from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from ninja import Router, Query
from .auth import generate_jwt, decode_jwt, AuthBearer

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
    user.first_name = data.first_name
    user.last_name = data.last_name
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


@router.get("", response=list[schemas.UserSchema])
def get_users(request, filters: schemas.UserFilterSchema = Query(...)):
    qs = models.User.objects.all()
    return filters.filter(qs)


@router.patch("", response=schemas.UserSchema, auth=AuthBearer())
def update_user(request, data: schemas.UserUpdateSchema):
    usr = get_object_or_404(models.User, pk=request.auth['id'])

    for attr, value in data.dict(exclude_unset=True).items():
        setattr(usr, attr, value)
    usr.save()

    return usr


@router.delete("", response={204: None}, auth=AuthBearer())
def delete_user(request):
    usr = get_object_or_404(models.User, pk=request.auth['id'])

    usr.delete()

    return 204, None
