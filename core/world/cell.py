import mesa
import random

class PheromoneCell(mesa.Agent):
    """
    Every cell on the grid has this agent to manage pheromones.
    """
    def __init__(self, model):
        super().__init__(model)
        self.pheromone_level = 0.0
        self.decay_rate = 0.03
        self.max_pheromone = 100.0

    def step(self):
        """Naturally decay pheromones over time."""
        if self.pheromone_level > 0:
            self.pheromone_level = max(0, self.pheromone_level - self.decay_rate)

    def add_pheromone(self, amount):
        self.pheromone_level = min(self.max_pheromone, self.pheromone_level + amount)

class NestCell(PheromoneCell):
    """
    A cell belonging to the nest.
    Can store food physically (Localized Stockpile).
    """
    def __init__(self, model):
        super().__init__(model)
        self.stored_food = 0.0
        self.food_capacity = 50.0 

    def store_food(self, amount):
        space = self.food_capacity - self.stored_food
        to_store = min(amount, space)
        self.stored_food += to_store
        return to_store

    def withdraw_food(self, amount):
        to_withdraw = min(amount, self.stored_food)
        self.stored_food -= to_withdraw
        return to_withdraw

class FoodSource(PheromoneCell):
    """
    A cell containing food resources.
    Can grow outwards to neighboring cells if healthy.
    """
    def __init__(self, model, amount=100):
        super().__init__(model)
        self.amount = amount
        self.initial_amount = amount
        self.expansion_chance = 0.005 # Probability to spread per tick

    def step(self):
        super().step()
        
        # 1. Self-Regrowth (only if not depleted)
        if 0 < self.amount < self.initial_amount and random.random() < 0.005:
            self.amount += 1

        # 2. Outward Growth (Spread to neighbors)
        if self.amount > 50 and random.random() < self.expansion_chance:
            self.spread()

        # 3. Depletion Check: Remove agent if empty
        if self.amount <= 0:
            self.remove()

    def spread(self):
        """Attempts to create a new food source in a neighboring cell."""
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        target_pos = random.choice(neighbors)
        
        # Check if target is valid (Not nest, doesn't already have food)
        cell_contents = self.model.grid.get_cell_list_contents([target_pos])
        if any(isinstance(obj, (NestCell, FoodSource)) for obj in cell_contents):
            return

        # Create new "offspring" food source with a portion of current food
        spread_amount = 20
        if self.amount > spread_amount + 10:
            new_food = FoodSource(self.model, amount=spread_amount)
            self.model.grid.place_agent(new_food, target_pos)
            self.amount -= spread_amount

    def harvest(self, amount):
        gathered = min(self.amount, amount)
        self.amount -= gathered
        return gathered
