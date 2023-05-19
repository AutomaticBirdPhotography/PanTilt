import cv2
import GUIopenCv as G

cap = cv2.VideoCapture(0)
main = G.window("Frame")

enable_button = G.button(active_text="ON", deactive_text="OFF", start_point=(40,380), height=50, active_color=(0,255,0), deactive_color=(0,0,255))
home_button = G.button("Hjem", "Hjem", (130, 380), 40, (255, 255, 255), (188,32,12))

main.add_objects([enable_button, home_button])
while True:
    ret, frame = cap.read()
    main.show(frame)
    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()