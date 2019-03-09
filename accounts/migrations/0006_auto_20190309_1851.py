# Generated by Django 2.1.7 on 2019-03-09 18:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_post_author_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='category',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='post',
            name='content',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='post',
            name='contentType',
            field=models.CharField(choices=[('text/markdown', 'text/markdown'), ('text/plain', 'text/plain'), ('image/png;base64', 'image/png;base64'), ('image/jpeg;base64', 'image/jpeg;base64')], default='text/plain', max_length=20),
        ),
        migrations.AddField(
            model_name='post',
            name='origin',
            field=models.URLField(default=''),
        ),
        migrations.AddField(
            model_name='post',
            name='publish_time',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='post',
            name='source',
            field=models.URLField(default=''),
        ),
        migrations.AddField(
            model_name='post',
            name='visibility',
            field=models.CharField(choices=[('PUBLIC', 'PUBLIC'), ('FOAF', 'FOAF'), ('FRIENDS', 'FRIENDS'), ('PRIVATE', 'PRIVATE'), ('SERVERONLY', 'SERVERONLY')], default='PUBLIC', max_length=20),
        ),
    ]