import mesa
import random

class EnvironmentalAgent(mesa.Agent):
    """
    Base class for static environmental objects in the grid.
    """
    def __init__(self, model):
        super().__init__(model)
        self.pheromone_level = 0.0
        self.max_pheromone = 100.0
        self.decay_rate = 0.05

    def step(self):
        """Decay pheromones over time."""
        if self.pheromone_level > 0:
            self.pheromone_level = max(0, self.pheromone_level - self.decay_rate)

    def add_pheromone(self, amount):
        self.pheromone_level = min(self.max_pheromone, self.pheromone_level + amount)

class NestCell(EnvironmentalAgent):
    """
    A cell representing part of the colony's nest.
    """
    def __init__(self, model, cell_type="nest"):
        super().__init__(model)
        self.cell_type = cell_type # 'nest', 'tunnel', 'chamber'

class FoodSource(EnvironmentalAgent):
    """
    A cell representing a food resource outside the nest.
    """
    def __init__(self, model, amount=100):
        super().__init__(model)
        self.amount = amount 
        self.initial_amount = amount

    def step(self):
        super().step()
        # Food source might regrow very slowly if not empty
        if 0 < self.amount < self.initial_amount and random.random() < 0.01:
            self.amount += 1

    def harvest(self, amount):
        """Ant calls this to gather food."""
        gathered = min(self.amount, amount)
        self.amount -= gathered
        return gathered
