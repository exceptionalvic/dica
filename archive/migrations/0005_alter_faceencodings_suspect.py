# Generated by Django 4.2 on 2023-04-12 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0004_alter_suspect_nationality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faceencodings',
            name='suspect',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='suspect_face_encodings', to='archive.suspect'),
        ),
    ]
