# Generated by Django 2.1.7 on 2019-03-29 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20190329_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='user_id',
            field=models.URLField(default=''),
        ),
    ]