from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound


# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView
from WEBAstro.forms import *

menu = [
    {"title":"О сайте", "url":"about"},
    {"title":"Приложение", "url":"astroassistant"},
]

def main_page(request):
    if request.method == "POST":
        form = RequestForm(request.POST)
        if form.is_valid():
            values = form.cleaned_data
            print(values)
            data = {
                "form": form,
                "menu": menu,
                "title":"Главная страница",
                "star_type":star_type,
                "values":values,
            }
            return render(request, "WEBAstro/result.html", data)
        else:
            print("errrrrr")
    else:
        form = RequestForm()

    return render(request, "WEBAstro/main_page.html", {"form": form, "menu": menu, "title":"Главная страница", "star_type":star_type})

def PageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")

def About(request):
    return render(request, "WEBAstro/about.html", {"menu": menu, "title":"О программе", "about":"Тут будет текст о программе"})

def User(request):
    stars = Star.objects.filter(user_id = request.user.id)
    return render(request, "WEBAstro/user.html", {"menu": menu, "title":"Пользователь", "stars":stars})

# def Login(request):
#     return render(request, "WEBAstro/login.html", {"menu": menu, "title":"Пользователь"})

# def Register(request):
#     return render(request, "WEBAstro/register.html", {"menu": menu, "title":"Пользователь"})

def AstroAssistant(request):
    text = """Это приложение является расширенной версией нашего сайта. Оно помогает собирать все необходимые данные для регистрации переменных звезд в каталог VSX (Variable Star Index https://www.aavso.org/vsx/index.php ) и реализует следующие возможности:
                \n  1.	Сбор данных для регистрации.
                2.	Обработка данных для построения графика изменения яркости звезды.
                3.	Составление цветного изображения из снимков неба.
                \n
                Для работы приложения необходимо:
                \n
                1. Стабильное подключение к интернету.
                2. 130 Мб места на жестком диске. Без учета файлов, которые создает программа.
                \n
                Программа создает регистрационные карты - папки, содержащие информацию о звезде в текстовом файле и график изменения яркости звезды. В среднем одина регистрационная карта весит 250 Кб."""
    return render(request, "WEBAstro/download.html", {"menu": menu, "title":"AstroAssistant", "load_text":text})


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "WEBAstro/register.html"
    success_url = reverse_lazy("login_page")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = "WEBAstro/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def get_success_url(self):
        return reverse_lazy("home")

def Logout(request):
    logout(request)
    return redirect("login_page")



