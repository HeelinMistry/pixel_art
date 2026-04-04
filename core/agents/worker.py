from .base_ant import BaseAnt
from ..world.cell import FoodSource, PheromoneCell
import random
import math

class WorkerAgent(BaseAnt):
    """
    A worker ant that uses pheromones to create trails to food sources.
    Incorporates 'Exploration vs Exploitation' logic and food attraction zones.
    """
    def __init__(self, model):
        super().__init__(model)
        self.state = "FORAGING" # FORAGING, RETURNING
        self.max_pheromone = 10.0 # Intensity of pheromones it can lay
        self.exploration_rate = 0.10 # Reduced slightly as attraction zone helps discovery
        self.scent_radius = 4 # Radius at which ants can 'smell' food sources

    def step(self):
        """Worker behavior with attraction zones and pheromone tracking."""
        if not self.model: return
        super().step()
        
        # 1. State-Based Logic
        if self.state == "FORAGING":
            # 2. Movement Logic: Follow Scent, Pheromones, or Random Explore
            new_pos = self.sense_and_move()
            if new_pos:
                self.move_to(new_pos)
            
            # 3. Foraging Check (Immediate cell)
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            for obj in cell_contents:
                if isinstance(obj, FoodSource) and obj.amount > 0:
                    self.inventory = obj.harvest(self.inventory_cap)
                    self.state = "RETURNING"
                    self.energy = 100
                    break
        
        elif self.state == "RETURNING":
            # 4. Lay Pheromones ONLY when returning with food
            self.lay_pheromone()
            
            # 5. Pathfinding back to nest
            cx, cy = self.model.width // 2, self.model.height // 2
            nest_pos = (cx, cy)
            
            neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
            if neighbors:
                best_neighbor = min(neighbors, key=lambda n: math.dist(n, nest_pos))
                self.move_to(best_neighbor)
            
            # 6. Check if returned to nest
            if self.pos == nest_pos:
                self.model.food_stockpile += self.inventory
                self.inventory = 0
                self.state = "FORAGING"
                self.energy = 100 # Replenish energy

    def lay_pheromone(self):
        """Adds pheromone to all PheromoneCell agents in the current cell."""
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if hasattr(obj, 'add_pheromone'):
                obj.add_pheromone(self.max_pheromone)

    def sense_and_move(self):
        """Moves toward pheromones or randomly explores."""
        neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
        if not neighbors: return self.pos
        random.shuffle(neighbors)
        
        # 1. SCENT CHECK: Can we smell food in a wider radius?
        # This creates the 'attraction zone' around food sources.
        nearby_cells = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=self.scent_radius)
        food_locations = []
        for cell_pos in nearby_cells:
            for obj in self.model.grid.get_cell_list_contents([cell_pos]):
                if isinstance(obj, FoodSource) and obj.amount > 0:
                    food_locations.append(cell_pos)
        
        if food_locations:
            # Move towards the closest food source we smell
            closest_food = min(food_locations, key=lambda f: math.dist(self.pos, f))
            # Pick the neighbor that gets us closest to that food
            best_n = min(neighbors, key=lambda n: math.dist(n, closest_food))
            return best_n

        # 2. EXPLORATION: Occasionally ignore pheromones to discover new areas
        if random.random() < self.exploration_rate:
            return random.choice(neighbors)
        
        # 3. PHEROMONE TRACKING: Weighted Choice based on Pheromone Levels
        neighbor_pheromones = []
        for n in neighbors:
            p_level = 0.0
            for obj in self.model.grid.get_cell_list_contents([n]):
                if isinstance(obj, PheromoneCell):
                    p_level += obj.pheromone_level
            # 0.1 baseline probability
            neighbor_pheromones.append(p_level + 0.1)
        
        return random.choices(neighbors, weights=neighbor_pheromones, k=1)[0]
