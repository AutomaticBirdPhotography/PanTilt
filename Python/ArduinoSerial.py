import serial
import threading
import queue

class Arduino():
    def __init__(self, port: str, baudrate: int = 115200 , timeout: float = 1) -> None:
        """
        Kjør `ls /dev/tty*` for å finne porten
        """
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.send_queue = queue.Queue()
        self.send_thread = threading.Thread(target=self._send_loop, args=())
        self.send_thread.daemon = True   #gjør at tråden avsluttes når programmet som bruker kalssen Arduino avsluttes
        self.send_thread.start()
    
    def _send_loop(self):
        while True:
            data = self.send_queue.get()
            if self.serial.is_open():
                self.serial.write(data.encode())
            self.send_queue.task_done() #markerer at en oppgave i køen er fullført, noe som er viktig for å unngå at tråden blir blokkert ved full kø.

    def send(self, data: str) -> None:
        """Tar seg av å encode til bytes!
        """
        self.send_queue.put(data)

    def read(self) -> str:
        data = self.serial.readline()
        return data.decode()

    def close(self) -> None:
        self.send("0,0,0,0")
        self.serial.close()