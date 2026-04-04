import mesa
import random

class AntColonyModel(mesa.Model):
    """
    A Mesa Model for the Ant Colony Simulation using Mesa 3.0+ features.
    """
    def __init__(self, width=50, height=50, initial_workers=10, **kwargs):
        super().__init__()
        self.width = width
        self.height = height
        
        # 1. Grid (Hexagonal grid via MultiGrid)
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        
        # 2. Colony Stats
        self.food_stockpile = 100
        self.brood_count = 0
        self.danger_level = 0
        self.phase = "FOUNDING" 
        
        # 3. Create World Structure
        # Nest is always at the center
        self.create_nest(width // 2, height // 2)
        self.create_food_sources(5)
        
        # 4. Initialize Agents
        self.spawn_initial_colony(initial_workers)
        
        # 5. Data Collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Workers": lambda m: len(m.agents),
                "Food": "food_stockpile"
            }
        )

    def create_nest(self, center_x, center_y, radius=3):
        from core.world.cell import NestCell
        for x in range(center_x - radius, center_x + radius + 1):
            for y in range(center_y - radius, center_y + radius + 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    cell = NestCell(self)
                    self.grid.place_agent(cell, (x, y))

    def create_food_sources(self, num_sources):
        from core.world.cell import FoodSource
        for _ in range(num_sources):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            # Avoid placing food inside the nest
            if abs(x - self.width // 2) < 10 and abs(y - self.height // 2) < 10:
                continue
                
            food = FoodSource(self, amount=random.randint(50, 150))
            self.grid.place_agent(food, (x, y))

    def spawn_initial_colony(self, initial_workers):
        from core.agents.worker import WorkerAgent
        from core.agents.queen import QueenAgent
        
        center_x, center_y = self.width // 2, self.height // 2
        queen = QueenAgent(self)
        self.grid.place_agent(queen, (center_x, center_y))
        
        for _ in range(initial_workers):
            worker = WorkerAgent(self)
            spawn_pos = (center_x + random.randint(-1, 1), center_y + random.randint(-1, 1))
            self.grid.place_agent(worker, spawn_pos)

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
