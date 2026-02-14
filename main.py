import pygame
import engine
import renderer

# --- Configuration ---
WIDTH, HEIGHT = 800, 800
CELL_SIZE = 10
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Conway's Game of Life: Pixel Art Sandbox")
    
    # Initialize Grid
    grid = engine.Grid(ROWS, COLS)
    
    # Initialize Renderer
    rend = renderer.Renderer(CELL_SIZE)

    render_mode = "classic"  # Options: "classic", "heatmap"
    
    running = False
    clock = pygame.time.Clock()

    while True:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:  # Press 'H' to toggle heatmap
                    render_mode = "heatmap" if render_mode == "classic" else "classic"
                
                if event.key == pygame.K_SPACE:
                    running = not running
                
                if event.key == pygame.K_c: # Clear grid
                    grid.cells.fill(0)
                    grid.heat_map.fill(0)

            # Mouse Interaction
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                # Ensure click is within bounds
                if 0 <= pos[0] < WIDTH and 0 <= pos[1] < HEIGHT:
                    col, row = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                    grid.set_cell(row, col, 1)
            
            if pygame.mouse.get_pressed()[2]: # Right click to erase
                pos = pygame.mouse.get_pos()
                if 0 <= pos[0] < WIDTH and 0 <= pos[1] < HEIGHT:
                    col, row = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                    grid.set_cell(row, col, 0)

        # 2. Update Logic
        if running:
            grid.update()
            # Add a small delay or control update rate separately from frame rate if needed
            # For now, we rely on clock.tick to limit speed, but simulation might be too fast at 60FPS.
            # We can add a counter or time check here.
            pygame.time.delay(50) 

        # 3. Render
        rend.draw(screen, grid.cells, grid.heat_map, mode=render_mode)
        pygame.display.update()
            
        clock.tick(60) # Limit FPS

if __name__ == "__main__":
    main()