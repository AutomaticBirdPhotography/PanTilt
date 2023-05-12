import GUIopenCv as g
import cv2

def onMouse(event, mouse_x, mouse_y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        main.mouse_x = mouse_x
        main.mouse_y = mouse_y

#main = g.window("hei", onMouse)
cv2.namedWindow("Hei")



i = 0
while True:
    i += 2
