from django.urls import path

from WEBAstro.views import *

urlpatterns = [
    path("", main_page, name = "home"),
    path("about/", About,name = "about"),
    path("user/", User, name = "user_page"),
    path("login/", Login, name = "login_page"),
    path("register/", Register, name = "register"),
    path("AstroAssistant/", AstroAssistant ,name = "astroassistant"),
]
