import cv2


video_path = 'demo1.mp4'
cap = cv2.VideoCapture(video_path)
while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('video', frame)
    else:
        break
    if cv2.waitKey(1) & 0xFF == ord('q') :
        break
cap.release()
cv2.destroyAllWindows()