import sys
import os
import pytest, time
from unittest.mock import Mock, patch

# Add the parent directory of 'tests' to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ArduinoSerial import Arduino

@pytest.mark.parametrize("data, expected_serial_data", [
    (None, b''),
    ([1,2,3], b'[1, 2, 3]'),
    ("Hello, world!", b'Hello, world!'),
    ("123", b'123'),
    # Add more test cases as needed
])
def test_send(data, expected_serial_data):
    # Create a mock serial port object.
    serial_port = Mock()

    # Patch the 'serial.Serial' class with the mock serial port object.
    with patch('serial.Serial', return_value=serial_port):
        # Create an instance of the Arduino class using the mock serial port object.
        arduino = Arduino('/dev/ttyUSB0')

        # Send the data to the mock serial port.
        arduino.send(data)

        # Wait for a short time to allow the send thread to process the data.
        time.sleep(0.1)

        # Assert that the serial port's write() method was called with the properly encoded data.
        serial_port.write.assert_called_once_with(expected_serial_data)

        # Stop the send thread.
        arduino.serial.close()


# Her tester vi read()-funksjonen. Expected_data er det serial.readline() vil returnere
# Først skriver vi det som arduinoen vil sende, så skriver vi det vi ønsker at funksjonen read() skal
#returnere. Vi endrer den faktiske funksjonen read() dersom vi ikke får ønsket svar
@pytest.mark.parametrize("serial_data, expected_data", [
    (b'Hello, world!', 'Hello, world!'),
    (b'123', '123'),
    (b'', '')
    # Add more test cases as needed
])
def test_read(serial_data, expected_data):
    # Create a mock serial port object.
    serial_port = Mock()

    # Patch the 'serial.Serial' class with the mock serial port object.
    with patch('serial.Serial', return_value=serial_port):
        # Create an instance of the Arduino class using the mock serial port object.
        arduino = Arduino('/dev/ttyUSB0')

        # Set up the mock serial port to return the encoded data.
        serial_port.readline.return_value = serial_data

        # Call the read() function to read the data from the mock serial port.
        received_data = arduino.read()

        # Assert that the read data is equal to the expected data.
        assert received_data == expected_data
