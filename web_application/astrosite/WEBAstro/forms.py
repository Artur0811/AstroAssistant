from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .astoprogramm import is_coord,is_name
from .models import *

star_type = (('ACEP', 'ACEP'), ('ACV', 'ACV'), ('ACYG', 'ACYG'), ('AHB1', 'AHB1'), ('AM', 'AM'), ('BCEP', 'BCEP'), ('BCEPS', 'BCEPS'), ('BE', 'BE'), ('BLAP', 'BLAP'), ('BXCIR', 'BXCIR'), ('BY', 'BY'), ('CBSS', 'CBSS'), ('CBSS/V', 'CBSS/V'), ('CEP', 'CEP'), ('CTTS', 'CTTS'), ('CTTS/ROT', 'CTTS/ROT'), ('CW', 'CW'), ('CWA', 'CWA'), ('CWB', 'CWB'), ('CWB(B)', 'CWB(B)'), ('CWBS', 'CWBS'), ('DCEP', 'DCEP'), ('DCEP(B)', 'DCEP(B)'), ('DCEPS', 'DCEPS'), ('DCEPS(B)', 'DCEPS(B)'), ('DPV', 'DPV'), ('DQ', 'DQ'), ('DQ/AE', 'DQ/AE'), ('DSCT', 'DSCT'), ('DSCTC', 'DSCTC'), ('DWLYN', 'DWLYN'), ('DYPer', 'DYPER'), ('E', 'E'), ('EA', 'EA'), ('EB', 'EB'), ('ELL', 'ELL'), ('EP', 'EP'), ('EW', 'EW'), ('EXOR', 'EXOR'), ('FF', 'FF'), ('FKCOM', 'FKCOM'), ('FSCMa', 'FSCMA'), ('FUOR', 'FUOR'), ('GCAS', 'GCAS'), ('GDOR', 'GDOR'), ('HADS', 'HADS'), ('HADS(B)', 'HADS(B)'), ('HB', 'HB'), ('HMXB', 'HMXB'), ('I', 'I'), ('IA', 'IA'), ('IB', 'IB'), ('IBWD', 'IBWD'), ('IMXB', 'IMXB'), ('IN', 'IN'), ('INA', 'INA'), ('INAT', 'INAT'), ('INB', 'INB'), ('INS', 'INS'), ('INSA', 'INSA'), ('INSB', 'INSB'), ('INST', 'INST'), ('INT', 'INT'), ('IS', 'IS'), ('ISA', 'ISA'), ('ISB', 'ISB'), ('L', 'L'), ('LB', 'LB'), ('LC', 'LC'), ('LERI', 'LERI'), ('LMXB', 'LMXB'), ('M', 'M'), ('N', 'N'), ('NA', 'NA'), ('NB', 'NB'), ('NC', 'NC'), ('NL', 'NL'), ('NL/VY', 'NL/VY'), ('NR', 'NR'), ('PPN', 'PPN'), ('PSR', 'PSR'), ('PVTEL', 'PVTEL'), ('PVTELI', 'PVTELI'), ('PVTELII', 'PVTELII'), ('PVTELIII', 'PVTELIII'), ('R', 'R'), ('RCB', 'RCB'), ('ROT', 'ROT'), ('RR', 'RR'), ('RRAB', 'RRAB'), ('RRC', 'RRC'), ('RRD', 'RRD'), ('RS', 'RS'), ('RV', 'RV'), ('RVA', 'RVA'), ('RVB', 'RVB'), ('SDOR', 'SDOR'), ('SN', 'SN'), ('SN I', 'SN I'), ('SN II', 'SN II'), ('SN II-L', 'SN II-L'), ('SN II-P', 'SN II-P'), ('SN IIa', 'SN IIA'), ('SN IIb', 'SN IIB'), ('SN IId', 'SN IID'), ('SN IIn', 'SN IIN'), ('SN Ia', 'SN IA'), ('SN Ia-CSM', 'SN IA-CSM'), ('SN Iax', 'SN IAX'), ('SN Ib', 'SN IB'), ('SN Ic', 'SN IC'), ('SN Ic-BL', 'SN IC-BL'), ('SN-pec', 'SN-PEC'), ('SPB', 'SPB'), ('SPBe', 'SPBE'), ('SR', 'SR'), ('SRA', 'SRA'), ('SRB', 'SRB'), ('SRC', 'SRC'), ('SRD', 'SRD'), ('SRS', 'SRS'), ('SXARI', 'SXARI'), ('SXARI/E', 'SXARI/E'), ('SXPHE', 'SXPHE'), ('SXPHE(B)', 'SXPHE(B)'), ('TTS', 'TTS'), ('TTS/ROT', 'TTS/ROT'), ('UG', 'UG'), ('UGER', 'UGER'), ('UGSS', 'UGSS'), ('UGSU', 'UGSU'), ('UGWZ', 'UGWZ'), ('UGZ', 'UGZ'), ('UGZ/IW', 'UGZ/IW'), ('UV', 'UV'), ('UVN', 'UVN'), ('UXOR', 'UXOR'), ('V1093HER', 'V1093HER'), ('V361HYA', 'V361HYA'), ('V838MON', 'V838MON'), ('WDP', 'WDP'), ('WR', 'WR'), ('WTTS', 'WTTS'), ('WTTS/ROT', 'WTTS/ROT'), ('X', 'X'), ('ZAND', 'ZAND'), ('ZZ', 'ZZ'), ('ZZ/GWLIB', 'ZZ/GWLIB'), ('ZZA', 'ZZA'), ('ZZA/O', 'ZZA/O'), ('ZZB', 'ZZB'), ('ZZLep', 'ZZLEP'), ('ZZO', 'ZZO'), ('cPNB[e]', 'CPNB[E]'), ('roAm', 'ROAM'), ('roAp', 'ROAP'))


class RequestForm(forms.Form):
    name = forms.CharField(max_length=255, label="Название звезды", validators=[is_name])
    coordinates = forms.CharField(max_length=255, label="Координаты звезды", validators=[is_coord])
    star_type_value = forms.ChoiceField(choices =star_type, label="Тип звезды")

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput())
    # email = forms.CharField(label="Почта")
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput())


    class Meta:
        model = User
        fields = ("username",  "password1", "password2")#"email",
        widgets = {
            "username": forms.TextInput(),
            "password1": forms.PasswordInput(),
            "password2": forms.PasswordInput(),
        }

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput())
    password = forms.CharField(label="Пароль", widget= forms.PasswordInput())