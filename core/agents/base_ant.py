import mesa

class BaseAnt(mesa.Agent):
    """
    A base class for all ant castes using Mesa 3.0+ features.
    Incorporates basic physiology: energy, health, and metabolism.
    """
    def __init__(self, model):
        super().__init__(model)
        self.age = 0
        self.max_age = 5000 
        
        # Physiology stats
        self.energy = 100.0
        self.max_energy = 100.0
        self.health = 100.0
        self.max_health = 100.0
        
        # Rates
        self.metabolism_rate = 0.1
        self.starvation_rate = 0.5 # Health loss per tick when energy is 0
        self.recovery_rate = 0.2    # Health gain per tick when energy > 50
        
        self.inventory = 0
        self.inventory_cap = 5
        self.state = "IDLE"

    def step(self):
        """Standard behavior for each tick."""
        self.age += 1
        
        # 1. Metabolism: Constant energy drain
        self.energy -= self.metabolism_rate
        
        # 2. Physiology Logic: Starvation and Recovery
        if self.energy <= 0:
            self.energy = 0
            self.health -= self.starvation_rate
        elif self.health < self.max_health and self.energy > (self.max_energy * 0.5):
            # Slow recovery when well-fed
            self.health = min(self.max_health, self.health + self.recovery_rate)
            self.energy -= self.recovery_rate # Recovery costs extra energy
        
        # 3. Death Check
        if self.health <= 0 or self.age >= self.max_age:
            self.die()

    def die(self):
        """Handle agent removal."""
        self.remove()

    def move_to(self, new_pos):
        """Helper to move the agent on the Mesa grid."""
        self.model.grid.move_agent(self, new_pos)

    def eat(self, amount=1):
        """
        Consumes food to restore energy. 
        Returns the amount actually consumed based on hunger.
        """
        needed = self.max_energy - self.energy
        if needed <= 0:
            return 0
            
        # 1 unit of food = 20 units of energy (tunable)
        can_eat = amount
        will_eat = min(can_eat, needed / 20.0)
        
        self.energy += will_eat * 20.0
        return will_eat
