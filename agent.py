import arcade
import random

# State Constants
STATE_NOMAD = "NOMAD"
STATE_PIONEER = "PIONEER"
STATE_RESIDENT = "RESIDENT"


class Agent(arcade.Sprite):
    def __init__(self, grid_x, grid_y, cell_dim):
        # Visual setup
        img = arcade.make_circle_texture(int(cell_dim * 0.4), arcade.color.ORANGE_PEEL)
        super().__init__(img)

        # Core Properties
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.cell_dim = cell_dim

        # New Concepts
        self.state = STATE_NOMAD
        self.age = 0
        self.max_age = random.randint(600, 1000)  # Lifetime in logic ticks
        self.inventory = 0
        self.inventory_cap = 10
        self.home = None  # Will point to a Settlement object later

        # Modifier: 0.05 (slow) to 0.3 (fast). Default was 0.15
        self.move_speed = random.uniform(0.08, 0.25)
        # Modifier: How many units they harvest per tick
        self.gather_rate = random.randint(1, 3)

        # Visual cue: Faster agents are slightly smaller/thinner?
        # Or just use the speed to adjust the think_delay
        self.think_delay = random.uniform(0.1, 0.4)
        self.time_since_think = random.uniform(0, self.think_delay)

    def update(self, delta_time: float, pathing_grid):  # Pass pathing_grid here
        target_x = self.grid_x * self.cell_dim + self.cell_dim // 2
        target_y = self.grid_y * self.cell_dim + self.cell_dim // 2

        # ROAD BONUS: Look up the path strength at the target
        road_quality = pathing_grid[self.grid_x][self.grid_y]

        # Speed is base speed + up to 0.20 bonus based on road quality
        current_speed = self.move_speed + (road_quality * 0.20)

        self.center_x = arcade.math.lerp(self.center_x, target_x, current_speed)
        self.center_y = arcade.math.lerp(self.center_y, target_y, current_speed)
        self.time_since_think += delta_time

        # 2. Calculate how far the visual sprite is from the logical target
        dist_x = abs(self.center_x - target_x)
        dist_y = abs(self.center_y - target_y)

        # Threshold of 1.0 pixel handles the float-math limitations of lerping
        is_visually_arrived = dist_x < 1.0 and dist_y < 1.0

        # 3. Only fire a logic tick if the timer is up AND we have arrived physically
        if is_visually_arrived and self.time_since_think >= self.think_delay:
            # Snap to the exact center to prevent any visual micro-jitters
            self.center_x = target_x
            self.center_y = target_y

            self.time_since_think = 0
            self.age += 1
            return True  # Signal a logic tick

        return False

    def survey_area(self, environment, radius=4):
        """ The 'Surveyor' mechanic: Finds the center of a resource cluster. """
        resource_coords = []
        rows = environment.height
        cols = environment.width
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tx, ty = self.grid_x + dx, self.grid_y + dy
                if 0 <= tx < cols and 0 <= ty < rows:
                    if environment.get_resource(tx, ty) > 0:
                        resource_coords.append((tx, ty))

        if not resource_coords:
            return None

        # Calculate Centroid
        avg_x = sum(p[0] for p in resource_coords) // len(resource_coords)
        avg_y = sum(p[1] for p in resource_coords) // len(resource_coords)
        return int(avg_x), int(avg_y)

    def sense_and_move(self, environment):
        """ Look at neighboring cells and move toward food. """
        best_move = None
        found_food = False
        
        rows = environment.height
        cols = environment.width

        # Scan a 3x3 area around the agent
        # Prioritize random shuffle to avoid bias in movement direction
        moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        random.shuffle(moves)
        
        for dx, dy in moves:
            check_x = self.grid_x + dx
            check_y = self.grid_y + dy

            # Stay within bounds
            if 0 <= check_x < cols and 0 <= check_y < rows:
                if environment.get_resource(check_x, check_y) > 0:
                    best_move = (dx, dy)
                    found_food = True
                    break  # Found food, head there!

        # If no food found, move randomly
        if not found_food:
            best_move = random.choice(moves + [(0,0)])

        # Apply movement
        new_x = self.grid_x + best_move[0]
        new_y = self.grid_y + best_move[1]
        
        # Clamp to grid
        self.grid_x = max(0, min(cols - 1, new_x))
        self.grid_y = max(0, min(rows - 1, new_y))
