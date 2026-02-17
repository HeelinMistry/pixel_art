

class PathingLayer:
    def __init__(self, width, height):
        # 0.0 = No path, 1.0 = Fully established road
        self.grid = [[0.0 for _ in range(height)] for _ in range(width)]

    def reinforce(self, x, y, amount=0.01):
        self.grid[x][y] = min(1.0, self.grid[x][y] + amount)

    def decay(self, amount=0.001):
        """Paths fade if not used."""
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                self.grid[x][y] = max(0.0, self.grid[x][y] - amount)