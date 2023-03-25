from vidgear.gears import NetGear
from vidgear.gears.helper import reducer
import traceback, time
import cv2
options = {
    "request_timeout": 5,
    "max_retries": 20,
    "bidirectional_mode": True,
    "jpeg_compression": True,
    "jpeg_compression_quality": 95,
    "jpeg_compression_fastdct": True,
    "jpeg_compression_fastupsample": True,
}
class VideoStream():
    def __init__(self, logging : bool = True, clientAddress : str = "192.168.4.1", port : str = "5454", framePercentage : int = 20) -> None:
        self.server = NetGear(logging=logging, address=clientAddress, port=port, **options)
        self.percentage = framePercentage
        #self.wait()
    def wait(self):
        client = None
        while not client:
            try:
                client = self.server.recv(return_data=False)
            except:
                time.sleep(0.1)
                continue

    def sendFrame(self, frame):
        self.frame = frame
        if self.frame is not None:
            self.frame = reducer(self.frame, self.percentage)
            self.recv_data = self.server.send(self.frame)
        key = cv2.waitKey(10) & 0xFF
        if key == ord("q"):
            self.stop()
            cv2.destroyAllWindows()
            raise Exception("sendFrame ble stoppet av bruker")  # Når denne erroren kommer, vil koden i finally-blokken kjøres

    def getData(self):
        if self.recv_data is not None:
            return self.recv_data
    
    def stop(self):
        self.server.close()

    def __del__(self):
        self.server.close()


class VideoClient():
    def __init__(self, logging : bool = True, clientAddress : str = "192.168.4.1", port : str = "5454") -> None:
        self.client = NetGear(receive_mode=True, logging=logging, address=clientAddress, port=port, **options)
        self.target_data = None

    def sendData(self, data):
        self.target_data = data
    
    def grabFrame(self):
        self.data = self.client.recv(return_data=self.target_data)
        if self.data is not None:
            self.server_data, self.frame = self.data
            if self.frame is not None:
                return self.frame

    def stop(self):
        """Stopper clienten, sender "s" til serveren"""
        self.sendData("s")
        self.grabFrame()    #Må være her for det er når bildet mottas at teksten sendes
        self.client.close()

    def __del__(self):
        self.sendData("s")
        self.grabFrame()    #Må være her for det er når bildet mottas at teksten sendes
        self.client.close()