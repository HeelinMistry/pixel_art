from .base_ant import BaseAnt
from .brood import BroodAgent
import random

class QueenAgent(BaseAnt):
    """
    The heart of the colony using Mesa 3.0+ features.
    Behavior is influenced by colony phase and localized feeding.
    """
    def __init__(self, model):
        super().__init__(model)
        self.state = "REPRODUCING"
        self.max_energy = 1000.0
        self.energy = 1000.0
        self.max_health = 500.0
        self.health = 500.0
        self.max_age = 10000 
        self.metabolism_rate = 0.05 
        self.lay_egg_cost = 1.5
        self.base_egg_laying_rate = 0.05

    def step(self):
        """Queen behavior: lays eggs based on colony phase and resources."""
        if not self.model: return
        super().step()
        if self.health <= 0: return

        # 1. Localized Self-Preservation (withdraw from NestCell)
        if self.energy < (self.max_energy * 0.8):
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            for obj in cell_contents:
                from core.world.cell import NestCell
                if isinstance(obj, NestCell):
                    withdrawn = obj.withdraw_food(1.0)
                    self.eat(amount=withdrawn)
                    break
            
        # 2. Dynamic Reproduction
        egg_rate = self.calculate_egg_rate()
        if self.state == "REPRODUCING" and random.random() < egg_rate:
            if self.energy > self.lay_egg_cost:
                self.lay_egg()
                self.energy -= self.lay_egg_cost

    def calculate_egg_rate(self):
        # Dynamically scale rate based on local nest food (Queen smells the stockpile)
        local_food = 0
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            from core.world.cell import NestCell
            if isinstance(obj, NestCell):
                local_food = obj.stored_food
                break

        rate = self.base_egg_laying_rate
        if self.model.phase == "ERGONOMIC": rate *= 2.0
        elif self.model.phase == "REPRODUCTIVE": rate *= 1.5
        
        # Scale by food
        if local_food < 10: rate *= 0.2
        elif local_food < 25: rate *= 0.5
        return rate

    def lay_egg(self):
        """Creates a new BroodAgent (egg)."""
        new_brood = BroodAgent(self.model, stage="EGG")
        self.model.grid.place_agent(new_brood, self.pos)
