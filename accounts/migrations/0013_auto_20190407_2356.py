# Generated by Django 2.1.7 on 2019-04-08 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20190403_0059'),
    ]

    operations = [
        
        migrations.AlterField(
            model_name='postvisibleto',
            name='user_url',
            field=models.URLField(default=''),
        ),
    ]