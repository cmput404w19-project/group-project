# Generated by Django 2.1.7 on 2019-03-27 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20190325_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalServer',
            fields=[
                ('server_url', models.URLField(primary_key=True, serialize=False)),
                ('user', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
            ],
        ),
    ]
