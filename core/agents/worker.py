from .base_ant import BaseAnt
from ..world.cell import FoodSource, PheromoneCell
from .brood import BroodAgent # Import BroodAgent
import random
import math

class WorkerAgent(BaseAnt):
    """
    A worker ant that uses pheromones to create trails to food sources.
    Incorporates task-switching logic aligned with colony phases and multi-stage brood care.
    Includes Physiology: Energy, health, and metabolism.
    """
    def __init__(self, model):
        super().__init__(model)
        self.state = "FORAGING" # FORAGING, RETURNING, NURSING
        self.max_pheromone = 10.0 # Intensity of pheromones it can lay
        self.exploration_rate = 0.10 
        self.scent_radius = 4 # Radius at which ants can 'smell' food sources
        
        # Energy costs for actions
        self.move_cost = 0.05
        self.forage_cost = 0.5
        self.nurse_cost = 1.0

    def step(self):
        """Worker behavior with phase-aware task switching."""
        if not self.model: return
        
        # 1. Base Physiology: Metabolism, Starvation, Recovery (handled by BaseAnt)
        super().step()
        
        if self.health <= 0: return

        # 2. Digestion / Feeding (Self-Preservation)
        self.check_self_feeding()

        # 3. Dynamic Task Selection
        self.update_task()

        # 4. State-Based Logic
        if self.state == "FORAGING":
            self.execute_foraging()
        
        elif self.state == "RETURNING":
            self.execute_returning()

        elif self.state == "NURSING":
            self.execute_nursing()

    def update_task(self):
        """
        Determines the current task based on colony needs and phase.
        Tasks: FORAGING, NURSING
        """
        # If carrying food, keep returning
        if self.state == "RETURNING" and self.inventory > 0:
            return

        # Colony needs assessment
        food_level = self.model.food_stockpile
        brood_count = self.model.brood_count
        
        # Phase-based behavior weighting
        if self.model.phase == "FOUNDING":
            if food_level < 50:
                self.state = "FORAGING"
            elif brood_count > 0 and random.random() < 0.6:
                self.state = "NURSING"
            else:
                self.state = "FORAGING"

        elif self.model.phase == "ERGONOMIC":
            if food_level < 100:
                self.state = "FORAGING"
            elif brood_count > 10 and random.random() < 0.7:
                self.state = "NURSING"
            else:
                self.state = "FORAGING"

        elif self.model.phase == "REPRODUCTIVE":
            if food_level < 500:
                self.state = "FORAGING"
            elif brood_count > 20 and random.random() < 0.5:
                self.state = "NURSING"
            else:
                self.state = "FORAGING"

    def execute_foraging(self):
        """Logic for foraging: finding food sources."""
        new_pos = self.sense_and_move()
        if new_pos:
            self.move_to(new_pos)
            self.energy -= self.move_cost
        
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if isinstance(obj, FoodSource) and obj.amount > 0:
                self.inventory = obj.harvest(self.inventory_cap)
                self.energy -= self.forage_cost
                self.state = "RETURNING"
                break

    def execute_returning(self):
        """Logic for returning to the nest with food."""
        self.lay_pheromone()
        
        cx, cy = self.model.width // 2, self.model.height // 2
        nest_pos = (cx, cy)
        
        neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
        if neighbors:
            best_neighbor = min(neighbors, key=lambda n: math.dist(n, nest_pos))
            self.move_to(best_neighbor)
            self.energy -= self.move_cost
        
        if self.pos == nest_pos:
            self.model.food_stockpile += self.inventory
            self.inventory = 0

    def execute_nursing(self):
        """Logic for nursing: specifically feeding larvae at the nest."""
        cx, cy = self.model.width // 2, self.model.height // 2
        nest_pos = (cx, cy)

        if self.pos != nest_pos:
            neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
            if neighbors:
                best_neighbor = min(neighbors, key=lambda n: math.dist(n, nest_pos))
                self.move_to(best_neighbor)
                self.energy -= self.move_cost
        else:
            # At the nest, look for larvae to feed
            nearby_brood = [a for a in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(a, BroodAgent)]
            larvae = [b for b in nearby_brood if b.stage == "LARVA"]
            
            if larvae and self.model.food_stockpile > 0.5:
                # Select a random larva to feed
                target_larva = random.choice(larvae)
                if target_larva.feed(amount=1):
                    self.model.food_stockpile -= 0.5
                    self.energy -= self.nurse_cost
                
                if random.random() < 0.2:
                    self.state = "FORAGING"
            else:
                # No larvae to feed or no food, maybe check for other brood care (optional)
                # For now, just go back to foraging
                self.state = "FORAGING"

    def check_self_feeding(self):
        """Workers eat if they are hungry."""
        if self.energy < (self.max_energy * 0.7):
            cx, cy = self.model.width // 2, self.model.height // 2
            if self.pos == (cx, cy) and self.model.food_stockpile > 0:
                eaten = self.eat(amount=1.0)
                self.model.food_stockpile -= eaten
            elif self.inventory > 0:
                eaten = self.eat(amount=min(1.0, self.inventory))
                self.inventory -= eaten

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
        
        nearby_cells = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=self.scent_radius)
        food_locations = []
        for cell_pos in nearby_cells:
            for obj in self.model.grid.get_cell_list_contents([cell_pos]):
                if isinstance(obj, FoodSource) and obj.amount > 0:
                    food_locations.append(cell_pos)
        
        if food_locations:
            closest_food = min(food_locations, key=lambda f: math.dist(self.pos, f))
            best_n = min(neighbors, key=lambda n: math.dist(n, closest_food))
            return best_n

        if random.random() < self.exploration_rate:
            return random.choice(neighbors)
        
        neighbor_pheromones = []
        for n in neighbors:
            p_level = 0.0
            for obj in self.model.grid.get_cell_list_contents([n]):
                if isinstance(obj, PheromoneCell):
                    p_level += obj.pheromone_level
            neighbor_pheromones.append(p_level + 0.1)
        
        return random.choices(neighbors, weights=neighbor_pheromones, k=1)[0]
