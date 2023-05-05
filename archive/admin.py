from django.contrib import admin
from .models import FaceEncodings, Suspect, Intelligence

admin.site.register(FaceEncodings)
admin.site.register(Suspect)
admin.site.register(Intelligence)
