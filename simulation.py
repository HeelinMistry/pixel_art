import json
import random
import csv

import arcade

from agent import Agent, STATE_NOMAD, STATE_PIONEER, STATE_RESIDENT
from environment import Environment
from settlement import Settlement

# --- Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
GRID_SIZE = 50
CELL_DIM = SCREEN_WIDTH // GRID_SIZE

# Colors & Assets (Placeholders)
COLOR_EMPTY = arcade.color.DARK_SLATE_GRAY
COLOR_FOOD = arcade.color.APPLE_GREEN
COLOR_AGENT = arcade.color.ORANGE_PEEL


class Simulation(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Arcade 3.0 Optimized Sim")
        arcade.set_background_color(arcade.color.BLACK)

        self.tick_count = 0
        self.history = []

        # 1. Initialize Environment
        self.environment = Environment(GRID_SIZE, GRID_SIZE)

        # 2. Visual Grid (The SpriteList)
        self.grid_sprites = arcade.SpriteList()

        # Create textures
        self.food_texture = arcade.make_circle_texture(
            diameter=(CELL_DIM - 2),
            color=COLOR_FOOD
        )

        self.empty_texture = arcade.make_circle_texture(
            diameter=(CELL_DIM - 2),
            color=COLOR_EMPTY
        )
        
        # Create a "flat" list of sprites to represent the grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                # Determine starting texture based on environment's grid
                tex = self.food_texture if self.environment.grid[col][row] > 0 else self.empty_texture

                # Create sprite with that texture
                cell = arcade.Sprite(tex)
                cell.center_x = col * CELL_DIM + CELL_DIM // 2
                cell.center_y = row * CELL_DIM + CELL_DIM // 2

                self.grid_sprites.append(cell)

        # 3. Agents
        self.agent_list = arcade.SpriteList()
        num_initial_agents = 10
        for i in range(num_initial_agents):
            start_x = random.randint(0, GRID_SIZE - 1)
            start_y = random.randint(0, GRID_SIZE - 1)

            # Create the agent
            new_agent = Agent(start_x, start_y, CELL_DIM)

            # Give them a random starting inventory
            new_agent.inventory = 0

            self.agent_list.append(new_agent)

        # Inside Simulation.__init__
        self.settlement_list = arcade.SpriteList()

    def found_settlement(self, x, y, pioneer_agent):
        # 1. Create the physical settlement
        new_home = Settlement(x, y, CELL_DIM)
        self.settlement_list.append(new_home)

        # 2. Link the pioneer to their new home
        pioneer_agent.home = new_home
        pioneer_agent.state = STATE_RESIDENT
        new_home.resident_count += 1

        # 3. Initial Deposit
        # The pioneer contributes their current inventory to the foundation
        new_home.stockpile += pioneer_agent.inventory
        pioneer_agent.inventory = 0

        print(f"Settlement founded at ({x}, {y}) by Agent {id(pioneer_agent)}")

    def on_update(self, delta_time):
        # Update the environment (e.g., resource regrowth)
        self.environment.step()

        # Update grid sprites based on environment changes
        # OPTIMIZATION: Only update sprites that have changed state
        # This is still O(N^2) but avoids texture swapping if not needed
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                index = (row * GRID_SIZE) + col
                sprite = self.grid_sprites[index]

                # Get the current resource level (0 to 10)
                resource_level = self.environment.grid[col][row]

                if resource_level > 0:
                    # Map 1-10 to 55-255 alpha (keeping a minimum visibility while it exists)
                    # Formula: (level / max) * 200 + 55
                    new_alpha = int((resource_level / 10) * 200) + 55
                    sprite.alpha = new_alpha

                    # Ensure it shows the food texture
                    if sprite.texture != self.food_texture:
                        sprite.texture = self.food_texture
                else:
                    # Resource is depleted
                    sprite.alpha = 255  # Reset alpha so the empty circle is clear
                    if sprite.texture != self.empty_texture:
                        sprite.texture = self.empty_texture

        for agent in self.agent_list:
            # Agent.update returns True when a logic tick occurs
            if agent.update(delta_time):
                # 1. Death Check
                if agent.age > agent.max_age:
                    agent.remove_from_sprite_lists()
                    continue

                # 2. State-Based Behavior
                if agent.state == STATE_NOMAD:
                    
                    # Harvest if on food
                    ix, iy = int(agent.grid_x), int(agent.grid_y)
                    if self.environment.get_resource(ix, iy) > 0:
                        # Pass the agent's specific gather_rate
                        amount = self.environment.consume(ix, iy, agent.gather_rate)
                        agent.inventory += amount
                        # Visual update as before...
                        # Force immediate visual update for responsiveness
                        self.grid_sprites[(iy * GRID_SIZE) + ix].texture = self.empty_texture

                    # Transition to Pioneer?
                    if agent.inventory >= 5:  # Threshold to consider settling
                        centroid = agent.survey_area(self.environment)
                        if centroid:
                            agent.state = STATE_PIONEER
                            agent.target_centroid = centroid

                    # Move randomly or use Radar
                    agent.sense_and_move(self.environment)

                elif agent.state == STATE_PIONEER:
                    # Move toward the cluster center
                    tx, ty = agent.target_centroid
                    
                    # Simple pathfinding to target
                    dx = 0
                    dy = 0
                    
                    if tx > agent.grid_x: dx = 1
                    elif tx < agent.grid_x: dx = -1
                    
                    if ty > agent.grid_y: dy = 1
                    elif ty < agent.grid_y: dy = -1
                    
                    agent.grid_x += dx
                    agent.grid_y += dy

                    # Arrived? Found the settlement!
                    # Check distance (manhattan or exact match)
                    if agent.grid_x == tx and agent.grid_y == ty:
                        self.found_settlement(tx, ty, agent)

                elif agent.state == STATE_RESIDENT:
                    # NEW: Resident Logic
                    if agent.inventory >= agent.inventory_cap:
                        # Pathfind home to deposit
                        dx = 0
                        dy = 0
                        
                        if agent.home.grid_x > agent.grid_x: dx = 1
                        elif agent.home.grid_x < agent.grid_x: dx = -1
                        
                        if agent.home.grid_y > agent.grid_y: dy = 1
                        elif agent.home.grid_y < agent.grid_y: dy = -1
                        
                        agent.grid_x += dx
                        agent.grid_y += dy

                        # Deposit if home
                        if agent.grid_x == agent.home.grid_x and agent.grid_y == agent.home.grid_y:
                            agent.home.stockpile += agent.inventory
                            agent.inventory = 0
                            print(f"Deposited resources. Stockpile: {agent.home.stockpile}")
                    else:
                        # 1. Harvest on the CURRENT cell first
                        ix, iy = int(agent.grid_x), int(agent.grid_y)
                        if self.environment.get_resource(ix, iy) > 0:
                            amount = self.environment.consume(ix, iy, agent.gather_rate)
                            agent.inventory += amount
                            self.grid_sprites[(iy * GRID_SIZE) + ix].texture = self.empty_texture

                        # 2. THEN decide where to move next
                        agent.sense_and_move(self.environment)
        
        self.collect_data()

    def collect_data(self):
        """Gathers stats about the current state of the simulation."""
        if self.tick_count % 60 != 0:
            self.tick_count += 1
            return

        # 1. Map Resources (on the ground)
        ground_resources = self.environment.get_stats()["total_resources"]

        # 2. Settlement Resources (in stockpiles)
        settlement_resources = sum(s.stockpile for s in self.settlement_list)
        total_resources = ground_resources + settlement_resources

        # 3. Population & Settlement counts
        alive_agents = len(self.agent_list)
        num_settlements = len(self.settlement_list)

        # 4. Average Age Calculation
        avg_age = sum(a.age for a in self.agent_list) / alive_agents if alive_agents > 0 else 0

        stats = {
            "tick": self.tick_count,
            "total_food": total_resources,
            "ground_food": ground_resources,
            "population": alive_agents,
            "settlements": num_settlements,
            "avg_age": round(avg_age, 0)
        }

        self.history.append(stats)
        self.tick_count += 1

    def on_draw(self):
        self.clear()
        self.grid_sprites.draw()
        self.settlement_list.draw()
        self.agent_list.draw()

        # Analytics Overlay
        if self.history:
            latest = self.history[-1]
            display_text = (
                f"Tick: {latest['tick']}\n"
                f"Population: {latest['population']}\n"
                f"Settlements: {latest['settlements']}\n"
                f"Total Resources: {latest['total_food']}\n"
                f"Avg Age: {latest['avg_age']}"
            )
            arcade.draw_text(display_text, 10, SCREEN_HEIGHT - 20,
                             arcade.color.WHITE, 12, multiline=True, width=250,
                             anchor_y="top")  # Anchor top makes multi-line easier to align

    def save_to_csv(self):
        """Exports the history list to a CSV file."""
        if not self.history:
            return

        keys = self.history[0].keys()
        with open('sim_analytics.csv', 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.history)
        print("Analytics saved to sim_analytics.csv")

    # Ensure this runs when the window closes
    def on_close(self):
        self.save_to_csv()
        super().on_close()
