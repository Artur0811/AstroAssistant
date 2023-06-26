from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound


# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView
from WEBAstro.forms import *

menu = [{"title":"О сайте", "url":"about"},
]

star_type = sorted(['ACEP', 'ACV', 'ACYG', 'AHB1', 'AM', 'BCEP', 'BCEPS', 'BE', 'BLAP', 'BXCIR', 'BY',
                                           'CBSS', 'CBSS/V', 'CEP', 'CTTS', 'CTTS/ROT', 'CW', 'CWA', 'CWB', 'CWB(B)', 'CWBS', 'DCEP',
                                           'DCEP(B)', 'DCEPS', 'DCEPS(B)', 'DPV', 'DQ', 'DQ/AE', 'DSCT', 'DSCTC', 'DWLYN', 'DYPer',
                                           'E', 'EA', 'EB', 'ELL', 'EP', 'EW', 'EXOR', 'FF', 'FKCOM', 'FSCMa', 'FUOR', 'GCAS', 'GDOR',
                                           'HADS', 'HADS(B)', 'HB', 'HMXB', 'I', 'IA', 'IB', 'IBWD', 'IMXB', 'IN', 'INA', 'INAT', 'INB',
                                           'INS', 'INSA', 'INSB', 'INST', 'INT', 'IS', 'ISA', 'ISB', 'L', 'LB', 'LC', 'LERI', 'LMXB', 'M',
                                           'N', 'NA', 'NB', 'NC', 'NL', 'NL/VY', 'NR', 'PPN', 'PSR', 'PVTEL', 'PVTELI', 'PVTELII', 'PVTELIII',
                                           'R', 'RCB', 'ROT', 'RR', 'RRAB', 'RRC', 'RRD', 'RS', 'RV', 'RVA', 'RVB', 'SDOR', 'SN', 'SN I', 'SN II',
                                           'SN II-L', 'SN II-P', 'SN IIa', 'SN IIb', 'SN IId', 'SN IIn', 'SN Ia', 'SN Ia-CSM', 'SN Iax', 'SN Ib', 'SN Ic',
                                           'SN Ic-BL', 'SN-pec', 'SPB', 'SPBe', 'SR', 'SRA', 'SRB', 'SRC', 'SRD', 'SRS', 'SXARI', 'SXARI/E', 'SXPHE', 'SXPHE(B)',
                                           'TTS', 'TTS/ROT', 'UG', 'UGER', 'UGSS', 'UGSU', 'UGWZ', 'UGZ', 'UGZ/IW', 'UV', 'UVN',
                                           'UXOR', 'V1093HER', 'V361HYA', 'V838MON', 'WDP', 'WR', 'WTTS', 'WTTS/ROT', 'X', 'ZAND',
                                           'ZZ', 'ZZ/GWLIB', 'ZZA', 'ZZA/O', 'ZZB', 'ZZLep', 'ZZO', 'cPNB[e]', 'roAm', 'roAp'])

def main_page(request):
    return render(request, "WEBAstro/main_page.html", {"menu": menu, "title":"Главная страница", "star_type":star_type})

def PageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")

def About(request):
    return render(request, "WEBAstro/about.html", {"menu": menu, "title":"О программе", "about":"Тут будет текст о программе"})

def User(request):
    return render(request, "WEBAstro/user.html", {"menu": menu, "title":"Пользователь"})

def Login(request):
    return render(request, "WEBAstro/login.html", {"menu": menu, "title":"Пользователь"})

def Register(request):
    return render(request, "WEBAstro/register.html", {"menu": menu, "title":"Пользователь"})

def Star_Request(request):
    form = RequestForm()
    return render(request, "WEBAstro/result.html", {"form": form, "menu": menu, "title":"Главная страница", "star_type":star_type})



class RegisterUser(CreateView):
    form_class = UserCreationForm
    tempfile_name = "WEBAstro/register.html"
    success_url = reverse_lazy("login_page")



