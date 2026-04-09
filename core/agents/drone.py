from .base_ant import BaseAnt
import random

class DroneAgent(BaseAnt):
    """
    Male ants using Mesa 3.0+ features.
    Drones are kept strictly within boundaries.
    Includes Physiology: Energy, health, and metabolism.
    """
    def __init__(self, model):
        super().__init__(model)
        self.state = "REPRODUCING"
        self.energy = 50.0
        self.max_energy = 50.0
        self.max_age = 500
        self.mating_success_rate = 0.05
        
        self.metabolism_rate = 0.2 # Drones have high metabolism

    def step(self):
        """Drone behavior: consumes food and looks for mating opportunities."""
        if not self.model: return
        
        # 1. Base Physiology: Metabolism, Starvation, Recovery (handled by BaseAnt)
        super().step()
        
        if self.health <= 0: return

        # 2. Consume colony food
        if self.energy < (self.max_energy * 0.5):
            if self.model.food_stockpile > 1.0:
                eaten = self.eat(amount=1.0)
                self.model.food_stockpile -= eaten
            
        # 3. Mating Logic (Phase 3: Reproductive)
        if self.model.phase == "REPRODUCTIVE":
            agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
            for agent in agents_in_cell:
                # Check for Queen
                from .queen import QueenAgent
                if isinstance(agent, QueenAgent):
                    if random.random() < self.mating_success_rate:
                        self.remove()
                        return
        
        # 4. Random movement within grid boundaries
        neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
        if neighbors:
            new_pos = random.choice(neighbors)
            self.move_to(new_pos)
            self.energy -= 0.1 # Movement cost
