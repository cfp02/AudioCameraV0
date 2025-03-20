import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import sys

# Configure these parameters
SERIAL_PORT = '/dev/cu.usbmodem2101'  # Your ESP32's serial port
BAUD_RATE = 115200
WINDOW_SIZE = 2000  # Number of samples to show
DISPLAY_DOWNSAMPLE = 10  # Only display every Nth sample
UPDATE_INTERVAL = 50  # Update interval in milliseconds

# Create figure for plotting
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
fig.suptitle('Real-time Audio Waveform')

# Setup main waveform plot
ax1.set_ylabel('Amplitude')
ax1.set_ylim(-32768, 32768)
line1, = ax1.plot([], [], 'c-', linewidth=1, label='Raw')

# Setup downsampled plot
ax2.set_xlabel('Sample')
ax2.set_ylabel('Amplitude')
ax2.set_ylim(-32768, 32768)
line2, = ax2.plot([], [], 'g-', linewidth=1, label='Downsampled')

# Add legends
ax1.legend(loc='upper right')
ax2.legend(loc='upper right')

# Initialize with zeros
raw_data = deque([0] * WINDOW_SIZE, maxlen=WINDOW_SIZE)
downsampled_data = deque([0] * (WINDOW_SIZE // DISPLAY_DOWNSAMPLE), maxlen=WINDOW_SIZE // DISPLAY_DOWNSAMPLE)
x_data_raw = np.arange(0, WINDOW_SIZE, 1)
x_data_downsampled = np.arange(0, WINDOW_SIZE, DISPLAY_DOWNSAMPLE)

# Initialize serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
except serial.SerialException:
    print(f"Error: Couldn't open port {SERIAL_PORT}")
    print("Available ports:")
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"  {port.device}")
    sys.exit(1)

def init():
    line1.set_data(x_data_raw, raw_data)
    line2.set_data(x_data_downsampled, downsampled_data)
    return line1, line2

def animate(frame):
    try:
        # Read data from serial
        while ser.in_waiting:
            try:
                value = int(ser.readline().decode().strip())
                raw_data.append(value)
                # Only add to downsampled data every Nth sample
                if len(raw_data) % DISPLAY_DOWNSAMPLE == 0:
                    downsampled_data.append(value)
            except (ValueError, UnicodeDecodeError):
                continue
        
        # Update plots
        line1.set_data(x_data_raw, raw_data)
        line2.set_data(x_data_downsampled, downsampled_data)
        return line1, line2
    except serial.SerialException:
        print("Serial connection lost!")
        sys.exit(1)

# Create animation with explicit save_count
anim = FuncAnimation(
    fig, 
    animate, 
    init_func=init, 
    interval=UPDATE_INTERVAL, 
    blit=True,
    cache_frame_data=False,
    save_count=100
)

# Set fixed axis limits
ax1.set_xlim(0, WINDOW_SIZE)
ax2.set_xlim(0, WINDOW_SIZE)

# Show plot with tight layout
plt.tight_layout()
plt.show()

# Cleanup
ser.close()