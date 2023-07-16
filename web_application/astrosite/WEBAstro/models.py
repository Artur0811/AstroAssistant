from django.db import models

# Create your models here.
from django.urls import reverse

class Star(models.Model):
    star_name = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=50)
    star_type = models.CharField(max_length=10)
    other_names = models.CharField(max_length=500)
    magnitude = models.CharField(max_length=30)
    eclipse = models.CharField(max_length=30)
    period = models.CharField(max_length=30)
    epoch = models.CharField(max_length=30)
    light_curve = models.ImageField(upload_to="curve/%Y/%m/%d/")
    time_create = models.DateTimeField(auto_now=True)
    user_id = models.CharField(max_length=15)

    def __str__(self):
        return self.star_name

    def get_absolute_url(self):
        return reverse("star", kwargs ={"star_id":self.pk})

    def get_names(self):
        return self.other_names.split(";")

class Last_Stars(models.Model):
    star_name = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=50)
    star_type = models.CharField(max_length=10)
    other_names = models.CharField(max_length=500)
    magnitude = models.CharField(max_length=30)
    eclipse = models.CharField(max_length=30)
    period = models.CharField(max_length=30)
    epoch = models.CharField(max_length=30)
    light_curve = models.ImageField(upload_to="curve/%Y/%m/%d/")
    time_create = models.DateTimeField(auto_now=True)
    user_id = models.CharField(max_length=15)

    def __str__(self):
        return self.star_name

    def get_absolute_url(self):
        return reverse("star", kwargs={"star_id": self.pk})

    def get_names(self):
        return self.other_names.split(";")

class Remove_curve(models.Model):
    light_curve = models.ImageField(upload_to="curve/%Y/%m/%d/")
    time_create = models.DateTimeField(auto_now=True)

class TypeStarInfo(models.Model):
    star_type = models.CharField(max_length=30)
    mainclass = models.CharField(max_length=30)
    type_info = models.CharField(max_length=3000)
    light_curve = models.ImageField(upload_to="curve/%Y/%m/%d/", default=None)