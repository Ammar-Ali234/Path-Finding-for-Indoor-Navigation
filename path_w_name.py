import pygame
import json
import sys

# Initialize Pygame
pygame.init()

# Screen settings
width, height = 1500, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Maze Creator")

# Colors
colors = {
    "black": (0, 0, 0),  # background
    "white": (255, 255, 255),  # grid
    "blue": (0, 0, 255),  # start
    "red": (255, 0, 0),  # target
    "gray": (128, 128, 128),  # walls
    "yellow": (255, 255, 0),  # button highlight
    "green": (0, 255, 0),  # nodes
    "error": (255, 0, 0),  # error text
}

# Board and cell parameters
v_cells, h_cells = 30, 30  # Rows and columns
cell_size = min(width, height) // max(v_cells, h_cells)

# Maze elements
start = None
target = None
walls = set()
nodes = {}  # Store nodes with their names and positions: {name: (x, y)}

# Fonts
font = pygame.font.Font(None, 30)
error_font = pygame.font.Font(None, 40)

# Button helper function
def draw_button(text, x, y, active):
    button = pygame.Rect(x, y, 120, 40)
    pygame.draw.rect(screen, colors["yellow"] if active else colors["white"], button)
    pygame.draw.rect(screen, colors["black"], button, 2)
    text_surface = font.render(text, True, colors["black"])
    screen.blit(text_surface, (x + 10, y + 10))
    return button

# Save maze
def save_maze():
    maze_data = {
        "walls": list(walls),
        "start": start,
        "target": target,
        "nodes": nodes,
    }
    with open("saved_maze.json", "w") as f:
        json.dump(maze_data, f, indent=4)
    print("Maze saved to saved_maze.json")
    save_maze_image()

def save_maze_image():
    maze_surface = pygame.Surface((width, height - 80))
    maze_surface.fill(colors["black"])

    for x, y in walls:
        pygame.draw.rect(maze_surface, colors["gray"], (x * cell_size, y * cell_size, cell_size, cell_size))
    if start:
        pygame.draw.circle(maze_surface, colors["blue"], (start[0] * cell_size + cell_size // 2, start[1] * cell_size + cell_size // 2), cell_size // 3)
    if target:
        pygame.draw.circle(maze_surface, colors["red"], (target[0] * cell_size + cell_size // 2, target[1] * cell_size + cell_size // 2), cell_size // 3)
    for name, (x, y) in nodes.items():
        pygame.draw.circle(maze_surface, colors["green"], (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2), cell_size // 3)
        text_surface = font.render(name, True, colors["white"])
        maze_surface.blit(text_surface, (x * cell_size + cell_size // 2 - text_surface.get_width() // 2, y * cell_size + cell_size // 2 - text_surface.get_height() // 2))

    pygame.image.save(maze_surface, "saved_maze.png")
    print("Maze image saved as saved_maze.png")

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
    for name, (x, y) in nodes.items():
        pygame.draw.circle(screen, colors["green"], (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2), cell_size // 3)
        text_surface = font.render(name, True, colors["white"])
        screen.blit(text_surface, (x * cell_size + cell_size // 2 - text_surface.get_width() // 2, y * cell_size + cell_size // 2 - text_surface.get_height() // 2))

# Dialog box for user input
def get_user_input(prompt):
    input_box = pygame.Rect(100, 100, 300, 50)
    active = True
    user_input = ""
    font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()

    while active:
        screen.fill(colors["black"])
        text_surface = font.render(f"{prompt}: {user_input}", True, colors["white"])
        pygame.draw.rect(screen, colors["white"], input_box, 2)
        screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode
        clock.tick(30)

    return user_input.strip()

# Show error message
def show_error_message(message):
    error_surface = error_font.render(message, True, colors["error"])
    screen.blit(error_surface, (width // 2 - error_surface.get_width() // 2, height // 2 - error_surface.get_height() // 2))

# Main loop
def main():
    global start, target, walls, nodes
    screen.fill(colors["black"])

    # Initialize buttons
    save_button = draw_button("Save Maze", 460, height - 60, False)
    draw_walls_button = draw_button("Draw Walls", 20, height - 60, False)
    erase_walls_button = draw_button("Erase Walls", 160, height - 60, False)
    node_button = draw_button("Node Mode", 300, height - 60, False)
    start_button = draw_button("Start", 620, height - 60, False)
    target_button = draw_button("Target", 740, height - 60, False)

    # Modes
    drawing_walls = False
    erasing_walls = False
    placing_nodes = False
    setting_start = False
    setting_target = False

    # Mouse button states
    mouse_down = False

    while True:
        screen.fill(colors["black"])
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                mouse_down = True
                if save_button.collidepoint(mouse_pos):
                    save_maze()
                elif draw_walls_button.collidepoint(mouse_pos):
                    drawing_walls = not drawing_walls
                    erasing_walls = placing_nodes = setting_start = setting_target = False
                elif erase_walls_button.collidepoint(mouse_pos):
                    erasing_walls = not erasing_walls
                    drawing_walls = placing_nodes = setting_start = setting_target = False
                elif node_button.collidepoint(mouse_pos):
                    placing_nodes = not placing_nodes
                    drawing_walls = erasing_walls = setting_start = setting_target = False
                elif start_button.collidepoint(mouse_pos):
                    setting_start = not setting_start
                    drawing_walls = erasing_walls = placing_nodes = setting_target = False
                elif target_button.collidepoint(mouse_pos):
                    target_name = get_user_input("Enter Target Node Name")
                    if target_name in nodes:
                        target = nodes[target_name]
                    else:
                        show_error_message("Error: Target node not found.")
                elif mouse_pos[1] < height - 60:
                    cell_pos = (mouse_pos[0] // cell_size, mouse_pos[1] // cell_size)
                    if placing_nodes:
                        node_name = get_user_input("Enter Node Name")
                        if node_name and cell_pos not in walls and cell_pos not in nodes.values():
                            nodes[node_name] = cell_pos
                    elif drawing_walls:
                        walls.add(cell_pos)
                    elif erasing_walls:
                        walls.discard(cell_pos)
                    elif setting_start:
                        start = cell_pos
                        setting_start = False

            elif event.type == pygame.MOUSEMOTION and mouse_down:
                mouse_pos = pygame.mouse.get_pos()
                if drawing_walls:
                    cell_pos = (mouse_pos[0] // cell_size, mouse_pos[1] // cell_size)
                    walls.add(cell_pos)
                elif erasing_walls:
                    cell_pos = (mouse_pos[0] // cell_size, mouse_pos[1] // cell_size)
                    walls.discard(cell_pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False

        # Redraw buttons
        save_button = draw_button("Save Maze", 460, height - 60, False)
        draw_walls_button = draw_button("Draw Walls", 20, height - 60, drawing_walls)
        erase_walls_button = draw_button("Erase Walls", 160, height - 60, erasing_walls)
        node_button = draw_button("Node Mode", 300, height - 60, placing_nodes)
        start_button = draw_button("Start", 620, height - 60, setting_start)
        target_button = draw_button("Target", 740, height - 60, False)

        # Draw the maze elements
        draw_maze()

        pygame.display.flip()

if __name__ == "__main__":
    main()
