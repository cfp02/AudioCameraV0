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
fig.suptitle('Quad Microphone Audio Waveforms')

# Setup plots for all channels
ax1.set_ylabel('Amplitude')
ax1.set_ylim(-32768, 32768)
line1_mic1, = ax1.plot([], [], 'c-', linewidth=1, label='Mic 1')
line1_mic2, = ax1.plot([], [], 'm-', linewidth=1, label='Mic 2')
line1_mic3, = ax1.plot([], [], 'y-', linewidth=1, label='Mic 3')
line1_mic4, = ax1.plot([], [], 'g-', linewidth=1, label='Mic 4')

# Setup downsampled plots
ax2.set_xlabel('Sample')
ax2.set_ylabel('Amplitude')
ax2.set_ylim(-32768, 32768)
line2_mic1, = ax2.plot([], [], 'c-', linewidth=1, label='Mic 1 (Downsampled)')
line2_mic2, = ax2.plot([], [], 'm-', linewidth=1, label='Mic 2 (Downsampled)')
line2_mic3, = ax2.plot([], [], 'y-', linewidth=1, label='Mic 3 (Downsampled)')
line2_mic4, = ax2.plot([], [], 'g-', linewidth=1, label='Mic 4 (Downsampled)')

# Add legends
ax1.legend(loc='upper right')
ax2.legend(loc='upper right')

# Initialize with zeros
raw_data = [deque([0] * WINDOW_SIZE, maxlen=WINDOW_SIZE) for _ in range(4)]
downsampled_data = [deque([0] * (WINDOW_SIZE // DISPLAY_DOWNSAMPLE), maxlen=WINDOW_SIZE // DISPLAY_DOWNSAMPLE) for _ in range(4)]

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
    # Initialize all lines with zeros
    line1_mic1.set_data(x_data_raw, raw_data[0])
    line1_mic2.set_data(x_data_raw, raw_data[1])
    line1_mic3.set_data(x_data_raw, raw_data[2])
    line1_mic4.set_data(x_data_raw, raw_data[3])
    line2_mic1.set_data(x_data_downsampled, downsampled_data[0])
    line2_mic2.set_data(x_data_downsampled, downsampled_data[1])
    line2_mic3.set_data(x_data_downsampled, downsampled_data[2])
    line2_mic4.set_data(x_data_downsampled, downsampled_data[3])
    return line1_mic1, line1_mic2, line1_mic3, line1_mic4, line2_mic1, line2_mic2, line2_mic3, line2_mic4

def animate(frame):
    try:
        # Read data from serial
        while ser.in_waiting:
            try:
                # Read CSV format: "mic1,mic2,mic3,mic4"
                line = ser.readline().decode().strip()
                values = list(map(int, line.split(',')))
                
                if len(values) == 4:
                    # Add to raw data
                    for i in range(4):
                        raw_data[i].append(values[i])
                    
                    # Add to downsampled data every Nth sample
                    if len(raw_data[0]) % DISPLAY_DOWNSAMPLE == 0:
                        for i in range(4):
                            downsampled_data[i].append(values[i])
            except (ValueError, UnicodeDecodeError):
                continue
        
        # Update plots
        line1_mic1.set_data(x_data_raw, raw_data[0])
        line1_mic2.set_data(x_data_raw, raw_data[1])
        line1_mic3.set_data(x_data_raw, raw_data[2])
        line1_mic4.set_data(x_data_raw, raw_data[3])
        line2_mic1.set_data(x_data_downsampled, downsampled_data[0])
        line2_mic2.set_data(x_data_downsampled, downsampled_data[1])
        line2_mic3.set_data(x_data_downsampled, downsampled_data[2])
        line2_mic4.set_data(x_data_downsampled, downsampled_data[3])
        
        return line1_mic1, line1_mic2, line1_mic3, line1_mic4, line2_mic1, line2_mic2, line2_mic3, line2_mic4
    
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