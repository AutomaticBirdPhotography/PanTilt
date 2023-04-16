import cv2
import numpy as np
kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
import ctypes

# Få skjermens bredde og høyde

class window():
    """
    A class for creating OpenCV windows and handling mouse events.
    """
    def __init__(self, win_name = None, function_on_mouse = None) -> None:
        """
        Creates a new Window object.

        Parameters
        ----------
        win_name : str
            The name of the window to display the GUI
        function_on_mouse : Funciton
            The function to call when a mouse event occurs in the window.
        """
        self.vertical_angle = 2.75 #grader ved fullframe 500mm
        self.aspect_ratio = 3/4 #endres i samsvar med PanTilt

        self.win_name = win_name
        self.function_on_mouse = function_on_mouse
        self.x = -1
        self.y = -1
        self.mouse_x = None
        self.mouse_y = None

        self.roi = []
        self.start_point = []
        self.end_point = []
        self.roi_selected = False
        self.roi_drawing = False
        self.tracker = None

        self.objects = []
        self.border_width = 0 #endres til antall pixler hvis man setter "createBorder()"
        if win_name is not None:
            skjerm_info = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
            self.skjerm_bredde = skjerm_info[0]
            self.skjerm_hoyde = skjerm_info[1]
            cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            if self.function_on_mouse is not None:
                cv2.setMouseCallback(self.win_name, self.function_on_mouse)
            

    def add_objects(self, objects: list):
        """
        Adds objects to the window.

        Parameters:
            objects (list): A list of objects to add to the window.
        """
        self.objects = objects

    
    def create_multiple(self, left_frame, right_frame):
        """
        Creates a new image consisting of the given frames.

        Parameters:
            right_frame (numpy.ndarray): The frame to place on the right side of
                the new image.
            left_frame (numpy.ndarray): The frame to place on the left side of the
                new image.

        Returns:
            numpy.ndarray: The new image consisting of the given frames.
        """
        left_frame = left_frame[..., :3]
        left_frame = cv2.rotate(left_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        l_height, l_width, l_channels = left_frame.shape
        r_height, r_width, r_channels = right_frame.shape
        result = np.zeros((max(l_height, r_height), l_width+r_width, l_channels), dtype=np.uint8)
        left_frame = cv2.filter2D(left_frame, -1, kernel)
        result[:l_height,:l_width] = left_frame
        result[:r_height, l_width:l_width+r_width] = right_frame        
        return result

    def create_point(self, x:int, y:int):
        """
        Sets a point at the given (x, y) coordinates and returns the degrees offset from the center of the frame

        Parameters
        ----------
        x : int
            The x-coordinate of the point
        y : int
            The y-coordinate of the point

        Returns
        -------
        tuple or None
            The degrees offset from the center of the frame if the point is within the frame, otherwise None
        """
        self.x = x
        self.y = y
        if (self.x > self.frame_width-self.dslr_width-self.border_width and self.x < self.frame_width-self.border_width and self.y > 0 and self.y < self.frame_height-self.border_width):
            degrees_per_pixel = self.vertical_angle/self.frame_height
            horisontal_offset = self.x-self.frame_width/2 #pixler unna senter
            vertiacal_offset = self.y-self.frame_height/2
            return (degrees_per_pixel*horisontal_offset, degrees_per_pixel*vertiacal_offset)
        else: return None
    
    def create_center_point(self, frame):
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        x = int(frame_width/2)
        y = int(frame_height/2)
        cv2.rectangle(frame, (x, y), (x, y), (0,0,255), 5)

    def draw_roi(self, event, x, y):
        """
        Draws a region of interest (ROI) on the frame when the left mouse button is clicked and dragged.

        Parameters
        ----------
        event
            The type of mouse event (left mouse button down, mouse move, or left mouse button up)
        x : int
            The x-coordinate of the mouse event
        y : int
            The y-coordinate of the mouse event
        """
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
            return(self.roi)
        
    def define_roi(self, roi):
        self.roi = roi
        self.roi_selected = True
        self.roi_drawing = False
        self.tracker = None

    def TRACK(self, frame):
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        x = int(frame_width/2)
        y = int(frame_height/2)
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
        else: return None

    def create_border(self, width: int = 50):
        """Setter at det skal være en kant på `width`px til høyre, venstre og under"""
        self.border_width = width

    def log(self, data: str):
        """
        Logger data til skjermen
        """
        #TODO her trengs en avbrytknapp
        bakgrunn = np.zeros((self.skjerm_hoyde, self.skjerm_bredde, 3), dtype=np.uint8)

        midtpunkt_x = int(self.skjerm_bredde / 2)
        midtpunkt_y = int(self.skjerm_hoyde / 2)


        tekst = data
        tekst_tykkelse = 2
        tekst_type = cv2.FONT_HERSHEY_SIMPLEX
        tekst_scale = 1

        tekst_storrelse, _ = cv2.getTextSize(tekst, tekst_type, tekst_scale, tekst_tykkelse)
        tekst_bredde = tekst_storrelse[0]
        tekst_hoyde = tekst_storrelse[1]
        tekst_pos_x = midtpunkt_x - int(tekst_bredde / 2)
        tekst_pos_y = midtpunkt_y + int(tekst_hoyde / 2)
        cv2.putText(bakgrunn, tekst, (tekst_pos_x, tekst_pos_y), tekst_type, tekst_scale, (255,255,255), tekst_tykkelse, cv2.LINE_AA)

        avbryt_bredde = 100
        avbryt_hoyde = 70
        avbryt = button("Avbryt", "Avbryt", (midtpunkt_x - int(avbryt_bredde/2), midtpunkt_y + int(avbryt_hoyde/2) + 50), avbryt_bredde, (0,0,255), (0,0,255))
        avbryt.create(bakgrunn)

        cv2.imshow(self.win_name, bakgrunn)
        key = cv2.waitKey(10) & 0xFF
        if key == ord("q") or avbryt.is_clicked((self.mouse_x, self.mouse_y)):
            avbryt.toggle()
            raise Exception("show ble stoppet av bruker")  # Når denne erroren kommer, vil koden i finally-blokken kjøres


    def show(self, frame, value_factor = None):
        """Viser `frame` i et OpenCV-vindu. Oppdaterer objektene (knappene, border)\n
        Avsluttes med "q"

        Parameters
        ----------
        frame : array
            Bildet som skal vises
        """
        if (self.border_width > 0):
            frame = cv2.copyMakeBorder(frame, 0,self.border_width,self.border_width,self.border_width, cv2.BORDER_CONSTANT, value=0)
        self.frame_height = frame.shape[0]
        self.frame_width = frame.shape[1]
        self.dslrWidth = (self.frame_height-self.border_width)/self.aspect_ratio
        
        if (self.x > self.frame_width-self.dslrWidth-self.border_width and self.x < self.frame_width-self.border_width and self.y > 0 and self.y < self.frame_height-self.border_width):
            cv2.rectangle(frame, (self.x, self.y), (self.x, self.y), (0,0,255), 5)
            self.x = -1
            self.y = -1
        for e in self.objects: e.create(frame)
        if (value_factor is not None):
            cv2.putText(frame, str(int(100*value_factor)), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, cv2.LINE_AA)
        
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
    def __init__(self, active_text, deactive_text, start_point, height, active_color, deactive_color):
        self.start_point = start_point
        
        self.active_color = active_color
        self.active_text = active_text
        self.deactive_text = deactive_text
        self.deactive_color = deactive_color

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 1
        self.font_thicknes = 2
        text_sizes_list = [cv2.getTextSize(active_text, self.font, self.font_scale, self.font_thicknes)[0], 
              cv2.getTextSize(deactive_text, self.font, self.font_scale, self.font_thicknes)[0]]
        largest_text_size = max(text_sizes_list, key=lambda x: x[0])
        button_width = largest_text_size[0] + 20
        self.end_point = (start_point[0]+button_width, start_point[1]+height)
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
            current_text = self.active_text
            current_color = self.active_color
        else:
            current_text = self.deactive_text
            current_color = self.deactive_color

        current_text_color = self.get_contrast_color(current_color)

        self.textsize = cv2.getTextSize(current_text, self.font, self.font_scale, self.font_thicknes)[0]
        self.textX = int((((self.end_point[0]-self.start_point[0]) - self.textsize[0]) / 2)+self.start_point[0])
        self.textY = int((((self.end_point[1]-self.start_point[1]) + self.textsize[1]) / 2)+self.start_point[1])
        self.frame = cv2.rectangle(self.frame, self.start_point, self.end_point, current_color, -1)
        self.frame = cv2.putText(self.frame, current_text, (self.textX, self.textY), self.font, self.font_scale, current_text_color, self.font_thicknes, cv2.LINE_AA)

    def is_clicked(self, mouse_pos):
        """Skjekker om `mouse_pos` er over arealet til knappen

        Parameters
        ----------
        mouse_pos : touple
            Posisjonen (x, y) til musa

        Returns
        -------
        True
            hvis `mouse_pos` er over arealet til knappen\n
        False
            hvis `mouse_pos` ikke er over arealet til knappen
        """
        if (mouse_pos[0] == None or mouse_pos[1] == None):
            return False

        elif ((mouse_pos[0] < self.end_point[0]) 
              & (mouse_pos[0] > self.start_point[0]) 
              & (mouse_pos[1] < self.end_point[1]) 
              & (mouse_pos[1] > self.start_point[1])):
            self.create(self.frame)
            return True
        else:
            return False

    def toggle(self):
        self.active = not self.active

    def activate(self):
        """Setter knappen til å være aktiv - endrer utseende"""
        self.active = True

    def deactivate(self):
        """Setter knappen til å være deaktivert - endrer utseende"""
        self.active = False

    def get_contrast_color(self, bg_color):
        """
        Returnerer enten hvit eller svart, 
        avhengig av hvilken som gir best kontrast mot bakgrunnsfargen.

        Parameters
        ----------
        bg_color : tuple
            En tuple med tre verdier som representerer RGB-verdien
            til bakgrunnsfargen.

        Returns
        -------
        tuple
            En tuple med tre verdier som representerer RGB-verdien
            til den beste teksten basert på bakgrunnsfargen.
        """
        # Konverter bakgrunnsfargen til gråskala
        bg_gray = cv2.cvtColor(np.uint8([[bg_color]]), cv2.COLOR_BGR2GRAY)[0][0]

        # Beregn luminansen til hvitt og svart
        white_luminance = cv2.cvtColor(np.uint8([[[255, 255, 255]]]), cv2.COLOR_BGR2GRAY)[0][0]
        black_luminance = cv2.cvtColor(np.uint8([[[0, 0, 0]]]), cv2.COLOR_BGR2GRAY)[0][0]

        # Beregn kontrasten mellom bakgrunnsfargen og hvitt/svart
        white_contrast = abs(int(white_luminance) - int(bg_gray))
        black_contrast = abs(int(black_luminance) - int(bg_gray))

        # Returner fargen med høyest kontrast
        if white_contrast > black_contrast:
            return (255, 255, 255)
        else:
            return (0, 0, 0)