# Generated by Django 2.2.5 on 2019-09-11 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_auto_20190911_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='check',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
    ]