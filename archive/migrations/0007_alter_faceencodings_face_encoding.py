# Generated by Django 4.2 on 2023-04-12 18:19

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0006_alter_faceencodings_face_encoding_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faceencodings',
            name='face_encoding',
            field=jsonfield.fields.JSONField(),
        ),
    ]
