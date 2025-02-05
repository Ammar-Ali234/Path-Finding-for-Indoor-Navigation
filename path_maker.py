import pygame
import json
import sys

# Initialize Pygame
pygame.init()

# Screen settings
width, height = 1500,700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Maze Creator")

# Colors
colors = {
    "black": (0, 0, 0),   # background
    "white": (255, 255, 255),  # grid
    "blue": (0, 0, 255),  # start
    "red": (255, 0, 0),   # target
    "gray": (128, 128, 128),  # walls
    "yellow": (255, 255, 0),  # button highlight
}

# Board and cell parameters
PADDING = 32
v_cells, h_cells = 30, 30 # Rows and columns
cell_size = min(width, height) // max(v_cells, h_cells)

# Start and target
start = None
target = None
walls = set()

# Fonts for buttons
font = pygame.font.Font(None, 30)

# Buttons
def draw_button(text, x, y):
    button = pygame.Rect(x, y, 120, 40)
    pygame.draw.rect(screen, colors["white"], button)
    pygame.draw.rect(screen, colors["black"], button, 2)
    text_surface = font.render(text, True, colors["black"])
    screen.blit(text_surface, (x + 10, y + 10))
    return button

def save_maze():
    # Save the maze layout to a JSON file
    maze_data = {
        "walls": list(walls),
        "start": start,
        "target": target,
    }
    with open("saved_maze.json", "w") as f:
        json.dump(maze_data, f)
    print("Maze saved to saved_maze.json")
    
    # Save the maze as an image (PNG format)
    save_maze_image()

def save_maze_image():
    # Create a new surface to render the maze to an image
    maze_surface = pygame.Surface((width, height - 80))
    maze_surface.fill(colors["black"])  # Fill with background color

    # Draw the maze elements onto the surface
    for x, y in walls:
        pygame.draw.rect(maze_surface, colors["white"], (x * cell_size, y * cell_size, cell_size, cell_size))
    if start:
        pygame.draw.circle(maze_surface, colors["blue"], (start[0] * cell_size + cell_size // 2, start[1] * cell_size + cell_size // 2), cell_size // 3)
    if target:
        pygame.draw.circle(maze_surface, colors["red"], (target[0] * cell_size + cell_size // 2, target[1] * cell_size + cell_size // 2), cell_size )

    # Save the surface to a PNG file
    pygame.image.save(maze_surface, "saved_maze.png")
    print("Maze image saved as saved_maze.png")

# Main loop
def main():
    global start, target, walls
    screen.fill(colors["black"])

    save_button = draw_button("Save Maze", 460, height - 60)
    draw_button("Draw Walls", 20, height - 60)
    erase_button = draw_button("Erase Walls", 160, height - 60)

    drawing_walls = False
    erasing_walls = False

    while True:
        screen.fill(colors["black"])
        draw_grid()

        # Button events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if save_button.collidepoint(mouse_pos):
                    save_maze()
                elif erase_button.collidepoint(mouse_pos):
                    erasing_walls = not erasing_walls
                    drawing_walls = False
                elif 20 <= mouse_pos[0] <= 140 and height - 60 <= mouse_pos[1] <= height - 20:
                    drawing_walls = not drawing_walls
                    erasing_walls = False
                elif mouse_pos[1] < height - 60:
                    cell_pos = (mouse_pos[0] // cell_size, mouse_pos[1] // cell_size)
                    if drawing_walls:
                        walls.add(cell_pos)
                    elif erasing_walls:
                        walls.discard(cell_pos)
                    else:
                        if start is None:
                            start = cell_pos
                        elif target is None:
                            target = cell_pos

            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left-click held down
                    mouse_pos = pygame.mouse.get_pos()
                    cell_pos = (mouse_pos[0] // cell_size, mouse_pos[1] // cell_size)
                    if drawing_walls:
                        walls.add(cell_pos)
                    elif erasing_walls:
                        walls.discard(cell_pos)

        # Draw buttons
        draw_button("Draw Walls", 20, height - 60)
        erase_button = draw_button("Erase Walls", 160, height - 60)
        save_button = draw_button("Save Maze", 460, height - 60)

        # Draw the current state of the maze (walls, start, target)
        draw_maze()

        pygame.display.flip()

# Draw grid and maze elements
def draw_grid():
    for x in range(0, width, cell_size):
        for y in range(0, height - 80, cell_size):
            pygame.draw.rect(screen, colors["white"], (x, y, cell_size, cell_size), 1)

def draw_maze():
    for x, y in walls:
        pygame.draw.rect(screen, colors["gray"], (x * cell_size, y * cell_size, cell_size, cell_size))
    if start:
        pygame.draw.circle(screen, colors["blue"], (start[0] * cell_size + cell_size // 2, start[1] * cell_size + cell_size // 2), cell_size // 3)
    if target:
        pygame.draw.circle(screen, colors["red"], (target[0] * cell_size + cell_size // 2, target[1] * cell_size + cell_size // 2), cell_size // 3)

if __name__ == "__main__":
    main()
