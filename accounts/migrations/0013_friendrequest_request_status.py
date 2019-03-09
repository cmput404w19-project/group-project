# Generated by Django 2.1.7 on 2019-03-09 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20190309_2029'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendrequest',
            name='request_status',
            field=models.CharField(choices=[('Accept', 'Accept'), ('Decline', 'Decline'), ('Pending', 'Pending')], default='Pending', max_length=20),
        ),
    ]