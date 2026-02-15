from PIL import Image
import numpy as np


def load_image_to_grid(image_path, grid_rows, grid_cols, threshold=128):
    """
    Converts an image to a binary grid using optimized NumPy operations.
    """
    # 1. Open and convert to Grayscale ('L') or 'RGB'
    img = Image.open(image_path).convert('L')

    # 2. Use NEAREST resizing to keep pixel art "crisp"
    # Note: PIL uses (width, height), but NumPy uses (rows, cols)
    img = img.resize((grid_cols, grid_rows), Image.NEAREST)

    # 3. Convert to NumPy array
    # This creates a 2D array of values 0-255
    img_data = np.array(img)

    # 4. Vectorized Thresholding
    # Creates 1 if pixel > threshold, else 0
    binary_grid = (img_data > threshold).astype(int)

    return binary_grid


def load_sprite_centered(image_path, grid_rows, grid_cols, target_size=None):
    """
    Loads an image, resizes it to fit, and centers it in the grid.
    target_size: (rows, cols) tuple to force the sprite to a certain size.
    """
    img = Image.open(image_path).convert("RGBA")
    img = img.convert("L")

    # 1. Determine size. If it's bigger than the grid, or target_size is set, shrink it.
    if target_size:
        img = img.resize((target_size[1], target_size[0]), Image.NEAREST)
    elif img.size[0] > grid_cols or img.size[1] > grid_rows:
        # Scale down to fit 80% of the grid so there's a margin
        scale = min(grid_cols * 0.8 / img.size[0], grid_rows * 0.8 / img.size[1])
        new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
        img = img.resize(new_size, Image.NEAREST)

    # 2. Convert to binary data
    sprite_data = (np.array(img) > 128).astype(int)
    s_rows, s_cols = sprite_data.shape

    # 3. Create empty grid and center it
    new_grid = np.zeros((grid_rows, grid_cols), dtype=int)

    start_row = (grid_rows - s_rows) // 2
    start_col = (grid_cols - s_cols) // 2

    # 4. The Slice (Now guaranteed to fit!)
    new_grid[start_row:start_row + s_rows, start_col:start_col + s_cols] = sprite_data

    return new_grid


def save_grid_as_image(cells, file_path):
    pass