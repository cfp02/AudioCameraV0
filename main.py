import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import sys

# Configure these parameters
SERIAL_PORT = '/dev/cu.usbmodem2101'
BAUD_RATE = 115200
WINDOW_SIZE = 500  # Reduced from 2000 for smoother display
DISPLAY_DOWNSAMPLE = 5  # Reduced from 10
UPDATE_INTERVAL = 50

# Scaling factors based on observed data ranges
SCALING_FACTORS = [1.0, 1.0, 50.0, 50.0]  # More conservative scaling

# Create figure for plotting
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
fig.suptitle('Quad Microphone Audio Waveforms')

# Setup plots for all channels
ax1.set_ylabel('Amplitude')
ax1.set_ylim(-35000, 35000)  # Adjusted based on your data
line1_mic1, = ax1.plot([], [], 'c-', linewidth=1, label='Mic 1')
line1_mic2, = ax1.plot([], [], 'm-', linewidth=1, label='Mic 2')
line1_mic3, = ax1.plot([], [], 'y-', linewidth=1, label='Mic 3')
line1_mic4, = ax1.plot([], [], 'g-', linewidth=1, label='Mic 4')

# Setup downsampled plots
ax2.set_xlabel('Sample')
ax2.set_ylabel('Amplitude')
ax2.set_ylim(-35000, 35000)  # Adjusted based on your data
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

def animate(frame):
    try:
        while ser.in_waiting:
            try:
                line = ser.readline().decode().strip()
                values = list(map(int, line.split(',')))
                
                if len(values) == 4:
                    # Add to raw data
                    for i in range(4):
                        raw_data[i].append(values[i] * SCALING_FACTORS[i])
                    
                    # Add to downsampled data every Nth sample
                    if len(raw_data[0]) % DISPLAY_DOWNSAMPLE == 0:
                        for i in range(4):
                            downsampled_data[i].append(values[i] * SCALING_FACTORS[i])
            except (ValueError, UnicodeDecodeError):
                continue
        
        # Update plots
        line1_mic1.set_data(x_data_raw, list(raw_data[0]))
        line1_mic2.set_data(x_data_raw, list(raw_data[1]))
        line1_mic3.set_data(x_data_raw, list(raw_data[2]))
        line1_mic4.set_data(x_data_raw, list(raw_data[3]))
        
        line2_mic1.set_data(x_data_downsampled, list(downsampled_data[0]))
        line2_mic2.set_data(x_data_downsampled, list(downsampled_data[1]))
        line2_mic3.set_data(x_data_downsampled, list(downsampled_data[2]))
        line2_mic4.set_data(x_data_downsampled, list(downsampled_data[3]))
        
        return line1_mic1, line1_mic2, line1_mic3, line1_mic4, line2_mic1, line2_mic2, line2_mic3, line2_mic4
    
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        sys.exit(1)

# Create animation
anim = FuncAnimation(
    fig, 
    animate, 
    interval=UPDATE_INTERVAL,
    blit=True,
    cache_frame_data=False
)

# Set fixed axis limits
ax1.set_xlim(0, WINDOW_SIZE)
ax2.set_xlim(0, WINDOW_SIZE)

plt.tight_layout()
plt.show()

# Cleanup
ser.close() 