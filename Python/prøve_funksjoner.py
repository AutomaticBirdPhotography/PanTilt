import cv2
import numpy as np

def DrawRoundedRectangle(frame, topLeft, bottomRight, radius=1, color=255, thickness=1, line_type=cv2.LINE_AA):
    min_half = int(min((bottomRight[0] - topLeft[0]), (bottomRight[1] - topLeft[1])) * 0.5)
    radius = min(radius, min_half)

    p1 = topLeft
    p2 = (bottomRight[0], topLeft[1])
    p3 = bottomRight
    p4 = (topLeft[0], bottomRight[1])

    if(thickness < 0):
        cv2.rectangle(frame, (p1[0] + radius, p1[1]), (p3[0] - radius, p3[1]), color, thickness, line_type)
        cv2.rectangle(frame, (p1[0], p1[1] + radius), (p3[0], p3[1] - radius), color, thickness, line_type)
    else:
        cv2.line(frame, (p1[0] + radius, p1[1]), (p2[0] - radius, p2[1]), color, thickness, line_type)
        cv2.line(frame, (p2[0], p2[1] + radius), (p3[0], p3[1] - radius), color, thickness, line_type)
        cv2.line(frame, (p4[0] + radius, p4[1]), (p3[0]-radius, p3[1]), color, thickness, line_type)
        cv2.line(frame, (p1[0], p1[1] + radius), (p4[0], p4[1] - radius), color, thickness, line_type)

    if(radius > 0):
        cv2.ellipse(frame, (p1[0] + radius, p1[1] + radius), (radius, radius), 180.0, 0, 90, color, thickness, line_type)
        cv2.ellipse(frame, (p2[0] - radius, p2[1] + radius), (radius, radius), 270.0, 0, 90, color, thickness, line_type)
        cv2.ellipse(frame, (p3[0] - radius, p3[1] - radius), (radius, radius), 0.0, 0, 90, color, thickness, line_type)
        cv2.ellipse(frame, (p4[0] + radius, p4[1] - radius), (radius, radius), 90.0, 0, 90, color, thickness, line_type)

    return frame


def create_button(width, height, text):
    # Create a blank image with a white background
    button_img = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Define button colors
    button_color = (100, 100, 100)  # Gray color for the button
    border_color = (150, 150, 150)  # Light gray color for the border
    text_color = (255, 255, 255)    # White color for the text

    # Define button dimensions
    border_thickness = 2
    border_radius = 10
    text_scale = 0.5

    # Draw the button rectangle with rounded corners
    DrawRoundedRectangle(
        button_img,
        (border_thickness, border_thickness),
        (width - border_thickness, height - border_thickness),
        radius=border_radius,
        color=button_color,
        thickness=-1,
    )

    # Draw the button border
    DrawRoundedRectangle(
        button_img,
        (0, 0),
        (width, height),
        radius=border_radius,
        color=border_color,
        thickness=border_thickness,
    )

    # Calculate the text position to be centered
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, text_scale, 2)
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2

    # Draw the text on the button
    cv2.putText(
        button_img,
        text,
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        text_scale,
        text_color,
        2,
        cv2.LINE_AA,
    )

    return button_img


# Example usage
button_width = 200
button_height = 80
button_text = "Click Me!"

button = create_button(button_width, button_height, button_text)
cv2.imshow("Button", button)
cv2.waitKey(0)
cv2.destroyAllWindows()
