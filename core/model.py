import mesa
import random

class AntColonyModel(mesa.Model):
    """
    A Mesa Model for the Ant Colony Simulation using Mesa 3.0+ features.
    """
    def __init__(self, width=50, height=50, initial_workers=15, **kwargs):
        super().__init__()
        self.width = width
        self.height = height
        
        # 1. Grid (Hexagonal grid via MultiGrid)
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        
        # 2. Colony Stats
        self.food_stockpile = 100
        self.brood_count = 0
        self.phase = "FOUNDING" 
        
        # 3. Create Environmental Layer (Pheromone/Grid Cells)
        self.create_environment()
        
        # 4. Initialize Agents
        self.spawn_initial_colony(initial_workers)
        
        # 5. Data Collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Workers": lambda m: len(m.agents),
                "Food": "food_stockpile"
            }
        )

    def create_environment(self):
        """Populates the grid with pheromone cells, the nest, and food sources."""
        from core.world.cell import PheromoneCell, NestCell, FoodSource
        
        # Center of the map
        cx, cy = self.width // 2, self.height // 2
        
        # 1. Fill the entire grid with basic PheromoneCells
        for x in range(self.width):
            for y in range(self.height):
                # Check for Nest Area (radius of 3)
                if abs(x - cx) <= 2 and abs(y - cy) <= 2:
                    cell = NestCell(self)
                else:
                    cell = PheromoneCell(self)
                self.grid.place_agent(cell, (x, y))
        
        # 2. Scatter Food Sources (on top of existing cells)
        for _ in range(8):
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            if abs(fx - cx) < 10 and abs(fy - cy) < 10:
                continue # Stay away from the nest
                
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
            spawn_pos = (cx + random.randint(-1, 1), cy + random.randint(-1, 1))
            self.grid.place_agent(worker, spawn_pos)

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
