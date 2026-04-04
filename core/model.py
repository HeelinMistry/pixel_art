import mesa
import random
from core.agents.base_ant import BaseAnt

class AntColonyModel(mesa.Model):
    """
    A Mesa Model for the Ant Colony Simulation.
    """
    def __init__(self, width=50, height=50, initial_workers=15, **kwargs):
        super().__init__()
        self.width = width
        self.height = height
        
        # 1. Grid
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        
        # 2. Colony Stats
        self.food_stockpile = 100
        self.brood_count = 0
        self.phase = "FOUNDING" 
        
        # 3. Create Environmental Layer
        self.create_environment()
        
        # 4. Initialize Agents
        self.spawn_initial_colony(initial_workers)
        
        # 5. Data Collection - Fixed to only count Ants
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Ants": lambda m: len([a for a in m.agents if isinstance(a, BaseAnt)]),
                "Food": "food_stockpile"
            }
        )

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
        from core.agents.worker import WorkerAgent
        from core.agents.queen import QueenAgent
        
        cx, cy = self.width // 2, self.height // 2
        queen = QueenAgent(self)
        self.grid.place_agent(queen, (cx, cy))
        
        for _ in range(initial_workers):
            worker = WorkerAgent(self)
            self.grid.place_agent(worker, (cx, cy))

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
