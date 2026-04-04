import arcade
import math
import mesa
from PIL import Image, ImageDraw
from core.model import AntColonyModel
from core.agents.worker import WorkerAgent
from core.agents.queen import QueenAgent
from core.agents.drone import DroneAgent
from core.world.cell import FoodSource, NestCell, PheromoneCell

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

# Colors
COLOR_NEST = arcade.color.DARK_BROWN
COLOR_FOOD = arcade.color.APPLE_GREEN
COLOR_EMPTY = arcade.color.DARK_SLATE_GRAY
COLOR_WORKER = arcade.color.ORANGE_PEEL
COLOR_QUEEN = arcade.color.PURPLE
COLOR_DRONE = arcade.color.SKY_BLUE

def make_hex_texture(radius, color):
    """Generates a hexagonal texture using PIL."""
    size = int(radius * 2) + 4
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    center = size / 2
    points = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        points.append((
            center + radius * math.cos(angle_rad),
            center + radius * math.sin(angle_rad)
        ))
    
    draw.polygon(points, fill=color)
    return arcade.Texture(image)

class AntRenderer(arcade.Window):
    def __init__(self, width, height, grid_resolution):
        super().__init__(width, height, "Mesa 3.0+ Full-Screen Ant Sim")
        arcade.set_background_color(arcade.color.BLACK)

        # 1. Geometry Calculation
        self.hex_radius = SCREEN_HEIGHT / (math.sqrt(3) * (grid_resolution + 0.5))
        self.horiz_dist = 1.5 * self.hex_radius
        self.vert_dist = math.sqrt(3) * self.hex_radius
        
        cols = int((SCREEN_WIDTH / self.hex_radius - 0.5) / 1.5)
        rows = grid_resolution
        
        # 2. Initialize Mesa Model
        model_params = {
            "width": cols,
            "height": rows,
            "initial_workers": 20
        }
        self.model = AntColonyModel(**model_params)
        
        # 3. Offsets for Centering
        actual_width = (1.5 * cols + 0.5) * self.hex_radius
        actual_height = (rows + 0.5) * self.vert_dist
        self.offset_x = (SCREEN_WIDTH - actual_width) / 2
        self.offset_y = (SCREEN_HEIGHT - actual_height) / 2
        
        # 4. Sprite Lists
        self.grid_sprites = arcade.SpriteList()
        self.agent_sprites = arcade.SpriteList()
        
        # Pre-generate textures
        self.nest_tex = make_hex_texture(self.hex_radius - 1, COLOR_NEST)
        self.food_tex = make_hex_texture(self.hex_radius - 1, COLOR_FOOD)
        self.empty_tex = make_hex_texture(self.hex_radius - 1, COLOR_EMPTY)
        
        # Agent textures
        agent_r = self.hex_radius * 0.6
        self.worker_tex = make_hex_texture(agent_r, COLOR_WORKER)
        self.queen_tex = make_hex_texture(agent_r * 1.5, COLOR_QUEEN)
        self.drone_tex = make_hex_texture(agent_r, COLOR_DRONE)

        # 5. Create Grid Sprites
        self.sprite_map = {} 
        for x in range(self.model.width):
            for y in range(self.model.height):
                sprite = arcade.Sprite(self.empty_tex)
                sprite.center_x, sprite.center_y = self.get_pixel_pos(x, y)
                self.grid_sprites.append(sprite)
                self.sprite_map[(x, y)] = sprite
                
        self.agent_map = {}

    def get_pixel_pos(self, x, y):
        px = x * self.horiz_dist + self.hex_radius + self.offset_x
        py = y * self.vert_dist + (self.vert_dist / 2) + self.offset_y
        if x % 2 == 1:
            py += self.vert_dist / 2
        return px, py

    def on_draw(self):
        self.clear()
        self.grid_sprites.draw()
        self.agent_sprites.draw()
        
        display_text = (
            f"Step: {self.model.steps}\n"
            f"Population: {len(self.model.agents)}\n"
            f"Food Stockpile: {int(self.model.food_stockpile)}\n"
            f"Brood Count: {self.model.brood_count}"
        )
        arcade.draw_text(display_text, 10, SCREEN_HEIGHT - 20, 
                         arcade.color.WHITE, 12, multiline=True, width=300)

    def on_update(self, delta_time):
        self.model.step()
        
        # Update Grid Visuals
        for agent in self.model.agents:
            if isinstance(agent, PheromoneCell):
                if not agent.pos: continue
                sprite = self.sprite_map[agent.pos]
                
                # 1. Base Texture Logic
                if isinstance(agent, FoodSource):
                    if agent.amount > 0:
                        sprite.texture = self.food_tex
                    else:
                        sprite.texture = self.empty_tex # VISUAL DECAY: Turn empty when depleted
                elif isinstance(agent, NestCell):
                    sprite.texture = self.nest_tex
                else:
                    sprite.texture = self.empty_tex

                # 2. Pheromone Overlay (Tinting)
                if agent.pheromone_level > 0:
                    # Tint towards a glowing yellow/amber
                    intensity = min(255, int(agent.pheromone_level * 10))
                    sprite.color = (255, 255, 255 - intensity)
                else:
                    sprite.color = (255, 255, 255) # Reset to default
        
        # Sync Agent Sprites
        active_agents = set(self.model.agents)
        for agent in active_agents:
            if not isinstance(agent, (WorkerAgent, QueenAgent, DroneAgent)):
                continue
                
            if agent not in self.agent_map:
                tex = self.worker_tex
                if isinstance(agent, QueenAgent): tex = self.queen_tex
                elif isinstance(agent, DroneAgent): tex = self.drone_tex
                
                sprite = arcade.Sprite(tex)
                if agent.pos:
                    tx, ty = self.get_pixel_pos(agent.pos[0], agent.pos[1])
                    sprite.center_x, sprite.center_y = tx, ty
                
                self.agent_map[agent] = sprite
                self.agent_sprites.append(sprite)
            
            sprite = self.agent_map[agent]
            if agent.pos:
                tx, ty = self.get_pixel_pos(agent.pos[0], agent.pos[1])
                sprite.center_x = arcade.math.lerp(sprite.center_x, tx, 0.2)
                sprite.center_y = arcade.math.lerp(sprite.center_y, ty, 0.2)
            
        mapped_agents = list(self.agent_map.keys())
        for agent in mapped_agents:
            if agent not in active_agents:
                sprite = self.agent_map.pop(agent)
                sprite.remove_from_sprite_lists()
