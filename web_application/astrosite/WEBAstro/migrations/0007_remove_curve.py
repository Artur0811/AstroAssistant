# Generated by Django 3.2.19 on 2023-07-14 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEBAstro', '0006_last_stars'),
    ]

    operations = [
        migrations.CreateModel(
            name='Remove_curve',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('light_curve', models.ImageField(upload_to='curve/%Y/%m/%d/')),
            ],
        ),
    ]