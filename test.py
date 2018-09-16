#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 18-7-31
import cv2

import numpy as np

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    while 1:
        ret, frame = cap.read()
        cv2.imshow("capture", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
