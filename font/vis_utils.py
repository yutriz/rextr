import numpy as np
import matplotlib.pyplot as plt

# troubleshooting:
# qt.qpa.plugin: Could not find the Qt platform plugin "wayland" in ""
# qt.qpa.plugin: Could not find the Qt platform plugin "xcb" in ""
# This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem
# 
# try: 
#   QT_PLUGIN_PATH=/usr/lib/qt/plugins/ python foo.py


# AI-generated
def visualize_distribution(data, mode='16bit'):
    # Split 16-bit into 8-bit rows and 8-bit cols
    rows = (data >> 8) & 0xFF
    cols = data & 0xFF
    grid_size = 256

    # 2. Create a 2D Histogram (The "Rough" way)
    heatmap, xedges, yedges = np.histogram2d(
        rows, cols, 
        bins=256, 
        range=[[0, grid_size], [0, grid_size]]
    )

    # 3. Plotting
    plt.imshow(heatmap.T, origin='lower', cmap='hot', interpolation='nearest')
    plt.colorbar(label='Frequency')
    plt.title(f"Distribution Map ({mode})")
    plt.xlabel("Last Bits (Column)")
    plt.ylabel("First Bits (Row)")
    
    # Optional: Format axis to show Hex
    plt.xticks([0, 64, 128, 192, 255], ['0x00', '0x40', '0x80', '0xC0', '0xFF'])
    plt.yticks([0, 64, 128, 192, 255], ['0x00', '0x40', '0x80', '0xC0', '0xFF'])
    
    plt.savefig('distribution_map.png')
    plt.show()