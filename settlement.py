import arcade


class Settlement(arcade.Sprite):
    def __init__(self, x, y, cell_dim):
        # Using a soft square to represent a 'hub'
        tex = arcade.make_soft_square_texture(
            name=f"settlement_{x}_{y}",
            size=cell_dim,
            color=arcade.color.GRAY)
        super().__init__(tex)

        self.grid_x = x
        self.grid_y = y
        self.center_x = x * cell_dim + cell_dim // 2
        self.center_y = y * cell_dim + cell_dim // 2

        # Core Economic Stats
        self.stockpile = 0
        self.total_historical_deposits = 0
        self.resident_count = 0

        # Compounding Stats
        self.tech_level = 1.0  # Increases harvest efficiency
        self.safety_bonus = 0  # Increases resident lifespan