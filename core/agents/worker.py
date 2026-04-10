from .base_ant import BaseAnt
from ..world.cell import FoodSource, PheromoneCell, NestCell
from .brood import BroodAgent
import random
import math

class WorkerAgent(BaseAnt):
    """
    A worker ant that uses behavioral chains. 
    Tasks are completed fully before re-evaluating in the nest.
    """
    def __init__(self, model):
        super().__init__(model)
        self.state = "IDLE" 
        
        self.max_pheromone = 10.0 
        self.exploration_rate = 0.12 # Slightly higher exploration
        self.scent_radius = 4 
        
        # Energy costs
        self.move_cost = 0.05
        self.forage_cost = 0.5
        self.nurse_cost = 0.8

    def step(self):
        """Worker behavior with State Completion logic."""
        if not self.model: return
        super().step() # Metabolism and Age
        if self.health <= 0: return

        # 1. Immediate Self-Feeding (if food is already in hand or under feet)
        self.check_self_feeding()

        # 2. State-Based Execution & Task Switching
        # We only re-evaluate our 'Master Task' if we are in the nest and empty-handed.
        if self.is_at_nest() and self.inventory <= 0:
            self.update_task()

        # 3. Execute the current state
        if self.state == "FORAGING":
            self.execute_foraging()
        
        elif self.state == "RETURNING":
            self.execute_returning()

        elif self.state == "NURSING":
            self.execute_nursing()
        
        elif self.state == "IDLE":
            # Idle ants stay in the nest until they decide to work
            if random.random() < 0.1: # Small chance to wake up and check tasks
                self.update_task()

    def is_at_nest(self):
        """Checks if the ant is currently standing on a NestCell."""
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        return any(isinstance(obj, NestCell) for obj in cell_contents)

    def update_task(self):
        """
        Decision Hub: Only called when in the nest and inventory is empty.
        Determines the next behavioral chain to commit to.
        """
        # Critical Hunger Override: Go forage for self
        if self.energy < (self.max_energy * 0.3):
            self.state = "FORAGING"
            return

        food_level = self.model.total_food_stockpile
        brood_count = self.model.brood_count
        
        # Calculate Propensities based on colony needs
        f_weight = 0.4
        n_weight = 0.3
        i_weight = 0.3

        if self.model.phase == "FOUNDING":
            if food_level < 50: f_weight += 0.8
            if brood_count > 0: n_weight += 0.4
        elif self.model.phase == "ERGONOMIC":
            if food_level < 150: f_weight += 0.5
            if brood_count > 10: n_weight += 0.7
        else: # Reproductive
            if food_level < 500: f_weight += 1.0
            if brood_count > 20: n_weight += 0.3

        # Weighted Choice
        self.state = random.choices(["FORAGING", "NURSING", "IDLE"], 
                                     weights=[f_weight, n_weight, i_weight], k=1)[0]

    def execute_foraging(self):
        """Commit to finding food. Cannot stop until inventory > 0."""
        new_pos = self.sense_and_move()
        if new_pos:
            self.move_to(new_pos)
            self.energy -= self.move_cost
        
        # Check for food to harvest
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        food_source = next((obj for obj in cell_contents if isinstance(obj, FoodSource) and obj.amount > 0), None)
        
        if food_source:
            self.inventory = food_source.harvest(self.inventory_cap)
            self.energy -= self.forage_cost
            self.state = "RETURNING" # Automatically switch to returning chain

    def execute_returning(self):
        """Commit to returning food to nest. Cannot stop until inventory == 0."""
        self.lay_pheromone()
        
        # Check if on nest cell to deposit
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        nest_cell = next((obj for obj in cell_contents if isinstance(obj, NestCell)), None)
        
        if nest_cell and self.inventory > 0:
            actual_stored = nest_cell.store_food(self.inventory)
            self.inventory -= actual_stored
            # If still have food (nest cell full), keep looking for another nest cell
            if self.inventory <= 0:
                # Chain complete! Will re-evaluate next step because is_at_nest() will be true.
                return

        # Move towards nest center
        cx, cy = self.model.width // 2, self.model.height // 2
        nest_pos = (cx, cy)
        neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
        if neighbors:
            best_neighbor = min(neighbors, key=lambda n: math.dist(n, nest_pos))
            self.move_to(best_neighbor)
            self.energy -= self.move_cost

    def execute_nursing(self):
        """Commit to brood care. If no larvae or food, task ends."""
        # 1. Ensure we are in the nest
        if not self.is_at_nest():
            cx, cy = self.model.width // 2, self.model.height // 2
            nest_pos = (cx, cy)
            neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
            if neighbors:
                best_neighbor = min(neighbors, key=lambda n: math.dist(n, nest_pos))
                self.move_to(best_neighbor)
            return

        # 2. Check for food to give. If empty, try to withdraw from current cell.
        if self.inventory <= 0:
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            nest_cell = next((obj for obj in cell_contents if isinstance(obj, NestCell)), None)
            if nest_cell:
                self.inventory = nest_cell.withdraw_food(1.0) # Withdraw a small amount to feed
        
        # 3. Feed larvae in the immediate vicinity
        if self.inventory > 0:
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            larvae = [a for a in cell_contents if isinstance(a, BroodAgent) and a.stage == "LARVA"]
            if larvae:
                target = random.choice(larvae)
                if target.feed(0.5):
                    self.inventory -= 0.5
                    self.energy -= self.nurse_cost
            else:
                # No larvae here? Move randomly within the nest to find some
                neighbors = list(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
                nest_neighbors = [n for n in neighbors if any(isinstance(obj, NestCell) for obj in self.model.grid.get_cell_list_contents([n]))]
                if nest_neighbors:
                    self.move_to(random.choice(nest_neighbors))
        else:
            # Out of food to nurse with, task ends
            self.state = "IDLE"

    def check_self_feeding(self):
        """Eat if hungry. Done mid-chain if possible."""
        if self.energy < (self.max_energy * 0.7):
            if self.inventory > 0:
                eaten = self.eat(amount=min(1.0, self.inventory))
                self.inventory -= eaten
            
            if self.energy < (self.max_energy * 0.7) and self.is_at_nest():
                cell_contents = self.model.grid.get_cell_list_contents([self.pos])
                nest_cell = next((obj for obj in cell_contents if isinstance(obj, NestCell)), None)
                if nest_cell:
                    withdrawn = nest_cell.withdraw_food(1.0)
                    self.eat(amount=withdrawn)

    def lay_pheromone(self):
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if hasattr(obj, 'add_pheromone'):
                obj.add_pheromone(self.max_pheromone)

    def sense_and_move(self):
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
