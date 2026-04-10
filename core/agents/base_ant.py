import mesa

class BaseAnt(mesa.Agent):
    """
    A base class for all ant castes using Mesa 3.0+ features.
    Incorporates basic physiology: energy, health, and metabolism.
    Includes Trophallaxis (Social Feeding).
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
        self.starvation_rate = 0.5 
        self.recovery_rate = 0.2    
        
        self.inventory = 0.0
        self.inventory_cap = 5.0
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
            self.health = min(self.max_health, self.health + self.recovery_rate)
            self.energy -= self.recovery_rate 
        
        # 3. Death Check
        if self.health <= 0 or self.age >= self.max_age:
            self.die()

    def die(self):
        """Handle agent removal."""
        self.remove()

    def move_to(self, new_pos):
        """Helper to move the agent on the Mesa grid."""
        self.model.grid.move_agent(self, new_pos)

    def eat(self, amount=1.0):
        """
        Consumes food to restore energy. 
        Returns the amount actually consumed based on hunger.
        """
        needed = self.max_energy - self.energy
        if needed <= 0:
            return 0.0
            
        # 1 unit of food = 20 units of energy (tunable)
        can_eat = amount
        will_eat = min(can_eat, needed / 20.0)
        
        self.energy += will_eat * 20.0
        return will_eat

    def give_food(self, recipient, amount):
        """
        Socially shares food (Trophallaxis).
        'amount' is from the donor's inventory.
        """
        if self.inventory <= 0: return 0.0
        
        to_give = min(amount, self.inventory)
        
        # Check if recipient can take it
        if hasattr(recipient, 'receive_food'):
            actual_received = recipient.receive_food(to_give)
            self.inventory -= actual_received
            return actual_received
        return 0.0

    def receive_food(self, amount):
        """
        Receives food via Trophallaxis. 
        If it can't fit in inventory, it's eaten immediately.
        """
        # 1. First, satisfy immediate hunger
        needed_energy = self.max_energy - self.energy
        can_eat = min(amount, needed_energy / 20.0)
        self.energy += can_eat * 20.0
        
        remaining = amount - can_eat
        
        # 2. Store rest in inventory if possible
        if hasattr(self, 'inventory_cap'):
            space = self.inventory_cap - self.inventory
            can_store = min(remaining, space)
            self.inventory += can_store
            return can_eat + can_store
            
        return can_eat
