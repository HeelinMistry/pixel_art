import arcade
from rendering.renderer import AntRenderer

if __name__ == "__main__":
    # Control the 'resolution' of the grid (number of hexes in a column)
    # The renderer will calculate the number of columns to fill the screen width
    GRID_RESOLUTION = 100
    
    # Run the Simulation
    # No longer passing a full params dict, just the resolution
    app = AntRenderer(1000, 1000, GRID_RESOLUTION)
    arcade.run()
