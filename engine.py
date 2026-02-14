import numpy as np
import rules.conway

class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = np.zeros((rows, cols), dtype=int)
        self.heat_map = np.zeros((rows, cols), dtype=float)
        self.current_rule = rules.conway.apply_rules

    def update(self):
        """
        Applies the currently selected rule to the grid and updates the heatmap.
        """
        new_cells = self.current_rule(self.cells)
        
        # Heatmap Logic:
        # If alive, increment heat (age).
        # If dead, reset heat to 0.
        
        # We use np.where to handle both cases in one go.
        # If the cell is alive in the new state, we take its current heat value + 1.
        # If it is dead, we set it to 0.
        self.heat_map = np.where(new_cells == 1, self.heat_map + 1, 0)

        self.cells = new_cells

    def set_rule(self, rule_function):
        self.current_rule = rule_function

    def set_cell(self, row, col, state):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.cells[row, col] = state
            if state == 1:
                self.heat_map[row, col] = 1
            else:
                self.heat_map[row, col] = 0

    def toggle_cell(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.cells[row, col] = 1 - self.cells[row, col]
            if self.cells[row, col] == 1:
                self.heat_map[row, col] = 1
            else:
                self.heat_map[row, col] = 0
