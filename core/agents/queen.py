from .base_ant import BaseAnt
import random

class QueenAgent(BaseAnt):
    """
    The heart of the colony using Mesa 3.0+ features.
    Includes Physiology: Energy, health, and metabolism.
    """
    def __init__(self, model):
        super().__init__(model)
        self.state = "REPRODUCING"
        
        # Queens are much hardier
        self.max_energy = 1000.0
        self.energy = 1000.0
        self.max_health = 500.0
        self.health = 500.0
        
        self.max_age = 10000 
        self.egg_laying_rate = 0.05 # Probability of laying an egg per tick
        
        self.metabolism_rate = 0.05 # Queens have slow metabolism when resting
        self.lay_egg_cost = 1.5

    def step(self):
        """Queen behavior: lays eggs and consumes colony food."""
        if not self.model: return
        
        # 1. Base Physiology: Metabolism, Starvation, Recovery (handled by BaseAnt)
        super().step()
        
        if self.health <= 0: return

        # 2. Consume colony food (Self-Preservation)
        if self.energy < (self.max_energy * 0.8):
            if self.model.food_stockpile > 1.0:
                eaten = self.eat(amount=1.0)
                self.model.food_stockpile -= eaten
            
        # 3. Reproduce (lay eggs)
        if self.state == "REPRODUCING" and random.random() < self.egg_laying_rate:
            if self.energy > self.lay_egg_cost:
                self.lay_egg()
                self.energy -= self.lay_egg_cost

    def lay_egg(self):
        """Adds to the model's brood count and occasionally spawns a new worker."""
        # Brood count represents developing larvae
        self.model.brood_count += 1
        
        # Every 10 eggs (on average), hatch a new worker
        # This can be refined later into a multi-stage life cycle
        if random.random() < 0.2:
            from .worker import WorkerAgent
            new_worker = WorkerAgent(self.model)
            self.model.grid.place_agent(new_worker, self.pos)
