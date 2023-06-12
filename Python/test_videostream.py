import pytest
from vidTransfer import VideoStream

class TestVideoStream:
    def test_sendFrame(self):
        videostream = VideoStream(logging=False, clientAddress="192.168.4.4", port="5454", framePercentage=20)

        videostream.sendFrame(frame)