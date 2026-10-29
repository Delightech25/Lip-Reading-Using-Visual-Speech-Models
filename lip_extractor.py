import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh

LIPS = [61,146,91,181,84,17,314,405,321,375]

def extract_lips(video_path):

    cap = cv2.VideoCapture(video_path)
    frames = []

    with mp_face_mesh.FaceMesh() as face_mesh:

        while True:

            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:

                for face in results.multi_face_landmarks:

                    h,w,_ = frame.shape
                    pts=[]

                    for i in LIPS:
                        x=int(face.landmark[i].x*w)
                        y=int(face.landmark[i].y*h)
                        pts.append((x,y))

                    pts=np.array(pts)

                    x,y,w1,h1=cv2.boundingRect(pts)

                    lip=frame[y:y+h1,x:x+w1]
                    lip=cv2.resize(lip,(96,96))

                    frames.append(lip)

    cap.release()

    return frames