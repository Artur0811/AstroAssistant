from django import forms
from .models import *

class RequestForm(forms.Form):
    name = forms.CharField(max_length=255)