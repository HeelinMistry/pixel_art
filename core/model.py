import mesa
import random
from core.agents.base_ant import BaseAnt
from core.agents.worker import WorkerAgent
from core.agents.brood import BroodAgent

class AntColonyModel(mesa.Model):
    """
    A Mesa Model for the Ant Colony Simulation.
    Fully aligned with Mesa 3.3.1 API.
    Includes Dynamic Food Spawning.
    """
    def __init__(self, width=50, height=50, initial_workers=15, **kwargs):
        super().__init__()
        self.width = width
        self.height = height
        
        # 1. Grid
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        
        # 2. Colony Stats
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
        
        # 5. Distribute Initial Food Stockpile (100 units)
        self.distribute_initial_food(100)
        
        # 6. Data Collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Ants": lambda m: len([a for a in m.agents if isinstance(a, BaseAnt)]),
                "Workers": lambda m: len([a for a in m.agents if isinstance(a, WorkerAgent)]),
                "Food": "total_food_stockpile",
                "Brood": lambda m: len([a for a in m.agents if isinstance(a, BroodAgent)]),
                "Eggs": lambda m: len([a for a in m.agents if isinstance(a, BroodAgent) and a.stage == "EGG"]),
                "Larvae": lambda m: len([a for a in m.agents if isinstance(a, BroodAgent) and a.stage == "LARVA"]),
                "Pupae": lambda m: len([a for a in m.agents if isinstance(a, BroodAgent) and a.stage == "PUPA"]),
                "Phase": "phase"
            }
        )

    def distribute_initial_food(self, amount):
        from core.world.cell import NestCell
        nest_cells = [a for a in self.agents if isinstance(a, NestCell)]
        if not nest_cells: return
        
        food_per_cell = amount / len(nest_cells)
        for cell in nest_cells:
            cell.store_food(food_per_cell)

    @property
    def total_food_stockpile(self):
        from core.world.cell import NestCell
        total = 0.0
        for agent in self.agents:
            if isinstance(agent, NestCell):
                total += agent.stored_food
        return total

    @property
    def brood_count(self):
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
        
        # Initial Food Patches
        for _ in range(8):
            self.spawn_random_food()

    def spawn_random_food(self):
        """Creates a new seed food source randomly on the map."""
        from core.world.cell import FoodSource, NestCell
        cx, cy = self.width // 2, self.height // 2
        
        fx = random.randint(0, self.width - 1)
        fy = random.randint(0, self.height - 1)
        
        # Ensure it's not too close to the nest
        if abs(fx - cx) < 10 and abs(fy - cy) < 10:
            return

        # Don't overlap with existing nest/food
        cell_contents = self.grid.get_cell_list_contents([(fx, fy)])
        if any(isinstance(obj, (NestCell, FoodSource)) for obj in cell_contents):
            return

        food = FoodSource(self, amount=random.randint(50, 150))
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

    def update_colony_phase(self):
        current_workers = len([a for a in self.agents if isinstance(a, WorkerAgent)])
        food_stockpile = self.total_food_stockpile

        if self.phase == "FOUNDING":
            if current_workers >= self.ergonomic_worker_threshold and food_stockpile >= self.ergonomic_food_threshold:
                self.phase = "ERGONOMIC"
                print(f"Colony transitioned to ERGONOMIC phase at step {self.steps}")
        elif self.phase == "ERGONOMIC":
            if current_workers >= self.reproductive_worker_threshold and food_stockpile >= self.reproductive_food_threshold:
                self.phase = "REPRODUCTIVE"
                print(f"Colony transitioned to REPRODUCTIVE phase at step {self.steps}")

    def step(self):
        self.update_colony_phase()
        
        # Dynamic Food Spawning: Very low chance each tick to drop a new seed
        if random.random() < 0.005:
            self.spawn_random_food()

        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
