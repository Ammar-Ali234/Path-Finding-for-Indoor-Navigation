import pygame
import json
import heapq
from PIL import Image

# Define colors
colors = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "blue": (0, 0, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),  # Color for intermediate nodes in the path
    "orange": (255, 165, 0),  # Color for nearby (side) nodes
}

# Maze settings
width, height = 600, 300
grid_size = 70
cell_size = width // grid_size

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pathfinding Visualizer")

# Load maze data
def load_maze(filename="saved_maze.json"):
    with open(filename, "r") as file:
        data = json.load(file)
    walls = set(tuple(cell) for cell in data["walls"])
    start = tuple(data["start"]) if data["start"] else None
    target = tuple(data["target"]) if data["target"] else None
    nodes = {key: tuple(value) for key, value in data.get("nodes", {}).items()}  # Convert to tuple
    return walls, start, target, nodes

# A* Algorithm for pathfinding
def a_star(walls, start, target, nodes):
    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, target)}

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == target:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()

            # Find intermediate nodes directly on the path
            intermediate_nodes = [node_name for node_name, coords in nodes.items() if coords in path]
            
            # Find side nodes (nodes close to the path but not on it)
            side_nodes = [node_name for node_name, coords in nodes.items() if coords not in path and any(heuristic(coords, p) <= 4 for p in path)]

            print("Intermediate Nodes on Path:", intermediate_nodes)
            print("Nearby Nodes (Side Nodes):", side_nodes)

            return path, intermediate_nodes, side_nodes

        for neighbor in get_neighbors(current):
            if neighbor in walls:
                continue
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, target)
                heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return [], [], []

# Manhattan Distance heuristic function
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Get neighboring nodes
def get_neighbors(node):
    x, y = node
    neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [(nx, ny) for nx, ny in neighbors if 0 <= nx < grid_size and 0 <= ny < grid_size]

# Main function to visualize the maze and pathfinding
def main():
    walls, start, target, nodes = load_maze()

    if not start or not target:
        print("Start or Target is missing in the maze. Please set both in the saved JSON.")
        pygame.quit()
        return

    path, intermediate_nodes, side_nodes = a_star(walls, start, target, nodes)

    # Prepare for capturing frames
    frames = []
    current_position = start
    path_index = 0  # To track the current path index
    running = True

    while running:
        screen.fill(colors["black"])

        # Draw grid
        for x in range(0, width, cell_size):
            pygame.draw.line(screen, colors["white"], (x, 0), (x, height))
        for y in range(0, height, cell_size):
            pygame.draw.line(screen, colors["white"], (0, y), (width, y))

        # Draw walls
        for wall in walls:
            pygame.draw.rect(screen, colors["white"], pygame.Rect(wall[0] * cell_size, wall[1] * cell_size, cell_size, cell_size))

        # Draw start and target positions
        pygame.draw.rect(screen, colors["blue"], pygame.Rect(start[0] * cell_size, start[1] * cell_size, cell_size, cell_size))
        pygame.draw.rect(screen, colors["red"], pygame.Rect(target[0] * cell_size, target[1] * cell_size, cell_size, cell_size))

        # Draw intermediate nodes (on path)
        for node in intermediate_nodes:
            x, y = nodes[node]
            pygame.draw.rect(screen, colors["purple"], pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))

        # Draw nearby nodes (side nodes)
        for node in side_nodes:
            x, y = nodes[node]
            pygame.draw.rect(screen, colors["orange"], pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))

        # Draw the path so far (green)
        for i in range(path_index + 1):
            pygame.draw.rect(screen, colors["green"], pygame.Rect(path[i][0] * cell_size, path[i][1] * cell_size, cell_size, cell_size))

        # Draw the current position of the moving point (yellow)
        pygame.draw.rect(screen, colors["yellow"], pygame.Rect(current_position[0] * cell_size, current_position[1] * cell_size, cell_size, cell_size))

        # Capture the current frame
        frame = pygame.surfarray.array3d(pygame.display.get_surface())  # Convert surface to array
        frames.append(frame)

        # Move to the next point in the path
        if current_position != target:
            # Update the path index and move to the next step
            path_index += 1
            current_position = path[path_index]
            pygame.display.flip()
        else:
            break

        # To stop the window from freezing and allow user to quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # Convert frames to images and save as GIF using Pillow
    images = [Image.fromarray(frame) for frame in frames]
    images[0].save("animation.gif", save_all=True, append_images=images[1:], loop=0, duration=200)

    pygame.quit()

if __name__ == "__main__":
    main()
