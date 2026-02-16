import random


class Environment:
    def __init__(self, width, height, initial_state=None):
        self.width = width
        self.height = height

        # 1. Load starting point if provided
        if initial_state:
            self.grid = initial_state
        else:
            # Default: Grid filled with random resource levels (0 to 5)
            self.grid = [[random.randint(0, 10) for _ in range(height)] for _ in range(width)]

    def get_resource(self, x, y):
        return self.grid[x][y]

    def consume(self, x, y, preferred_amount):
        """Take up to preferred_amount, but don't go below zero."""
        available = self.grid[x][y]
        amount_taken = min(available, preferred_amount)
        self.grid[x][y] -= amount_taken
        return amount_taken

    def step(self):
        """Environment physics: e.g., Regrow resources slowly over time."""
        # for x in range(self.width):
        #     for y in range(self.height):
        #         if self.grid[x][y] < 5 and random.random() < 0.1:
        #             self.grid[x][y] += 1
        pass

    def get_stats(self):
        """Aggregate environment data."""
        total_resources = sum(sum(row) for row in self.grid)
        return {"total_resources": total_resources}

