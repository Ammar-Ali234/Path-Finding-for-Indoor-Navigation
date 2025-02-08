import json
import heapq

def load_maze(filename="saved_maze.json"):
    with open(filename, "r") as file:
        data = json.load(file)
    return (
        set(tuple(cell) for cell in data["walls"]),
        tuple(data["start"]) if data["start"] else None,
        tuple(data["target"]) if data["target"] else None,
        {key: tuple(value) for key, value in data.get("nodes", {}).items()},
    )

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(node, grid_size=70):
    x, y = node
    neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [(nx, ny) for nx, ny in neighbors if 0 <= nx < grid_size and 0 <= ny < grid_size]

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

def get_direction(reference_path, curr_node):
    """
    Determines the movement direction of `curr_node` based on the reference path.

    Returns: "Straight", "Left", or "Right".
    """
    if curr_node in reference_path:
        return "Straight"  # Node is part of the path → Straight

    # Find the closest path point
    min_distance = float("inf")
    closest_point = None
    for path_point in reference_path:
        distance = heuristic(curr_node, path_point)
        if distance < min_distance:
            min_distance = distance
            closest_point = path_point

    if closest_point is None:
        return "Unknown"  # Should never happen

    # Determine direction based on relative position to the path
    dx = curr_node[0] - closest_point[0]
    dy = curr_node[1] - closest_point[1]

    if abs(dx) > abs(dy):  # Greater difference in X → Left/Right
        return "Left" if dx < 0 else "Right"
    else:  # Greater difference in Y → Up/Down
        return "Left" if dy < 0 else "Right"

def main():
    walls, start, target, nodes = load_maze()
    if not start or not target:
        print("Start or Target is missing in the maze.")
        return

    path = a_star(walls, start, target, nodes)
    reference_path = set(path)
    dynamic_nodes = []
    for step in path:
        for name, coords in nodes.items():
            if coords == step and name not in dynamic_nodes:
                dynamic_nodes.append(name)
        for name, coords in nodes.items():
            if name not in dynamic_nodes and any(heuristic(coords, p) <= 4 for p in path[:path.index(step)+1]):
                dynamic_nodes.append(name)
    
    node_directions = {node: get_direction(reference_path, nodes[node]) for node in dynamic_nodes}
    
    print("\n=== Node Sequence with Directions ===")
    for node in dynamic_nodes:
        print(f"{node}: {node_directions.get(node, 'Unknown')}")

if __name__ == "__main__":
    main()

