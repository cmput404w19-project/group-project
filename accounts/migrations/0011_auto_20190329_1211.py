# Generated by Django 2.1.7 on 2019-03-29 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20190329_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendrequest',
            name='requestedBy_name',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='friendrequest',
            name='requestedBy_url',
            field=models.URLField(default=''),
        ),
    ]