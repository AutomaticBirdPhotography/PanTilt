import pytest
import numpy as np
import cv2

import GUIopenCv as G

@pytest.mark.parametrize("background_color, text_color",[
    ((0,0,0), (255,255,255)),                       # Svart bilde - hvit tekst
    ((255,255,255), (0,0,0)),                       # Hvitt bilde - svart tekst
    ((255/2,255/2,255/2), (255,255,255))                  # Midt mellom svart og hvitt bilde, forventer hvit tekst
])

def test_get_contrast_color(background_color, text_color):
    output = G.get_contrast_color(background_color)
    assert output == text_color
    

error_window_frame = G.error_window()
@pytest.mark.parametrize("frame, expected_output", [
    (np.ones((100, 100)), np.ones((100, 100))),             # Valid frame within size range
    (np.ones((10, 100)), error_window_frame),                   # Frame with invalid size (height)
    (np.ones((100, 3000)), error_window_frame),                 # Frame with invalid size (width)
    (np.empty((0, 0)), error_window_frame),                     # Empty frame
    ("not an array", error_window_frame),                       # Non-array frame
    (None, error_window_frame)                                  # Invalid frame type
])
def test_ensure_valid_frame(frame, expected_output):
    assert np.array_equal(G.ensure_valid_frame(frame), expected_output)

@pytest.mark.parametrize("frame, expected_output", [
    (np.ones((100, 200)), (200, 100)),                    # Non-empty frame
    (np.empty((0, 0)), (0, 0)),                            # Empty frame
    (np.ones((100, 200, 3)), (200, 100))                # Frame with irregular shape
])
def test_get_frame_size(frame, expected_output):
    assert G.get_frame_size(frame) == expected_output
    
    
@pytest.mark.parametrize("frame, bbox, expected_output", [
    (np.ones((100, 200)), None, (100, 50)),                           # Frame provided, expected center coordinates
    (None, (50, 50, 150, 150), (125, 125)),             # Bbox provided, expected center coordinates
    (None, None, (0, 0))                                               # No frame or bbox provided, expected (0, 0)
])
def test_get_center_point_coordinates(frame, bbox, expected_output):
    assert G.get_center_point_coordinates(frame, bbox) == expected_output



# Teste largest_text_width, da trenger vi først å finne bredden i piksler
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_scale = 1
FONT_thickness = 2

def get_text_size(text):
    return cv2.getTextSize(text, FONT, FONT_scale, FONT_thickness)[0][0]   #[0] for det gir (bredde, høyde), så [0] for å få bredde
@pytest.mark.parametrize("text1, text2, expected_output", [
    ("III", "WWW", get_text_size("WWW")),      # Example texts with different widths, expected largest width
    ("Testing", "123", get_text_size("Testing")),      # Example texts with different widths, expected largest width
    ("", "Empty", get_text_size("Empty")),           # Example texts with one empty string, expected largest width from the non-empty string
    ("Equal", "Equal", get_text_size("Equal"))       # Example texts with equal widths, expected the width of either text
])
def test_get_largest_text_width(text1, text2, expected_output):
    assert G.get_largest_text_width(text1, text2) == expected_output