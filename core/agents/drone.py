from .base_ant import BaseAnt
import random

class DroneAgent(BaseAnt):
    """
    Male ants using Mesa 3.0+ features.
    Drones are kept strictly within boundaries.
    """
    def __init__(self, model):
        super().__init__(model)
        self.state = "REPRODUCING"
        self.energy = 50
        self.max_age = 200
        self.mating_success_rate = 0.01

    def step(self):
        """Drone behavior: consumes food and looks for mating opportunities."""
        if not self.model: return
        super().step()
        
        # 1. Consume colony food
        if self.model.food_stockpile > 0:
            self.model.food_stockpile -= 0.05
            self.energy = min(self.energy + 2, 50)
        else:
            self.energy -= 1
            
        # 2. Mating Logic (Phase 3: Reproductive)
        if self.model.phase == "REPRODUCTIVE":
            agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
            for agent in agents_in_cell:
                # Check for Queen
                if "QueenAgent" in str(type(agent)):
                    if random.random() < self.mating_success_rate:
                        self.remove()
                        return
        
        # 3. Random movement within grid boundaries
        neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
        if neighbors:
            new_pos = random.choice(neighbors)
            self.move_to(new_pos)
