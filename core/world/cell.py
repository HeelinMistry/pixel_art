import mesa
import random

class PheromoneCell(mesa.Agent):
    """
    Every cell on the grid has this agent to manage pheromones.
    """
    def __init__(self, model):
        super().__init__(model)
        self.pheromone_level = 0.0
        self.decay_rate = 0.03
        self.max_pheromone = 100.0

    def step(self):
        """Naturally decay pheromones over time."""
        if self.pheromone_level > 0:
            self.pheromone_level = max(0, self.pheromone_level - self.decay_rate)

    def add_pheromone(self, amount):
        self.pheromone_level = min(self.max_pheromone, self.pheromone_level + amount)

class NestCell(PheromoneCell):
    """A cell belonging to the nest."""
    def __init__(self, model):
        super().__init__(model)

class FoodSource(PheromoneCell):
    """A cell containing food resources."""
    def __init__(self, model, amount=100):
        super().__init__(model)
        self.amount = amount
        self.initial_amount = amount

    def step(self):
        super().step()
        # Slow regrowth only if NOT completely depleted (optional behavior)
        if 0 < self.amount < self.initial_amount and random.random() < 0.005:
            self.amount += 1

    def harvest(self, amount):
        gathered = min(self.amount, amount)
        self.amount -= gathered
        return gathered
