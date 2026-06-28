import cv2
import os
path = r'C:\Users\marko\Desktop\camera_real.jpg'
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
ok, frame = cap.read()
cap.release()
if not ok:
    raise SystemExit('CAMERA_READ_FAILED')
cv2.imwrite(path, frame)
print('SAVED', os.path.abspath(path))
print('SIZE', os.path.getsize(path))
