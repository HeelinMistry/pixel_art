import mesa

class BaseAnt(mesa.Agent):
    """
    A base class for all ant castes using Mesa 3.0+ features.
    """
    def __init__(self, model):
        super().__init__(model) # unique_id is now automatically handled in Mesa 3.0+
        self.age = 0
        self.max_age = 5000 # Increased max age to prevent premature death
        self.energy = 100 # Increased starting energy
        self.inventory = 0
        self.inventory_cap = 5
        self.state = "IDLE" # IDLE, FORAGING, RETURNING, NURSING, etc.

    def step(self):
        """Standard behavior for each tick."""
        self.age += 1
        self.energy -= 0.1 # Reduced energy consumption to prevent starvation too quickly
        
        # Check for death
        if self.energy <= 0 or self.age >= self.max_age:
            self.remove() # Mesa 3.0+ simplified removal
            return

    def move_to(self, new_pos):
        """Helper to move the agent on the Mesa grid."""
        self.model.grid.move_agent(self, new_pos)
