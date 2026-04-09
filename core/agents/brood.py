import mesa
import random
# from .worker import WorkerAgent # Moved to local import in hatch()
# from .drone import DroneAgent   # Moved to local import in hatch()

class BroodAgent(mesa.Agent):
    """
    Represents a single unit of brood (egg, larva, or pupa).
    Develops through stages and eventually hatches into an adult ant.
    """
    def __init__(self, model, stage="EGG"):
        super().__init__(model)
        self.stage = stage
        self.development_timer = 0
        self.fed_status = 0 # For larvae: how much food they've received

        # Development thresholds (tunable)
        self.egg_to_larva_time = 50
        self.larva_to_pupa_food_needed = 5 # How many "feedings" a larva needs
        self.pupa_to_adult_time = 100

    def step(self):
        """Handles the development of the brood through its stages."""
        self.development_timer += 1

        if self.stage == "EGG":
            if self.development_timer >= self.egg_to_larva_time:
                self.stage = "LARVA"
                self.development_timer = 0
                self.fed_status = 0
                # print(f"Brood {self.unique_id} hatched into LARVA.")

        elif self.stage == "LARVA":
            # Larvae need to be fed by workers
            # Development timer here tracks how long it's been a larva
            # Fed status tracks how much food it has received
            if self.fed_status >= self.larva_to_pupa_food_needed:
                self.stage = "PUPA"
                self.development_timer = 0
                # print(f"Brood {self.unique_id} pupated into PUPA.")

        elif self.stage == "PUPA":
            if self.development_timer >= self.pupa_to_adult_time:
                self.hatch()
                # print(f"Brood {self.unique_id} hatched into ADULT.")

    def feed(self, amount=1):
        """Increases the fed status of a larva."""
        if self.stage == "LARVA":
            self.fed_status += amount
            return True
        return False

    def hatch(self):
        """Transforms the pupa into an adult ant and removes itself."""
        # Import WorkerAgent and DroneAgent locally to avoid circular dependency
        from .worker import WorkerAgent
        from .drone import DroneAgent

        # Determine what kind of ant hatches based on colony phase or other factors
        new_ant = None
        if self.model.phase == "REPRODUCTIVE" and random.random() < 0.1: # 10% chance for drone in reproductive phase
            new_ant = DroneAgent(self.model)
        else: # Otherwise, always a worker for now
            new_ant = WorkerAgent(self.model)
            
        self.model.grid.place_agent(new_ant, self.pos)
        self.remove() # In Mesa 3.0+, simply call self.remove() to remove from model and grid
