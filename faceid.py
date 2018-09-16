#!/usr/bin/env python3
# coding: utf-8
import time

import numpy as np
import face_recognition
import cv2
import pandas as pd
import glob


def FaceID(image_path):
    face_lst = []
    for i in image_path:
        image = cv2.imread(i)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=1, model="cnn")

        # face = face_locations[0]
        # face_img = image[face[0] - 50:face[2] + 50, face[3] - 50:face[1] + 50, :]

        face_encoding = face_recognition.face_encodings(image, known_face_locations=face_locations, num_jitters=1)[0]

        # face_encoding = face_recognition.face_encodings(image)[0]

        face_lst.append(face_encoding)

    return np.array(face_lst)


def FromCamera(code):
    cap = cv2.VideoCapture()
    # cap.open(0)
    # cap.open('rtsp://172.16.0.35/onvif/live/1')
    cap.open('rtsp://admin:123iselab.cn@172.16.0.209:554/Streaming/Channels/102')

    red = (0, 0, 255)  # BGR?
    th = 3

    while True:
        # for i in range(20):
        #     _, _ = cap.read()
        ret, frame = cap.read()
        if not ret:
            continue

        # frame = cv2.resize(frame, (0, 0), fx=0.8, fy=0.8)
        image = frame.copy()
        # image = cv2.resize(image, (0, 0), fx=0.8, fy=0.8)

        # image = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        video_width = int(cap.get(3) * 0.3)
        video_height = int(cap.get(4) * 0.3)

        remark_shape = (int(video_width * 0.3), int(video_height * 0.3))

        font = cv2.FONT_HERSHEY_SIMPLEX

        # image=cv2.imread('/Users/wanjun/Desktop/ISEFaceId/my.jpg')
        # image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=1, model="hog")

        if len(face_locations) != 0:
            for face in face_locations:
                cv2.rectangle(image, (face[1], face[0]), (face[3], face[2]), color=red, thickness=th)

        face_landmarks_list = face_recognition.face_landmarks(image)

        if len(face_landmarks_list) == 0:
            cv2.putText(image, 'No landmark', remark_shape, font, 1, (0, 0, 255),
                        1)

        else:
            chin = face_landmarks_list[0]['chin']
            left_eye = np.array(face_landmarks_list[0]['left_eye'])
            right_eye = np.array(face_landmarks_list[0]['right_eye'])
            nose_tip = np.array(face_landmarks_list[0]['nose_tip'])

            le = left_eye[:, 1].mean()
            le_w = left_eye[:, 0].mean()
            re = right_eye[:, 1].mean()
            re_w = right_eye[:, 0].mean()
            nt = nose_tip[:, 1].mean()
            nt_w = nose_tip[:, 0].mean()

            mark = [(int(le_w), int(le)), (int(re_w), int(re)), (int(nt_w), int(nt)), chin[8], chin]

            for i in range(len(chin) - 1):
                cv2.line(image, chin[i], chin[i + 1], color=red, thickness=th)

            cv2.circle(image, mark[0], 5, red, 10)
            cv2.circle(image, mark[1], 5, red, 10)
            cv2.circle(image, mark[2], 5, red, 10)

            # face_img=image[face[0]-20:face[2]+20,face[3]-20:face[1]+20:]

            face_encoding = face_recognition.face_encodings(image, known_face_locations=face_locations, num_jitters=1)

            if len(face_encoding) != 0:

                face_encoding = face_encoding[0]

                results = face_recognition.compare_faces(code, face_encoding, tolerance=0.5)
            else:
                results = False

            if not results:
                cv2.putText(image, 'No face', remark_shape, font, 1, red, 1)
            else:
                for i in range(len(name_lst)):
                    if results[i]:
                        print(name_lst[i])
                        cv2.putText(image, name_lst[i], remark_shape, font, 1, red, 1)
                        break

        cv2.imshow('frame', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # time.sleep(0.3)


if __name__ == '__main__':
    time1 = time.time()
    img_lst = glob.glob('face_data/*.jpg')
    print(img_lst)
    print("time used: %s" % (time.time() - time1))
    time1 = time.time()
    name_lst = list()
    for img in img_lst:
        fn = img.split('/')[-1].split('.')[0]
        name_lst.append(fn)
    code = FaceID(img_lst)
    print('face image coded')
    print("time used: %s" % (time.time() - time1))
    FromCamera(code)
