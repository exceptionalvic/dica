# Generated by Django 4.2 on 2023-04-17 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0008_alter_faceencodings_suspect'),
    ]

    operations = [
        migrations.AddField(
            model_name='suspect',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]