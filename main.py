import pygame
import numpy as np

# --- Configuration ---
WIDTH, HEIGHT = 800, 800
CELL_SIZE = 10  # Increase this for "chunkier" pixels
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE

# Colors (Feel free to change these for your "Art" style!)
COLOR_BG = (10, 10, 10)
COLOR_GRID = (40, 40, 40)
COLOR_DIE = (170, 0, 0)
COLOR_ALIVE = (0, 255, 150)


def update(screen, cells, size, with_progress=False):
    updated_cells = np.zeros((cells.shape[0], cells.shape[1]))

    for row, col in np.ndindex(cells.shape):
        # Calculate neighbors using a 3x3 slice
        alive_neighbors = np.sum(cells[row - 1:row + 2, col - 1:col + 2]) - cells[row, col]
        color = COLOR_BG if cells[row, col] == 0 else COLOR_ALIVE

        # Conway's Rules
        if cells[row, col] == 1:
            if alive_neighbors < 2 or alive_neighbors > 3:
                if with_progress:
                    updated_cells[row, col] = 0
            elif 2 <= alive_neighbors <= 3:
                updated_cells[row, col] = 1
                if with_progress: color = COLOR_ALIVE
        else:
            if alive_neighbors == 3:
                updated_cells[row, col] = 1
                if with_progress: color = COLOR_ALIVE

        pygame.draw.rect(screen, color, (col * size, row * size, size - 1, size - 1))

    return updated_cells


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    cells = np.zeros((ROWS, COLS))
    screen.fill(COLOR_GRID)
    update(screen, cells, CELL_SIZE)

    pygame.display.flip()
    pygame.display.set_caption("Conway's Game of Life: Pixel Art Sandbox")

    running = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # Use Mouse to Draw "Pixel Art"
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                cells[pos[1] // CELL_SIZE, pos[0] // CELL_SIZE] = 1
                update(screen, cells, CELL_SIZE)
                pygame.display.update()

            # Spacebar to Start/Stop the simulation
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = not running
                    update(screen, cells, CELL_SIZE)
                    pygame.display.update()

        screen.fill(COLOR_GRID)

        if running:
            cells = update(screen, cells, CELL_SIZE, with_progress=True)
            pygame.display.update()

        pygame.time.delay(50)  # Controls simulation speed


if __name__ == "__main__":
    main()