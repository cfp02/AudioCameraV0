import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import serial
import sys

class ArrayVisualizer:
    def __init__(self, window_size=500, downsample=5, update_interval=50):
        # Store parameters
        self.window_size = window_size
        self.downsample = downsample
        self.update_interval = update_interval
        self.scaling_factors = [1.0, 1.0, 50.0, 50.0]
        
        # Create figure and subplots
        plt.style.use('dark_background')
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.suptitle('Quad Microphone Audio Waveforms')
        
        # Setup raw data plot
        self.ax1.set_ylabel('Amplitude')
        self.ax1.set_ylim(-35000, 35000)
        self.line1_mic1, = self.ax1.plot([], [], 'c-', linewidth=1, label='Mic 1')
        self.line1_mic2, = self.ax1.plot([], [], 'm-', linewidth=1, label='Mic 2')
        self.line1_mic3, = self.ax1.plot([], [], 'y-', linewidth=1, label='Mic 3')
        self.line1_mic4, = self.ax1.plot([], [], 'g-', linewidth=1, label='Mic 4')
        
        # Setup downsampled plot
        self.ax2.set_xlabel('Sample')
        self.ax2.set_ylabel('Amplitude')
        self.ax2.set_ylim(-35000, 35000)
        self.line2_mic1, = self.ax2.plot([], [], 'c-', linewidth=1, label='Mic 1 (Downsampled)')
        self.line2_mic2, = self.ax2.plot([], [], 'm-', linewidth=1, label='Mic 2 (Downsampled)')
        self.line2_mic3, = self.ax2.plot([], [], 'y-', linewidth=1, label='Mic 3 (Downsampled)')
        self.line2_mic4, = self.ax2.plot([], [], 'g-', linewidth=1, label='Mic 4 (Downsampled)')
        
        # Add legends
        self.ax1.legend(loc='upper right')
        self.ax2.legend(loc='upper right')
        
        # Initialize data storage
        self.raw_data = [deque([0] * window_size, maxlen=window_size) for _ in range(4)]
        self.downsampled_data = [deque([0] * (window_size // downsample), 
                                      maxlen=window_size // downsample) for _ in range(4)]
        
        # Create x-axis data
        self.x_data_raw = np.arange(0, window_size, 1)
        self.x_data_downsampled = np.arange(0, window_size, downsample)
        
    def update(self, frame, ser):
        try:
            while ser.in_waiting:
                try:
                    line = ser.readline().decode().strip()
                    values = list(map(int, line.split(',')))
                    
                    if len(values) == 4:
                        # Add to raw data
                        for i in range(4):
                            self.raw_data[i].append(values[i] * self.scaling_factors[i])
                        
                        # Add to downsampled data every Nth sample
                        if len(self.raw_data[0]) % self.downsample == 0:
                            for i in range(4):
                                self.downsampled_data[i].append(values[i] * self.scaling_factors[i])
                except (ValueError, UnicodeDecodeError):
                    continue
            
            # Update plots
            self.line1_mic1.set_data(self.x_data_raw, list(self.raw_data[0]))
            self.line1_mic2.set_data(self.x_data_raw, list(self.raw_data[1]))
            self.line1_mic3.set_data(self.x_data_raw, list(self.raw_data[2]))
            self.line1_mic4.set_data(self.x_data_raw, list(self.raw_data[3]))
            
            self.line2_mic1.set_data(self.x_data_downsampled, list(self.downsampled_data[0]))
            self.line2_mic2.set_data(self.x_data_downsampled, list(self.downsampled_data[1]))
            self.line2_mic3.set_data(self.x_data_downsampled, list(self.downsampled_data[2]))
            self.line2_mic4.set_data(self.x_data_downsampled, list(self.downsampled_data[3]))
            
            return (self.line1_mic1, self.line1_mic2, self.line1_mic3, self.line1_mic4,
                    self.line2_mic1, self.line2_mic2, self.line2_mic3, self.line2_mic4)
        
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            sys.exit(1) 