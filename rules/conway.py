import numpy as np

def apply_rules(cells):
    """
    Applies Conway's Game of Life rules using vectorized operations.
    This implementation treats the grid as a torus (edges wrap around).
    """
    # Count neighbors using roll (shifts the array)
    # This is much faster than iterating with loops
    neighbors = (
        np.roll(cells, 1, axis=0) + np.roll(cells, -1, axis=0) +
        np.roll(cells, 1, axis=1) + np.roll(cells, -1, axis=1) +
        np.roll(np.roll(cells, 1, axis=0), 1, axis=1) +
        np.roll(np.roll(cells, 1, axis=0), -1, axis=1) +
        np.roll(np.roll(cells, -1, axis=0), 1, axis=1) +
        np.roll(np.roll(cells, -1, axis=0), -1, axis=1)
    )
    
    # Apply rules
    new_cells = np.zeros_like(cells)
    
    # Rule 1: Any live cell with two or three live neighbours survives.
    new_cells[(cells == 1) & ((neighbors == 2) | (neighbors == 3))] = 1
    
    # Rule 2: Any dead cell with three live neighbours becomes a live cell.
    new_cells[(cells == 0) & (neighbors == 3)] = 1
    
    return new_cells