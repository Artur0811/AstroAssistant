from django.urls import path

from WEBAstro.views import *

urlpatterns = [
    path("", main_page, name = "home"),
    path("about/", About,name = "about"),
    path("user/", User, name = "user_page"),
    path("login/", Login, name = "login_page"),
    path("request/", Star_Request, name="star_info"),
    path("register/", Register, name = "register")
]
