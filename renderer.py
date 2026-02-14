import pygame
import numpy as np

class Renderer:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        
        # Palette
        self.COLOR_BG = (10, 10, 10)
        self.COLOR_GRID = (40, 40, 40)
        self.COLOR_ALIVE = (0, 255, 150)

    @staticmethod
    def get_heat_color(age):
        """Maps age to a color gradient."""
        # Ensure age is an integer for bitwise operations or color values
        intensity = min(int(age * 5), 255)
        # Gradient from Blue (cold) to Red (hot)
        # (R, G, B)
        return intensity, 50, 255 - intensity

    def draw(self, screen, cells, heat_map, mode="classic"):
        screen.fill(self.COLOR_GRID)
        
        # Iterate over all cells
        for row, col in np.ndindex(cells.shape):
            cell_value = cells[row, col]
            
            if cell_value == 1:
                if mode == "heatmap":
                    color = self.get_heat_color(heat_map[row, col])
                else:
                    color = self.COLOR_ALIVE
            else:
                color = self.COLOR_BG
            
            # Draw cell with a 1px gap for the grid
            pygame.draw.rect(screen, color, (
                col * self.cell_size, 
                row * self.cell_size, 
                self.cell_size - 1, 
                self.cell_size - 1
            ))

# Wrapper for backward compatibility if needed, but we will update main.py
def draw_grid(screen, cells, heat_map, size, mode="classic"):
    r = Renderer(size)
    r.draw(screen, cells, heat_map, mode)
