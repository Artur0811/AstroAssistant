import datetime
from io import StringIO

from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound


# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView

from WEBAstro.astoprogramm import *
from WEBAstro.forms import *

import os

from astrosite.settings import MEDIA_ROOT

menu = [
    {"title":"О сайте", "url":"about"},
    {"title":"Приложение", "url":"astroassistant"},
    {"title": "Типы переменных звёзд", "url": "startypes"}
]


def main_page(request):
    if request.method == "POST":
        if request.POST.get("req"):
            form = RequestForm(request.POST)
            if form.is_valid():
                values = form.cleaned_data

                o = OtherName(values["coordinates"])
                o_names = o.getname()
                periodic, maximum = is_periodic(values["star_type_value"])
                name = values["name"]
                ztf = ZTF_Points(values["coordinates"]).points()
                r_data = ztf['ZTF r']
                g_data = ztf['ZTF g']
                magn = ztf['magn']
                eclipse = None
                if r_data != [] or g_data != []:
                    per, epoch = None, None
                    if periodic:
                        per, epoch = Lafler_clinman(max(r_data, g_data, key=lambda x: len(x)), maximum)
                        r_data = make_LightCurve_with_per(r_data, per, epoch)
                        g_data = make_LightCurve_with_per(g_data, per, epoch)
                        if not maximum:
                            eclipse = eclipse_percent(max(r_data, g_data, key=lambda x: len(x)))
                    data_light = []
                    if r_data != []:
                        data_light.append([r_data, "ZTF r"])
                    if g_data != []:
                        data_light.append([g_data, "ZTF g"])
                    grf = makeGrapf(data_light, name, periodic).make()

                tame = datetime.date.today()
                save_dir = os.path.join(MEDIA_ROOT, "curve\{}\{}\{}".format(tame.year, tame.month, tame.day))
                if not os.path.exists(os.path.join(MEDIA_ROOT, "curve\{}\{}\{}".format(tame.year, tame.month, tame.day))):
                    os.makedirs(os.path.join(MEDIA_ROOT, "curve\{}\{}\{}".format(tame.year, tame.month, tame.day)))
                num_files = len([f for f in os.listdir(save_dir)
                                 if os.path.isfile(os.path.join(save_dir, f))])
                curve_name=values["coordinates"][0:5].replace(" ","")+str(tame.year)+values["name"][1:5].replace(" ","")+str(tame.month)+values["coordinates"][7:13].replace(" ","")+str(num_files)+".png"
                curve_name = curve_name.replace("+","")
                grf.savefig(os.path.join(save_dir, curve_name))
                grf.close()
                curve_path = "media/curve/{}/{}/{}/{}".format(tame.year, tame.month, tame.day, curve_name)

                data = {
                    "form": form,
                    "menu": menu,
                    "title":"Главная страница",
                    "values":values,
                    "curve":curve_path,
                    "names":o_names,
                    "period":per,
                    "epoch":epoch,
                    "magn":magn,
                    "eclipse":eclipse,
                    "show_btn": True,
                }

                if request.user.is_authenticated:
                    last_star = Last_Stars()
                    last_star.user_id = request.user.id
                    last_star.star_name = values["name"]
                    last_star.coordinates = values["coordinates"]
                    last_star.star_type = values['star_type_value']
                    last_star.light_curve = curve_path[6:]
                    last_star.other_names = ";".join(o_names)
                    last_star.magnitude = magn["min"] + " " + magn["max"]
                    if per:
                        last_star.period = per
                        last_star.epoch = epoch
                        if eclipse:
                            last_star.eclipse = eclipse
                    last_star.save()
                else:
                    rem = Remove_curve()
                    rem.light_curve = curve_path

                return render(request, "WEBAstro/result.html", data)
            else:
                print("errrrrr")
        else:
            star_info = request.POST.get("save").split(";")
            values = {"name": star_info[0], "coordinates": star_info[1], 'star_type_value':star_info[2]}
            form = RequestForm(values)
            o_names = star_info[5][2:-2].split("', '")
            data = {
                "form": form,
                "menu": menu,
                "title": "Главная страница",
                "values": values,
                "curve": star_info[-1],
                "names": o_names,
                "show_btn": False,
            }
            data["magn"] = {"min":star_info[3], "max":star_info[4]}
            if star_info[6] == "None":
                data["period"] = None
                data["epoch"] = None
            else:
                data["period"] = star_info[6]
                data["epoch"] = star_info[7]
            if star_info[8] == "None":
                data["eclipse"] = None
            else:
                data["eclipse"] = star_info[8]
            star = Star()
            star.star_name = star_info[0]
            star.coordinates = star_info[1]
            star.star_type = star_info[2]
            star.light_curve = star_info[-1][6:]
            star.magnitude = star_info[3]+' ' + star_info[4]
            star.other_names = ";".join(o_names)
            if data["period"]:
                star.period = data["period"]
                star.epoch = data["epoch"]
            if data["eclipse"]:
                star.eclipse = data["eclipse"]
            star.user_id = request.user.id
            star.save()
            return render(request, "WEBAstro/result.html", data)
    else:
        form = RequestForm()
    return render(request, "WEBAstro/main_page.html", {"form": form, "menu": menu, "title":"Главная страница", "star_type":star_type})

def PageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")

def About(request):
    text = """В астрономии есть множество направлений исследований и одно из них - изучение переменных звезд. Сайт разработан для быстрого сбора необходимой информации о переменных звездах.
    
            Пользователю необходимо ввести координаты звезды, дать ей название, правильно определить тип переменности и нажать кнопку обработать. Программа соберет информацию и выведет:
             1. График изменения яркости звезды (У определённых типов переменных это фазовый график)
             2. Магнитуду изменения яркости
             3. Обозначения этой звезды в различных каталогах
             
             Также для некоторых типов переменных звезд будет выводиться дополнительная информация:
             1. Период и эпоха для периодических переменных.
             2. Доля затмения для двойных систем, компоненты которой периодически затмевают друг друга.
             
             Для построения графиков и определения магнитуды используются данные наблюдений ZTF(Zwicky Transient Facility). Обозначения звезды в каталогах из общего каталога Vizier.
             
             При регистрации на сайте вы сможете сохранять свои запросы и просматривать последние.
             """
    return render(request, "WEBAstro/about.html", {"menu": menu, "title":"О сайте", "about":text})

def User(request):
    if request.method == "POST":
        del_star = Star.objects.filter(pk=request.POST.get("del_btn"))[0]
        rem = Remove_curve()
        rem.light_curve = del_star.light_curve
        rem.save()
        del_star.delete()
    stars = Star.objects.filter(user_id = request.user.id)
    last = Last_Stars.objects.filter(user_id = request.user.id)[::-1]
    while len(last)>3:
        rem = Remove_curve()
        rem.light_curve = last[-1].light_curve
        rem.save()
        last_star = last[-1]
        last_star.delete()
        last = last[:-1]
    return render(request, "WEBAstro/user.html", {"menu": menu, "title":"Пользователь", "stars":stars, "last":last})


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
        values = dict(list(context.items()))
        values["menu"] = menu
        return values

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = "WEBAstro/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        values = dict(list(context.items()))
        values["menu"] = menu
        return values

    def get_success_url(self):
        return reverse_lazy("home")

def Logout(request):
    logout(request)
    return redirect("login_page")



def Star_type_info(request):
#     types_text = """
# X-RAY
#
# HMXB
# Двойные рентгеновские снимки большой массы. Системы с массивной звездой (обычно звездой O или B, звездой Be или голубым сверхгигантом) и компактным объектом (обычно нейтронной звездой, черной дырой или белым карликом). Часть звездного ветра обычной звезды улавливается компактным объектом и производит рентгеновские лучи, когда они падают на него или на окружающий его аккреционный диск. В двоичных файлах рентгеновского излучения подтипы указывают, какой тип поведения отображает двоичный файл, например, рентгеновские всплески (XB), вспышки большой амплитуды также в визуальном (XN), эффект отражения (XR) или это также может информировать о природе объекта, например: если компактный объект является пульсаром (XP). Обратитесь к приведенному ниже списку подтипов.
#
# IMXB
# Рентгеновские двойные системы средней массы. Двойные системы, в которых компактный объект – черная дыра (BH), нейтронная звезда (NS) или белый карлик (WD) – накапливает вещество от звезды-компаньона спектрального типа A или F. IMXBS наблюдаются редко, потому что, когда компаньон массивнее аккретора, но недостаточно массивен, чтобы иметь сильные ветры, ветровая аккреция протекает с очень низкой скоростью, и считается, что аккреция лепестка Роша нестабильна. Для NSs и WDs в IMXBs масса перетекает от более массивной звезды к более легкой, а сохранение углового момента сокращает орбиту, что приводит к усилению массопереноса. Таким образом, яркая рентгеновская фаза является интенсивной и недолговечной.
#
# LMXB
# Рентгеновские двойные системы малой массы. Системы, в которых одним из компонентов является либо черная дыра, либо нейтронная звезда. Другой, донорский, компонент обычно заполняет его лепесток Роша и, следовательно, передает массу компактному объекту. Донором может быть обычный карлик, белый карлик или эволюционировавшая звезда (красный гигант). Рентгеновские лучи испускаются, когда масса падает на компактный объект или на окружающий его аккреционный диск. Рентгеновское излучение попадает в атмосферу более холодного спутника компактного объекта и переизлучается в виде оптического высокотемпературного излучения (эффект отражения), таким образом, придавая этой области поверхности более холодного спутника более ранний спектральный тип. Эти эффекты приводят к довольно своеобразному сложному характеру оптической изменчивости в таких системах. В двоичных файлах рентгеновского излучения подтипы указывают, какой тип поведения отображает двоичный файл, например, рентгеновские всплески (XB), всплески большой амплитуды также в визуальном (XN), эффект отражения (XR) или это также может информировать о природе объекта, например: если компактный объект является пульсар (XP). Обратитесь к приведенному ниже списку подтипов.
#
# X
# Источники сильного переменного рентгеновского излучения, которые не принадлежат или пока не отнесены ни к какому другому типу переменных звезд. Большинство переменных типа X оказываются двоичными системами типа HMXB, IMXB, LMXB, AM или DQ. Подтипы систем HMXB и LMXB перечислены в разделе подтипы.
# """.split("\n")[:-1]
#     i = 2
#     text = ""
#     typy_is = ""
#     while i < len(types_text):
#         if types_text[i].strip() == "":
#             if text != "":
#                 # print(types_text[1])
#                 # print(typy_is, "is_type")
#                 # print(text, "is_text")
#                 type_star = TypeStarInfo()
#                 type_star.mainclass = types_text[1]
#                 type_star.star_type = typy_is
#                 type_star.type_info = text
#                 type_star.save()
#                 text = ""
#             typy_is = types_text[i+1].strip()
#             i+=2
#         text+=types_text[i]
#         i+=1
#     type_star = TypeStarInfo()
#     type_star.star_type = typy_is
#     type_star.type_info = text
#     type_star.mainclass = types_text[1]
#     type_star.save()
    type_star = TypeStarInfo.objects.all()
    type_star = sorted(type_star, key=lambda x: x.star_type)
    return render(request, "WEBAstro/startypeinfo.html", {"menu":menu, "star_types": type_star, "title":"Звезды"})



