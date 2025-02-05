import pygame
import json
import heapq

# Define colors
colors = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "blue": (0, 0, 255),
    "red": (255, 0, 0),
    "gray": (128, 128, 135),
    "green": (0, 255, 0),
    "yellow": (255, 255, 0),
}

# Maze settingss
width, height = 600,300
grid_size = 70
cell_size = width // grid_size

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Pathfinding Visualizer')

# Load maze data
def load_maze(filename="saved_maze.json"):
    with open(filename, "r") as file:
        data = json.load(file)
    walls = set(tuple(cell) for cell in data["walls"])
    start = tuple(data["start"]) if data["start"] else None
    target = tuple(data["target"]) if data["target"] else None
    return walls, start, target

# A* Algorithm for pathfinding
def a_star(walls, start, target):
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
            path.reverse()
            return path

        for neighbor in get_neighbors(current):
            if neighbor in walls:
                continue
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, target)
                heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return []

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(node):
    x, y = node
    neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    return [(nx, ny) for nx, ny in neighbors if 0 <= nx < grid_size and 0 <= ny < grid_size]

# Main loop to visualize the maze and pathfinding
def main():
    walls, start, target = load_maze()

    if not start or not target:
        print("Start or Target is missing in the maze. Please set both in the saved JSON.")
        pygame.quit()
        return

    path = a_star(walls, start, target)

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

        # Draw path
        for step in path:
            pygame.draw.rect(screen, colors["green"], pygame.Rect(step[0] * cell_size, step[1] * cell_size, cell_size, cell_size))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()
