from .base_ant import BaseAnt
import random

class QueenAgent(BaseAnt):
    """
    The heart of the colony using Mesa 3.0+ features.
    """
    def __init__(self, model):
        super().__init__(model)
        self.state = "REPRODUCING"
        self.energy = 500  # Queens are much hardier
        self.max_age = 5000 # Queens live a long time
        self.egg_laying_rate = 0.1 # Probability of laying an egg per tick

    def step(self):
        """Queen behavior: lays eggs and consumes colony food."""
        if not self.model: return
        super().step()
        
        # 1. Consume colony food
        if self.model.food_stockpile > 0:
            self.model.food_stockpile -= 0.1
            self.energy = min(self.energy + 5, 500)
        else:
            self.energy -= 2
            
        # 2. Reproduce (lay eggs)
        if self.state == "REPRODUCING" and random.random() < self.egg_laying_rate:
            self.lay_egg()

    def lay_egg(self):
        """Adds to the model's brood count."""
        self.model.brood_count += 1
