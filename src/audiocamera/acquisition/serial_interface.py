import serial
import serial.tools.list_ports

class MicArrayInterface:
    def __init__(self, port='/dev/cu.usbmodem2101', baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        try:
            self.serial = serial.Serial(port, baud_rate)
        except serial.SerialException:
            print(f"Error: Couldn't open port {port}")
            print("Available ports:")
            ports = serial.tools.list_ports.comports()
            for p in ports:
                print(f"  {p.device}")
            self.serial = None
            
    def read_frame(self):
        """Read one frame of data from all microphones."""
        if not self.serial:
            return None
        return self.serial
        
    def close(self):
        if self.serial:
            self.serial.close() 