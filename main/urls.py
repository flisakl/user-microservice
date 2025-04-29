"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from users.api import router
from jwt.exceptions import ExpiredSignatureError

api = NinjaAPI()
api.add_router('/users', router)


@api.exception_handler(ExpiredSignatureError)
def on_expired_token(request, exc):
    return api.create_response(
        request,
        {"detail": "Token has expired"},
        status=401
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api.urls)
]
