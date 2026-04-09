import mesa
import random
from core.agents.base_ant import BaseAnt
from core.agents.worker import WorkerAgent
from core.agents.brood import BroodAgent

class AntColonyModel(mesa.Model):
    """
    A Mesa Model for the Ant Colony Simulation.
    Fully aligned with Mesa 3.3.1 API (using self.agents AgentSet).
    """
    def __init__(self, width=50, height=50, initial_workers=15, **kwargs):
        super().__init__()
        self.width = width
        self.height = height
        
        # 1. Grid
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        
        # 2. Colony Stats
        self.food_stockpile = 100
        self.phase = "FOUNDING" 
        self.initial_workers = initial_workers 
        
        # Phase transition thresholds
        self.ergonomic_worker_threshold = initial_workers * 2
        self.ergonomic_food_threshold = 200
        self.reproductive_worker_threshold = 50
        self.reproductive_food_threshold = 500
        
        # 3. Create Environmental Layer
        self.create_environment()
        
        # 4. Initialize Agents
        self.spawn_initial_colony(initial_workers)
        
        # 5. Data Collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Ants": lambda m: len([a for a in m.agents if isinstance(a, BaseAnt)]),
                "Workers": lambda m: len([a for a in m.agents if isinstance(a, WorkerAgent)]),
                "Food": "food_stockpile",
                "Brood": lambda m: len([a for a in m.agents if isinstance(a, BroodAgent)]),
                "Eggs": lambda m: len([a for a in m.agents if isinstance(a, BroodAgent) and a.stage == "EGG"]),
                "Larvae": lambda m: len([a for a in m.agents if isinstance(a, BroodAgent) and a.stage == "LARVA"]),
                "Pupae": lambda m: len([a for a in m.agents if isinstance(a, BroodAgent) and a.stage == "PUPA"]),
                "Phase": "phase"
            }
        )

    @property
    def brood_count(self):
        """Dynamic count of all brood agents."""
        return len([a for a in self.agents if isinstance(a, BroodAgent)])

    def create_environment(self):
        from core.world.cell import PheromoneCell, NestCell, FoodSource
        cx, cy = self.width // 2, self.height // 2
        
        for x in range(self.width):
            for y in range(self.height):
                if abs(x - cx) <= 2 and abs(y - cy) <= 2:
                    cell = NestCell(self)
                else:
                    cell = PheromoneCell(self)
                self.grid.place_agent(cell, (x, y))
        
        for _ in range(8):
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            if abs(fx - cx) < 10 and abs(fy - cy) < 10:
                continue
                
            food = FoodSource(self, amount=random.randint(100, 200))
            self.grid.place_agent(food, (fx, fy))

    def spawn_initial_colony(self, initial_workers):
        from core.agents.queen import QueenAgent
        
        cx, cy = self.width // 2, self.height // 2
        queen = QueenAgent(self)
        self.grid.place_agent(queen, (cx, cy))
        
        for _ in range(initial_workers):
            worker = WorkerAgent(self)
            self.grid.place_agent(worker, (cx, cy))

    def update_colony_phase(self):
        current_workers = len([a for a in self.agents if isinstance(a, WorkerAgent)])

        if self.phase == "FOUNDING":
            if current_workers >= self.ergonomic_worker_threshold and self.food_stockpile >= self.ergonomic_food_threshold:
                self.phase = "ERGONOMIC"
                print(f"Colony transitioned to ERGONOMIC phase at step {self.steps}")
        elif self.phase == "ERGONOMIC":
            if current_workers >= self.reproductive_worker_threshold and self.food_stockpile >= self.reproductive_food_threshold:
                self.phase = "REPRODUCTIVE"
                print(f"Colony transitioned to REPRODUCTIVE phase at step {self.steps}")

    def step(self):
        self.update_colony_phase()
        # In Mesa 3.0+, shuffle_do("step") is the replacement for scheduler.step()
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
