from django.shortcuts import render, redirect, HttpResponse
import numpy as np
from .models import FaceEncodings, Intelligence, Suspect
from .train import train_new_model
from .process import process
from django.contrib import messages
from django.views.decorators import gzip
from imutils.video import VideoStream
from imutils.video import FPS
import imutils
# from pygame import mixer
import cv2,os,urllib.request,pickle
import face_recognition
from django.conf import settings
import threading
from django.http import StreamingHttpResponse
import os
import base64
import sys
import urllib.request, urllib.parse, urllib.error
import json, socket
from werkzeug.utils import secure_filename
# Create your views here.
ALLOWED_EXTENSIONS = set(['txt','mp4','jpeg'])
# mixer.init()
# mixer.music.load("alarm.wav")

# try to get the hostname and Ip of where
host_name = socket.gethostname() 
host_ip = socket.gethostbyname(host_name) 
serviceurl = 'http://www.geoplugin.net/json.gp?ip='+host_ip

print('Retrieving', serviceurl)
uh = urllib.request.urlopen(serviceurl)
data = uh.read().decode()
print('Retrieved', len(data), 'characters')
js = json.loads(data)
print(data)

class VideoCamera(object):
    def __init__(self):
        self.vs = VideoStream(src=0).start()
		# start the FPS throughput estimator
        self.fps = FPS().start()
    
    def __del__(self):
        # self.video.release()
        self.vs.stop()
        # cv2.destroyAllWindows()

    def get_frame(self):
        known_face_encodings =[]
        known_face_names = []

        all_encoding = FaceEncodings.objects.all()
        for obj in all_encoding:
            known_face_encodings.append(obj.face_encoding)
            known_face_names.append(str(obj.suspect.first_name)+' '+str(obj.suspect.last_name))
        
        frame = self.vs.read()
        frame = cv2.flip(frame,1)
        frame = imutils.resize(frame, width=600)
        # (h, w) = frame.shape[:2]
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        process_this_frame = True
        
        
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame,  model='haar')
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        # Only process every other frame of video to save time
        if process_this_frame:
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                # # If a match was found in known_face_encodings, just use the first one.
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    if name:
                        try:
                            get_suspect = Suspect.objects.filter(first_name=str(name).split(" ")[0], last_name=str(name).split(" ")[1]).first()
                            print(get_suspect)
                            Intelligence.objects.create(suspect=get_suspect, location_last_seen=js)
                        except:
                            pass
                        # play alarm sound if face is recognized
                        # mixer.music.play()
                    

                face_names.append(name)
        process_this_frame = not process_this_frame
        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            # cv2.putText('press q on keyboard to close',(left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        # update the FPS counter
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.__del__(self)
                break
        # video_capture.release()
        # out.release()
        # cv2.destroyAllWindows()
        self.fps.update()
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

        # image = self.frame
        # _, jpeg = cv2.imencode('.jpg', image)
        # return jpeg.tobytes()
    
        # jpeg_base64 = base64.b64encode(jpeg.tostring())

        # return """
        # <html>
        # <head>
        # <meta http-equiv="refresh" content="1" />
        # <title>Cherrypy webcam</title>
        # </head>
        # <html>
        # <body>
        # <img src='data:image/jpeg;base64,%s' />
        # </body>
        # </html>
        # """ % (jpeg_base64, jpeg_base64)

    # def update(self):
    #     # while True:
    #     self.alarm = True
    #         (self.grabbed, self.frame) = self.video.read()
            
def StopStream(request):
    try:
        vs = VideoStream(src=0)
        vs.stream.stop()
        messages.success(request, 'Live camera stopped')
    except:
        pass
    return redirect('idle_mode')

def IdleMode(request):
    return render(request, 'archive/idle_mode.html')

def gen(camera):
    while True:
        # cv2.imencode('.jpg', image
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def home(request):
    all_suspect = Suspect.objects.filter(active=True)
    context = {
        'suspects': all_suspect
    }
    return render(request, 'archive/home.html', context)

def AddNewSuspect(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        address_of_suspect = request.POST.get('address')
        name_of_law_court = request.POST.get('court')
        crime_title = request.POST.get('crime_title')
        crime_description = request.POST.get('crime_desc')
        age = request.POST.get('age')
        date_convicted = request.POST.get('date')
        # nationality = request.POST.get('nationality')
        suspect_status = request.POST.get('status')
        source = request.POST.get('source')
        mugshot = request.FILES.get('image')

        new_suspect = Suspect(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            address_of_suspect=address_of_suspect,
            crime_title=crime_title,
            name_of_law_court=name_of_law_court,
            crime_description=crime_description,
            age=age,
            date_convicted=date_convicted,
            # nationality=nationality,
            suspect_status=suspect_status,
            source=source,
            mugshot=mugshot

        )
        new_suspect.save()
        messages.success(request, 'New suspect saved in archives')
        image_url = str(request.build_absolute_uri('/')[:-1]) + str(new_suspect.mugshot.url)
        # train_new_model(request,new_suspect)
    return render(request, 'archive/add_suspect.html')
        

def StartVideoStream(request):
    messages.success(request,'Video Stream Started')
    messages.info(request,'Video will display in 60 seconds')
    # alarm = VideoCamera.alarm
    # print(alarm)
    return render(request, 'archive/start-stream.html')

# @gzip.gzip_page
def Stream(request):
    cam = VideoCamera()
    # alarm = alarm
    return StreamingHttpResponse(gen(cam),content_type='multipart/x-mixed-replace; boundary=frame')
    # try:
    #     # cam = process()
    #     cam = VideoCamera()
    #     return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    #     # return """
    #     #     <html>
    #     #     <head>
    #     #     <meta http-equiv="refresh" content="1" />
    #     #     <title>Cherrypy webcam</title>
    #     #     </head>
    #     #     <html>
    #     #     <body>
    #     #     <img src='data:image/jpeg;base64,%s' />
    #     #     </body>
    #     #     </html>
    #     #     """ % (jpeg_base64, jpeg_base64)
    # except:
    #     pass
    # # process()
    # # stream_io = process()
    # return render(request, 'archive/stream.html')

# @gzip.gzip_page
def process(request):
    video_capture = cv2.VideoCapture(0)
    # video_capture = VideoCamera()
    length = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))


    # Create arrays of known face encodings and their names
    known_face_encodings =[]
    known_face_names = []

    all_encoding = FaceEncodings.objects.all()
    for obj in all_encoding:
        known_face_encodings.append(obj.face_encoding)
        known_face_names.append(str(obj.suspect.first_name)+' '+str(obj.suspect.last_name))

    width  = int(video_capture.get(3)) # float
    height = int(video_capture.get(4))
    fourcc = cv2.VideoWriter_fourcc(*'vp80')
    PATH = str(settings.VIDEO_PATH)+''.join("video.webm")
    out = cv2.VideoWriter(PATH,fourcc, fps, (width,height))

    for i in range(1,length-1):
        ret, frame = video_capture.read()
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            # check faces with smallest distance
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 10), (right, bottom + 10 ), (10, 10, 10), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 2, bottom), font, 0.4, (255, 255, 255), 1)

            sys.stdout.write(f"writing...{int((i/length)*100)+1}%")
            sys.stdout.flush()
            out.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    video_capture.release()
    out.release()
    cv2.destroyAllWindows()
    # return PATH

    
# def showstream(request):
#     # various performance tweaks
#     options = {
#         "frame_size_reduction": 40,
#         "jpeg_compression_quality": 80,
#         "jpeg_compression_fastdct": True,
#         "jpeg_compression_fastupsample": False,
#     }

#     # initialize WebGear app
#     # web = WebGear(source="foo.mp4", logging=True, **options)
#     web = WebGear(source=str(process()), logging=True, **options)

#     # run this app on Uvicorn server at address http://localhost:8000/
#     uvicorn.run(web(), host="localhost", port=8000)

#     # close app safely
#     web.shutdown()

