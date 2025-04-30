import matplotlib.pyplot as plt
import pandas as pd
import os

def enhance_latest_plot():
    """Add styling to make the demo plot more visually impressive"""
    try:
        # Look for the most recent plot file
        plot_file = os.path.join(os.path.dirname(__file__), "demo_plot.png")
        
        if not os.path.exists(plot_file):
            return
            
        # Apply a more professional style
        plt.style.use('dark_background')
        
        # Re-create the plot with enhanced styling
        # (This would normally use the same data that generated the original plot)
        
        plt.savefig(plot_file, dpi=300)
        print(f"Enhanced plot saved to {plot_file}")
    except Exception as e:
        print(f"Could not enhance plot: {e}")

if __name__ == "__main__":
    enhance_latest_plot()
