# Generated by Django 3.2.19 on 2023-07-06 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEBAstro', '0004_remove_star_user_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='star',
            name='area_photo',
        ),
        migrations.RemoveField(
            model_name='star',
            name='registered',
        ),
        migrations.AddField(
            model_name='star',
            name='user_id',
            field=models.CharField(default=3, max_length=15),
            preserve_default=False,
        ),
    ]
