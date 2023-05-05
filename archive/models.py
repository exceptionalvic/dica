from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.html import mark_safe
import uuid
import random
import string
import numbers
from django_resized import ResizedImageField
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import face_recognition
from jsonfield import JSONField



def cida_frs_image_archive(instance, filename):
    file_extension = filename.split('.')[-1]
    file_name = str(instance.first_name)+' '+str(instance.last_name)+'-'+str(instance.crime_title)
    return f"{settings.CIDA_IMAGE_UPLOAD_PATH}/{file_name}.{file_extension}"

class Suspect(models.Model):
    GENDER = (
    ('MALE', 'male'),
    ('FEMALE', 'female'),
    ('NON-BINARY', 'non-binary')
    )
    STATUS = (
        ('MANHUNT','Manhunt'),
        ('INCARCERATED','incarcerated')
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()
    nationality = models.CharField(max_length=100, default='Nigerian')
    gender = models.CharField(max_length=15, choices=GENDER, default='MALE')
    suspect_status = models.CharField(max_length=100, choices=STATUS, default='MANHUNT')
    address_of_suspect = models.CharField(max_length=100)
    crime_title = models.CharField(max_length=255)
    crime_description = models.TextField()
    mugshot = ResizedImageField(size=[1200,630], upload_to=cida_frs_image_archive, blank=True, null=True)
    date_convicted = models.DateField(blank=True)
    name_of_law_court = models.CharField(max_length=255, help_text='name of court where suspect was arraigned')
    source = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created']
    
    def save(self, *args, **kwargs):
        if self.date_convicted:
            try:
                self.date_convicted = self.date_convicted.replace("/","-")
            except:
                self.date_convicted = self.date_convicted
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

@receiver(post_save, sender=Suspect)
def create_encoding(sender, instance, *args, **kwargs):
    if instance:
        format_image = str(instance.mugshot.url)
        split_img = format_image.split('/')
        # print(split_img)
        new_img = split_img[1]+'/'+split_img[2]+'/'+split_img[3]+'/'+split_img[4]
        s_image = face_recognition.load_image_file(new_img)
        s_image_encoding = face_recognition.face_encodings(s_image)[0]
        new_encoding = FaceEncodings(suspect=instance,face_encoding=s_image_encoding)
        try:
            get_encoding = FaceEncodings.objects.get(suspect=instance)
            pass
        except FaceEncodings.DoesNotExist:
            new_encoding.save()
        # FaceEncodings.objects.create

class FaceEncodings(models.Model):
    face_encoding = JSONField()
    suspect = models.OneToOneField(Suspect, on_delete=models.CASCADE, related_name='suspect_face_encodings')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.suspect}'
    


class Intelligence(models.Model):
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, related_name='suspect_detected')
    location_last_seen = models.TextField(help_text='location, coordinates and other details of location where suspect was detected')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f'{self.suspect} - seen on {self.date}'
    

