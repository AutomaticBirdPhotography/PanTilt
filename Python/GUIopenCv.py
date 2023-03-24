"""
V 1.0.9
"""

import cv2
import numpy as np
kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
class window():
    def __init__(self, win_name = None, function_on_mouse = None) -> None:
        """
        Parameters
        ----------
        win_name : str
            Må definerses for bruk av knapp og `.show()`\n
            Dersom `win_name` er definert lages OpenCV-vindu med dette navnet
        function_on_mouse : function
            Må defineres for bruk av knapp\n
            Dersom `function_on_mouse` er definert bindes klikk på knapp til denne
        """
        self.verticalAngle = 2.75 #grader ved fullframe 500mm
        self.aspectRatio = 3/4 #endres i samsvar med PanTilt

        self.win_name = win_name
        self.function_on_mouse = function_on_mouse
        self.x = -1
        self.y = -1

        self.roi = []
        self.start_point = []
        self.end_point = []
        self.roi_selected = False
        self.roi_drawing = False
        self.tracker = None

        self.objects = []
        self.borderWidth = 0 #endres til antall pixler hvis man setter bruker "createBorder()"
        self.initGUI = False
        if win_name is not None:
            self.initGUI = True
            

    def addObjects(self, objects: list):
        self.objects = objects

    
    def createMultiple(self, leftFrame, rightFrame):
        """Lager et bilde bestående av `leftFrame` og `rightFrame`\n
        Fyller områdene som ikke er dekket av bilde svarte

        Parameters
        ----------
        leftFrame : array
            Bildet til venstre.

        rightFrame : array
            Bildet til høyre.

        Returns
        -------
        result : array
            Bilde bestående av `leftFrame` og `rightFrame`
        """
        leftFrame = leftFrame[..., :3]
        leftFrame = cv2.rotate(leftFrame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        Lheight, Lwidth, Lchannels = leftFrame.shape
        Rheight, Rwidth, Rchannels = rightFrame.shape
        result = np.zeros((max(Lheight, Rheight), Lwidth+Rwidth, Lchannels), dtype=np.uint8)
        leftFrame = cv2.filter2D(leftFrame, -1, kernel)
        result[:Lheight,:Lwidth] = leftFrame
        result[:Rheight, Lwidth:Lwidth+Rwidth] = rightFrame        
        return result

    def createPoint(self, x:int, y:int):
        """Setter et punkt på `x` og `y` koordinatene"""
        self.x = x
        self.y = y
        if (self.x > self.frameWidth-self.dslrWidth-self.borderWidth and self.x < self.frameWidth-self.borderWidth and self.y > 0 and self.y < self.frameHeight-self.borderWidth):
            degreesPerPixel = self.verticalAngle/self.frameHeight
            horisontalOffset = self.x-self.frameWidth/2 #pixler unna senter
            vertiacalOffset = self.y-self.frameHeight/2
            return (degreesPerPixel*horisontalOffset, degreesPerPixel*vertiacalOffset)
        else: return None
    
    def createCenterPoint(self, frame):
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]
        x = int(frameWidth/2)
        y = int(frameHeight/2)
        cv2.rectangle(frame, (x, y), (x, y), (0,0,255), 5)

    def drawRoi(self, event, x, y):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_point = [x,y]
            self.roi = [x,y,0,0]
            self.roi_selected = False
            self.roi_drawing = True
        elif event == cv2.EVENT_MOUSEMOVE and self.roi_drawing:
            if not self.roi_selected:
                self.end_point = [x, y]
                self.roi = [min(self.start_point[0], self.end_point[0]), min(self.start_point[1],self.end_point[1]), abs(self.end_point[0]-self.start_point[0]), abs(self.end_point[1]-self.start_point[1])]
        elif event == cv2.EVENT_LBUTTONUP:
            self.roi_selected = True
            self.roi_drawing = False
            self.tracker = None

    def TRACK(self, frame):
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]
        x = int(frameWidth/2)
        y = int(frameHeight/2)
        track_center = [x,y]
        cv2.rectangle(frame, (x, y), (x, y), (0,0,255), 5)
        if self.roi_selected and self.tracker is None:
            self.tracker = cv2.legacy.TrackerMOSSE_create()
            track_success = self.tracker.init(frame, tuple(self.roi))
        if self.tracker is not None:
            track_success, bbox = self.tracker.update(frame)
            if track_success:
                track_center = [int((bbox[2])/2+bbox[0]), int((bbox[3])/2+bbox[1])]
                cv2.rectangle(frame, track_center, track_center, (255, 0, 255), 5)
                cv2.line(frame, track_center, (x,y), (255, 0, 0), 2, cv2.LINE_AA)
                bbox = [int(i) for i in bbox]
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), (0, 255, 255), 2)
        return [track_center[0]-x,track_center[1]-y]

    def createBorder(self, width: int = 50):
        """Setter at det skal være en kant på `width`px til høyre, venstre og under        """
        self.borderWidth = width

    def show(self, frame, valueFactor = None):
        """Viser `frame` i et OpenCV-vindu. Oppdaterer objektene (knappene, border)\n
        Avsluttes med "q"

        Parameters
        ----------
        frame : array
            Bildet som skal vises
        """
        if self.initGUI:
            cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)
            #cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            if self.function_on_mouse is not None:
                cv2.setMouseCallback(self.win_name, self.function_on_mouse)
            self.initGUI = False
        if (self.borderWidth > 0):
            frame = cv2.copyMakeBorder(frame, 0,self.borderWidth,self.borderWidth,self.borderWidth, cv2.BORDER_CONSTANT, value=0)
        self.frameHeight = frame.shape[0]
        self.frameWidth = frame.shape[1]
        self.dslrWidth = (self.frameHeight-self.borderWidth)/self.aspectRatio
        
        if (self.x > self.frameWidth-self.dslrWidth-self.borderWidth and self.x < self.frameWidth-self.borderWidth and self.y > 0 and self.y < self.frameHeight-self.borderWidth):
            cv2.rectangle(frame, (self.x, self.y), (self.x, self.y), (0,0,255), 5)
            self.x = -1
            self.y = -1
        for e in self.objects: e.create(frame)
        if (valueFactor is not None):
            cv2.putText(frame, str(int(100*valueFactor)), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, cv2.LINE_AA)
        
        if self.roi_drawing:
            cv2.rectangle(frame, (self.roi[0], self.roi[1]), (self.roi[0]+self.roi[2], self.roi[1]+self.roi[3]), (0, 255, 0), 2)
    
        cv2.imshow(self.win_name, frame)
        key = cv2.waitKey(10) & 0xFF
        if key == ord("q"):
            raise Exception("show ble stoppet av bruker")  # Når denne erroren kommer, vil koden i finally-blokken kjøres

    def destroy(self):
        """Fjerner OpenCV-vinduene"""
        cv2.destroyAllWindows()

class button():
    def __init__(self, active_text, deactive_text, start_point, width, height, active_color, deactive_color):
        self.start_point = start_point
        self.end_point = (start_point[0]+width, start_point[1]+height)
        self.active_color = active_color
        self.active_text = active_text
        self.deactive_text = deactive_text
        self.deactive_color = deactive_color

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontScale = 1
        self.fontThicknes = 2
        
        self.active = False
        

    def create(self, frame):
        """Legger knappen til på `frame`, med knappeegenskapene definert i konstruktøren

        Parameters
        ----------
        frame : array
            Bildet knappen skal legges til på
        """
        self.frame = frame
        if self.active:
            self.textsize = cv2.getTextSize(self.active_text, self.font, self.fontScale, self.fontThicknes)[0]# finn størrelsen på teksten
            self.textX = int((((self.end_point[0]-self.start_point[0]) - self.textsize[0]) / 2)+self.start_point[0])
            self.textY = int((((self.end_point[1]-self.start_point[1]) + self.textsize[1]) / 2)+self.start_point[1])

            self.frame = cv2.rectangle(self.frame, self.start_point, self.end_point, self.active_color, -1)
            self.frame = cv2.putText(self.frame, self.active_text, (self.textX, self.textY), self.font, self.fontScale, (0,0,0), self.fontThicknes, cv2.LINE_AA)
        else:
            self.textsize = cv2.getTextSize(self.deactive_text, self.font, self.fontScale, self.fontThicknes)[0]# finn størrelsen på teksten
            self.textX = int((((self.end_point[0]-self.start_point[0]) - self.textsize[0]) / 2)+self.start_point[0])
            self.textY = int((((self.end_point[1]-self.start_point[1]) + self.textsize[1]) / 2)+self.start_point[1])

            self.frame = cv2.rectangle(self.frame, self.start_point, self.end_point, self.deactive_color, -1)
            self.frame = cv2.putText(self.frame, self.deactive_text, (self.textX, self.textY), self.font, self.fontScale, (0,0,0), self.fontThicknes, cv2.LINE_AA)


    def isClicked(self, mousePos):
        """Skjekker om `mousePos` er over arealet til knappen

        Parameters
        ----------
        mousePos : touple
            Posisjonen (x, y) til musa

        Returns
        -------
        True
            hvis `mousePos` er over arealet til knappen\n
        False
            hvis `mousePos` ikke er over arealet til knappen
        """
        if (mousePos[0] == None or mousePos[1] == None):
            return False

        elif ((mousePos[0] < self.end_point[0]) & (mousePos[0] > self.start_point[0]) & (mousePos[1] < self.end_point[1]) & (mousePos[1] > self.start_point[1])):
            self.create(self.frame)
            return True
        else:
            return False

    def activate(self):
        """Setter knappen til å være aktiv - endrer utseende"""
        self.active = True

    def deactivate(self):
        """Setter knappen til å være deaktivert - endrer utseende"""
        self.active = False
    