from vidgear.gears import NetGear
from vidgear.gears.helper import reducer
import traceback, time, threading
import cv2
import numpy as np
import ip_config
import socket
import GUIopenCv as G
ip_configurator = ip_config.IPConfigurator()
def configure_ip():
    ip_configurator.selectIP(invalid_ip=ip_configurator.clientAddress)
    print(ip_configurator.clientAddress)

options = {
    "request_timeout": 5,
    "max_retries": 35,
    "bidirectional_mode": True,
    "jpeg_compression": True,
    "jpeg_compression_quality": 95,
    "jpeg_compression_fastdct": True,
    "jpeg_compression_fastupsample": True,
}
class VideoStream():
    def __init__(self, logging : bool = True, clientAddress : str = "192.168.4.4", port : str = "5454", framePercentage : int = 20) -> None:
        self.recv_data = None
        self.server = NetGear(logging=logging, address=clientAddress, port=port, **options)
        self.percentage = framePercentage

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
        return self.recv_data
    
    def stop(self):
        if self.server is not None:
            self.server.close()

    def __del__(self):
        self.stop()


class VideoClient():
    def __init__(self, logging : bool = True, clientAddress : str = "auto", port : str = "5454") -> None:
        """
        Finner automatisk client-adressen, hvis ikke kommer tkintervindu opp hvor man kan legge inn

        Parameters
        ---------
            `clientAddress` 
                "auto" eller adresse, typ.: "192.168.10.184"
        """
        self.is_connected = False
        self.client = None
        self.server_data = None
        if clientAddress == "auto":
            self.clientAddress = socket.gethostbyname(socket.gethostname())
        else:
            self.clientAddress = clientAddress
        ip_configurator.clientAddress = self.clientAddress
        while True:
            try:
                self.client = NetGear(receive_mode=True, logging=logging, address=self.clientAddress, port=port, **options)
                self.target_data = None
                break
            except:
                configure_ip()
                self.clientAddress = ip_configurator.clientAddress
                if ip_configurator.closed:
                    raise Exception("Etableringsforsøk ble avsluttet")
        
        self.stopped = False
        self.frame = self.errorImg = G.error_window(600, 500, "Waiting for connection")
        self.thread = threading.Thread(target=self._grabFrameLoop)
        self.thread.daemon = True
        self.thread.start()

    def sendData(self, data):
        if self.is_connected:
            self.target_data = data
    
    def _grabFrameLoop(self):
        while not self.stopped:
            self.data = self.client.recv(return_data=self.target_data)
            if self.data is not None:
                self.is_connected = True
                self.server_data, in_frame = self.data
            else:
                in_frame = self.errorImg

            if np.any(in_frame):
                self.frame = in_frame

    def grabFrame(self):
        return self.frame
    
    def stop(self):
        """Stopper clienten, sender "s" til serveren"""
        self.stopped = True
        if self.client is not None:
            if self.is_connected:  #hvis den ikke er tilkoblet vil det ikke gå å skulle sende "s"
                self.client.recv(return_data="s")
            self.client.close()

    def __del__(self):
        self.stop()