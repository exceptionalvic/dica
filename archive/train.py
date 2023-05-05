import face_recognition
import cv2
import numpy as np
from .models import FaceEncodings, Intelligence, Suspect

def train_all_models():
    all_suspect = Suspect.objects.all()
    # create face_encodings and store them in the archive
    for s in all_suspect:
        s_image = face_recognition.load_image_file(str(s.mugshot.url))
        s_image_encoding = face_recognition.face_encodings(s_image)[0]
        new_encoding = FaceEncodings(suspect=s.id,face_encoding=s_image_encoding)
        new_encoding.save()


def train_new_model(request, suspect):
    # format_image = str(request.build_absolute_uri('/')[:-1])+str(suspect.mugshot.url)
    format_image = str(suspect.mugshot.url)
    split_img = format_image.split('/')
    # print(split_img)
    new_img = split_img[1]+'/'+split_img[2]+'/'+split_img[3]+'/'+split_img[4]
    # new_formated_image = '"'+format_image+'"'
    print(new_img)
    s_image = face_recognition.load_image_file(new_img)
    s_image_encoding = face_recognition.face_encodings(s_image)[0]
    new_encoding = FaceEncodings(suspect=suspect,face_encoding=s_image_encoding)
    new_encoding.save()

# # Load a sample picture and learn how to recognize it.
# obama_image = face_recognition.load_image_file("obama.jpg")
# obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# # Load a second sample picture and learn how to recognize it.
# biden_image = face_recognition.load_image_file("biden.jpg")
# biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# Create arrays of known face encodings and their names
# known_face_encodings = [
#     obama_face_encoding,
#     biden_face_encoding
# ]
# known_face_names = [
#     "Barack Obama",
#     "Joe Biden"
# ]