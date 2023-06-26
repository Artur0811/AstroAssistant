from django.db import models

# Create your models here.

class Star(models.Model):
    star_name = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=50)
    star_type = models.CharField(max_length=10)
    other_names = models.CharField(max_length=500)
    magnitude = models.CharField(max_length=30)
    eclipse = models.CharField(max_length=30)
    light_curve = models.ImageField(upload_to="curve/%Y/%m/%d/")
    area_photo = models.ImageField(upload_to="area/%Y/%m/%d/")
    time_create = models.DateTimeField(auto_now=True)
    registered = models.BooleanField(default=False)

    def __str__(self):
        return self.star_name
