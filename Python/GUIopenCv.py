#TODO:
# - i create_point brukes self.frame_width, men denne defineres ikke før i show

import cv2
import numpy as np
kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
from screeninfo import get_monitors
standard_frame_size = (600,500)
standard_screen_size = (640,480)
screen_size_offset = 200    #+- hvor mange piksler skjærmstørrelsen kan avvike fra standard før den går til standard

def get_screen_size():
    screen_info = get_monitors()[0]
    width = screen_info.width
    height = screen_info.height

    if width > standard_screen_size[0] + screen_size_offset or width < standard_screen_size[0] - screen_size_offset:
        width = standard_screen_size[0]
    
    if height > standard_screen_size[1] + screen_size_offset or height < standard_screen_size[1] - screen_size_offset:
        height = standard_screen_size[1]
    
    return (width, height)

def ensure_valid_frame(frame):
    """ Returnerer `frame` bare hvis `frame` er et gyldig bilde og ikke avviker for mye fra standard
    bildestørrelse"""
    if np.any(frame) and type(frame) == np.ndarray:             # Sjekker at det er rett type
        try:
            frame_width, frame_height = get_frame_size(frame)   # Prøver å ta størrelsen på bildet, hvis den feiler, blir det error_window
            if frame_height < 50 or frame_height > 2000 or frame_width < 50 or frame_width > 2000:      # Dersom størrelsen på bildet er helt feil, blir det error_window
                frame = error_window()
            else:
                frame = frame
        except:
            frame = error_window()
    else:
        frame = error_window()
    return frame

def get_frame_size(frame):
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]
    return (frame_width, frame_height)

def create_cv2_window(window_name, function_on_mouse = None):
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            #cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        if function_on_mouse is not None:
            cv2.setMouseCallback(window_name, function_on_mouse)

def draw_border(frame, border_width):
    if (border_width > 0):
            frame = cv2.copyMakeBorder(frame, 0, border_width, border_width, border_width, cv2.BORDER_CONSTANT, value=0)
    return frame

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
        self.point_x = None
        self.point_y = None
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
            create_cv2_window(win_name, function_on_mouse)

            screen_width, screen_height = get_screen_size()
            
            bakgrunn = error_window(screen_width, screen_height)
            self.show(bakgrunn)

    def add_objects(self, objects: list):
        """
        Adds objects to the window.

        Parameters:
            objects (list): A list of objects to add to the window.
        """
        self.objects = objects

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
        if (self.point_x > self.frame_width-self.dslr_width-self.border_width and self.point_x < self.frame_width-self.border_width and self.point_y > 0 and self.point_y < self.frame_height-self.border_width):
            self.point_x = x  #setter self.point_x som det punktet skal være, dette håndteres av show()
            self.point_y = y
            
            degrees_per_pixel = self.vertical_angle/self.frame_height
            horisontal_offset = self.point_x-self.frame_width/2 #pixler unna senter
            vertiacal_offset = self.point_y-self.frame_height/2
            return (degrees_per_pixel*horisontal_offset, degrees_per_pixel*vertiacal_offset)
        else: 
            self.point_x = None
            self.point_y = None
            return None
    
    def create_center_point(self, frame):
        frame_width, frame_height = get_frame_size(frame)
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
        frame_width, frame_height = get_frame_size(frame)
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
        if width > 0:
            self.border_width = width

    def show(self, frame, value_factor = None):
        """Viser `frame` i et OpenCV-vindu. Oppdaterer objektene (knappene, border)\n
        Avsluttes med "q"

        Parameters
        ----------
        frame : array
            Bildet som skal vises
        """
        self.frame_width, self.frame_height = get_frame_size(frame)
        self.dslr_width = (self.frame_height-self.border_width)/self.aspect_ratio

        draw_border(frame, self.border_width)        
        
        # Tegner punktet
        if (self.point_x is not None and self.point_y is not None):
            cv2.rectangle(frame, (self.point_x, self.point_y), (self.point_x, self.point_y), (0,0,255), 5)
            self.point_x = None
            self.point_y = None

        # Legger til objektene (knappene)
        for e in self.objects: e.create(frame)

        # Skriver inn verdien til value_factor i øver venstre hjørne
        if (value_factor is not None):
            cv2.putText(frame, str(int(100*value_factor)), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, cv2.LINE_AA)
        
        # Tegner inn roi
        if self.roi_drawing:
            cv2.rectangle(frame, (self.roi[0], self.roi[1]), (self.roi[0]+self.roi[2], self.roi[1]+self.roi[3]), (0, 255, 0), 2)

        # Viser framen, håndterer avbryt med "q"
        cv2.imshow(self.win_name, frame)
        key = cv2.waitKey(10) & 0xFF
        if key == ord("q"):
            raise Exception("show ble stoppet av bruker")  # Når denne erroren kommer, vil koden i finally-blokken kjøres

    def destroy(self):
        """Fjerner OpenCV-vinduene"""
        cv2.destroyAllWindows()

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_scale = 1
FONT_thickness = 2

def get_text_size(text):
    return cv2.getTextSize(text, FONT, FONT_scale, FONT_thickness)[0]   #[0] for det gir (bredde, høyde)

def get_largest_text_width(text1, text2):
    text_width_list = [get_text_size(text1)[0], get_text_size(text2)[0]]    #[0] ettersom vi skal ha bredden
    largest_text_width = max(text_width_list)
    return largest_text_width

def get_contrast_color(background_color):
    """
    Returnerer enten hvit eller svart, 
    avhengig av hvilken som gir best kontrast mot bakgrunnsfargen.

    Parameters
    ----------
    background_color : tuple
        En tuple med tre verdier som representerer RGB-verdien
        til bakgrunnsfargen.

    Returns
    -------
    tuple
        En tuple med tre verdier som representerer RGB-verdien
        til den beste teksten basert på bakgrunnsfargen.
    """
    # Konverter bakgrunnsfargen til gråskala
    bg_gray = cv2.cvtColor(np.uint8([[background_color]]), cv2.COLOR_BGR2GRAY)[0][0]

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

def calculate_center_text(frame_width : int, frame_height : int, text : str = "", text_width : int = 0, text_height : int = 0, text_offset_position : tuple = (0,0)):
    """
    text_offset_position : verdi for hvor øvre venstre hjørne av frame vi skal kalkulere midt av, er på skjermen
        dette blir vanligvis øvre venstre hjørne av omrisset til knappen
    """
    if text_width == 0 and text_height == 0:
        (text_width, text_height) = get_text_size(text)
    # Beregn posisjonen for teksten
    text_x = (frame_width - text_width) // 2 + text_offset_position[0]
    text_y = (frame_height + text_height) // 2 + text_offset_position[1]
    return text_x, text_y

class button():
    def __init__(self, active_text, deactive_text, start_point, height, active_color, deactive_color):
        self.start_point = start_point
        
        self.active_color = active_color
        self.active_text = active_text
        self.deactive_text = deactive_text
        self.deactive_color = deactive_color

        largest_text_width = get_largest_text_width(active_text, deactive_text)

        self.button_width = largest_text_width + 20
        self.button_height = height
        self.end_point = (start_point[0] + self.button_width, start_point[1] + self.button_height)
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

        current_text_color = get_contrast_color(current_color)
        
        self.textX, self.textY = calculate_center_text(self.button_width, self.button_height, current_text, text_offset_position=self.start_point)
        self.frame = DrawRoundedRectangle(self.frame, self.start_point, self.end_point, radius=4, color=current_color, thickness=-1, line_type=cv2.LINE_AA)
        self.frame = cv2.putText(self.frame, current_text, (self.textX, self.textY), FONT, FONT_scale, current_text_color, FONT_thickness)
    
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

def create_multiple(left_frame, right_frame):
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

def error_window(width: int = standard_frame_size[0], height: int = standard_frame_size[1], text: str = "") -> np.ndarray:
    """
    Oppretter et bilde av en ikke-kontakt skjermeffekt.

    Parameters:
        width (int): Bredden på bildet.
        height (int): Høyden på bildet.
        text (str): Tekst på bildet.

    Returns:
        numpy.ndarray: Et numpy-array som representerer bildet av den ikke-kontakt skjermen.
    """
     # Opprett et tomt bilde
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Del vinduet inn i 5 like brede sektorer
    num_sectors = 5
    sector_width = width // num_sectors

    # Definer fargene for hver sektor
    colors = [(255, 255, 255), (0, 255, 255), (0, 255, 0), (255, 0, 255), (255, 255, 0)]

    # Gå gjennom hver sektor
    for i in range(num_sectors):
        # Hent fargen for gjeldende sektor
        color = colors[i]

        # Fyll sektoren med fargen
        sector_start = i * sector_width
        sector_end = (i + 1) * sector_width
        image[:, sector_start:sector_end] = color

    if text != "":
        try:
            (text_width, text_height) = get_text_size(text)
            
            text_x, text_y = calculate_center_text(width, height, text_width=text_width, text_height=text_height)

            # Definer størrelsen på rektangelet bak teksten
            rect_x = text_x - 20
            rect_y = text_y-text_height - 20
            rect_width = text_width + 40
            rect_height = text_height + 40

            # Fyll rektangelet med svart farge
            image = cv2.rectangle(image, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), (0, 0, 0), -1)

            # Skriv ut teksten på bildet
            image = cv2.putText(image, text, (text_x, text_y), FONT, FONT_scale, (255, 255, 255), FONT_thickness, cv2.LINE_AA)
        except TypeError:
            # If any of the rectangle coordinates are invalid, skip drawing the rectangle
            pass
    return image

def DrawRoundedRectangle(frame, topLeft, bottomRight, radius=1, color=255, thickness=1, line_type=cv2.LINE_AA):
    min_half = int(min((bottomRight[0] - topLeft[0]), (bottomRight[1] - topLeft[1])) * 0.5)
    radius = min(radius, min_half)

    # /* corners:
    #  * p1 - p2
    #  * |     |
    #  * p4 - p3
    #  */
    p1 = topLeft
    p2 = (bottomRight[0], topLeft[1])
    p3 = bottomRight
    p4 = (topLeft[0], bottomRight[1])

    if(thickness < 0):
        # // draw rectangle
        cv2.rectangle(frame, (p1[0] + radius, p1[1]),  (p3[0] - radius, p3[1]), color, thickness, line_type)
        cv2.rectangle(frame, (p1[0], p1[1] + radius),  (p3[0], p3[1] - radius), color, thickness, line_type)
    else:
        # // draw straight lines
        cv2.line(frame, (p1[0] + radius, p1[1]),  (p2[0] - radius, p2[1]), color, thickness, line_type)
        cv2.line(frame, (p2[0], p2[1] + radius),  (p3[0], p3[1] - radius), color, thickness, line_type)
        cv2.line(frame, (p4[0] + radius, p4[1]),  (p3[0]-radius, p3[1]), color, thickness, line_type)
        cv2.line(frame, (p1[0], p1[1] + radius),  (p4[0], p4[1] - radius), color, thickness, line_type)

    # // draw arcs
    if(radius > 0):
        cv2.ellipse( frame, (p1[0] + radius, p1[1] + radius), ( radius, radius ), 180.0, 0, 90, color, thickness, line_type )
        cv2.ellipse( frame, (p2[0] - radius, p2[1] + radius), ( radius, radius ), 270.0, 0, 90, color, thickness, line_type )
        cv2.ellipse( frame, (p3[0] - radius, p3[1] - radius), ( radius, radius ), 0.0, 0, 90, color, thickness, line_type )
        cv2.ellipse( frame, (p4[0] + radius, p4[1] - radius), ( radius, radius ), 90.0, 0, 90, color, thickness, line_type )
    return frame