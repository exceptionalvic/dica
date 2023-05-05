from django.urls import path, include, re_path
from .views import *


urlpatterns = [
    path('', home, name='home'),
    # path('home/', home, name='home'),
    path('archive/add-new-suspect/', AddNewSuspect, name='add_new_suspect'),
    path('archive/start-stream/', StartVideoStream, name='start_stream'),
    path('archive/camera/', process, name='live_camera'),
    path('archive/stream/', Stream, name='stream'),
    path('archive/stream/stop-livestream/', StopStream, name='stop_stream'),
    path('archive/stream/idle/', IdleMode, name='idle_mode'),
]