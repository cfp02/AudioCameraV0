from src.audiocamera import MicArrayInterface, ArrayVisualizer
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

def main():
    # Initialize microphone interface
    mic_array = MicArrayInterface()
    if not mic_array.serial:
        return
    
    # Initialize visualizer
    visualizer = ArrayVisualizer()
    
    # Create animation
    anim = FuncAnimation(
        visualizer.fig,
        visualizer.update,
        fargs=(mic_array.serial,),
        interval=visualizer.update_interval,
        blit=True,
        cache_frame_data=False
    )
    
    # Set plot limits
    visualizer.ax1.set_xlim(0, visualizer.window_size)
    visualizer.ax2.set_xlim(0, visualizer.window_size)
    
    # Show plot
    plt.tight_layout()
    plt.show()
    
    # Cleanup
    mic_array.close()

if __name__ == '__main__':
    main() 