from .base_ant import BaseAnt
from ..world.cell import FoodSource, NestCell
import random
import math

class WorkerAgent(BaseAnt):
    """
    A worker ant responsible for foraging, nursing, and defense.
    """
    def __init__(self, model):
        super().__init__(model)
        self.state = "FORAGING" # FORAGING, RETURNING
        self.max_pheromone = 5.0 # Max pheromone intensity it can lay

    def step(self):
        """Worker behavior: forages for food or returns to colony."""
        if not self.model: return
        super().step()
        
        # 1. State-Based Logic
        if self.state == "FORAGING":
            # 2. Movement Logic: Follow Pheromones or Random Walk
            new_pos = self.sense_and_move()
            if new_pos:
                self.move_to(new_pos)
            
            # 3. Foraging Check
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            for obj in cell_contents:
                if isinstance(obj, FoodSource) and obj.amount > 0:
                    self.inventory = obj.harvest(self.inventory_cap)
                    self.state = "RETURNING"
                    self.energy = min(self.energy + 20, 100)
                    break
        
        elif self.state == "RETURNING":
            self.lay_pheromone()
            
            # Nest is at the center
            nest_pos = (self.model.width // 2, self.model.height // 2)
            
            # Find neighbors and pick one closest to nest
            neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
            if neighbors:
                best_neighbor = min(neighbors, key=lambda n: math.dist(n, nest_pos))
                self.move_to(best_neighbor)
            
            # Check if returned to nest
            if self.pos == nest_pos:
                self.model.food_stockpile += self.inventory
                self.inventory = 0
                self.state = "FORAGING"
                self.energy = 100

    def lay_pheromone(self):
        """Adds pheromone to the current cell."""
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if hasattr(obj, 'add_pheromone'):
                obj.add_pheromone(self.max_pheromone)

    def sense_and_move(self):
        """Moves toward pheromones or randomly explores within boundaries."""
        # Mesa's get_neighborhood with torus=False naturally respects boundaries
        neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
        
        if not neighbors:
            return self.pos

        random.shuffle(neighbors)
        
        # 1. Check for neighbors with food first
        for n in neighbors:
            for obj in self.model.grid.get_cell_list_contents([n]):
                if isinstance(obj, FoodSource) and obj.amount > 0:
                    return n
        
        # 2. Weighted Random Choice based on Pheromones
        neighbor_pheromones = []
        for n in neighbors:
            p_level = 0.0
            for obj in self.model.grid.get_cell_list_contents([n]):
                if hasattr(obj, 'pheromone_level'):
                    p_level += obj.pheromone_level
            neighbor_pheromones.append(p_level + 0.1)
        
        return random.choices(neighbors, weights=neighbor_pheromones, k=1)[0]
