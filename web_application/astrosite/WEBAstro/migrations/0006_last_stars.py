# Generated by Django 3.2.19 on 2023-07-14 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEBAstro', '0005_auto_20230707_0048'),
    ]

    operations = [
        migrations.CreateModel(
            name='Last_Stars',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('star_name', models.CharField(max_length=255)),
                ('coordinates', models.CharField(max_length=50)),
                ('star_type', models.CharField(max_length=10)),
                ('other_names', models.CharField(max_length=500)),
                ('magnitude', models.CharField(max_length=30)),
                ('eclipse', models.CharField(max_length=30)),
                ('period', models.CharField(max_length=30)),
                ('epoch', models.CharField(max_length=30)),
                ('light_curve', models.ImageField(upload_to='curve/%Y/%m/%d/')),
                ('time_create', models.DateTimeField(auto_now=True)),
                ('user_id', models.CharField(max_length=15)),
            ],
        ),
    ]
