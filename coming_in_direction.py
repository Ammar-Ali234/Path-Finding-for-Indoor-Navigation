
import json
import heapq
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

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
    if curr_node in reference_path:
        return "Straight"

    min_distance = float("inf")
    closest_point = None
    for path_point in reference_path:
        distance = heuristic(curr_node, path_point)
        if distance < min_distance:
            min_distance = distance
            closest_point = path_point

    if closest_point is None:
        return "Unknown"

    dx = curr_node[0] - closest_point[0]
    dy = curr_node[1] - closest_point[1]

    if abs(dx) > abs(dy):
        return "Left" if dx < 0 else "Right"
    else:
        return "Left" if dy < 0 else "Right"

def get_node_sequence(path, nodes):
    dynamic_nodes = []
    for step in path:
        for name, coords in nodes.items():
            if coords == step and name not in dynamic_nodes:
                dynamic_nodes.append(name)
        for name, coords in nodes.items():
            if name not in dynamic_nodes and any(heuristic(coords, p) <= 4 for p in path[:path.index(step)+1]):
                dynamic_nodes.append(name)
    return dynamic_nodes

def update_sequence_from_position(full_sequence, current_node, nodes):
    if current_node not in full_sequence:
        return full_sequence
    
    current_index = full_sequence.index(current_node)
    return full_sequence[current_index:]

def create_visualization_frame(walls, path, nodes, current_node, active_nodes, fig, ax):
    """Create a single frame for the visualization with Y-axis flipped."""
    ax.clear()
    
    # Get grid size for Y-axis flip
    grid_size = 70  # Using default grid size
    
    # Plot walls with flipped Y coordinates
    if walls:
        wall_xs, wall_ys = zip(*walls)
        wall_ys = [grid_size - y - 1 for y in wall_ys]  # Flip Y coordinates
        ax.scatter(wall_xs, wall_ys, color='gray', marker='s', s=100, alpha=0.5, label='Walls')
    
    # Plot path with flipped Y coordinates
    path_xs, path_ys = zip(*path)
    path_ys = [grid_size - y - 1 for y in path_ys]  # Flip Y coordinates
    ax.plot(path_xs, path_ys, 'b-', alpha=0.5, label='Path')
    
    # Plot all nodes with flipped Y coordinates
    for name, coords in nodes.items():
        flipped_coords = (coords[0], grid_size - coords[1] - 1)  # Flip Y coordinate
        if name in active_nodes:
            color = 'g'  # Active nodes in green
            alpha = 1.0
        else:
            color = 'r'  # Inactive nodes in red
            alpha = 0.3
        ax.scatter(flipped_coords[0], flipped_coords[1], color=color, alpha=alpha, s=100)
        ax.annotate(name, (flipped_coords[0], flipped_coords[1]), xytext=(5, 5), textcoords='offset points')
    
    # Highlight current node with flipped Y coordinate
    if current_node in nodes:
        current_coords = nodes[current_node]
        flipped_current = (current_coords[0], grid_size - current_coords[1] - 1)  # Flip Y coordinate
        ax.scatter(flipped_current[0], flipped_current[1], color='yellow', 
                  edgecolor='black', s=200, zorder=5, label='Current Node')
    
    ax.grid(True)
    ax.set_title(f'Maze Navigation - Current Node: {current_node}')
    ax.legend()

def find_target_node(target_coords, nodes):
    """Find the node name corresponding to target coordinates."""
    for name, coords in nodes.items():
        if coords == target_coords:
            return name
    return None

def main():
    walls, start, target, nodes = load_maze()
    if not start or not target:
        print("Start or Target is missing in the maze.")
        return

    path = a_star(walls, start, target, nodes)
    reference_path = set(path)
    
    # Find target node name
    target_node = find_target_node(target, nodes)
    if not target_node:
        print("Target coordinates don't match any node.")
        return
    
    # Get initial complete sequence
    full_sequence = get_node_sequence(path, nodes)
    node_directions = {node: get_direction(reference_path, nodes[node]) for node in full_sequence}
    
    # Show initial sequence
    print("\n=== Initial Node Sequence ===")
    for node in full_sequence:
        print(f"{node}: {node_directions.get(node, 'Unknown')}")
    
    # Setup visualization
    fig, ax = plt.subplots(figsize=(12, 8))
    frames = []
    
    # Interactive navigation
    visited_nodes = []
    while True:
        print("\nEnter current node name (or 'exit' to quit):")
        current_node = input().strip()
        
        if current_node.lower() == 'exit':
            break
            
        if current_node not in nodes:
            print("Invalid node name. Please try again.")
            continue
        
        visited_nodes.append(current_node)
        updated_sequence = update_sequence_from_position(full_sequence, current_node, nodes)
        updated_sequence = updated_sequence[1:3]
        print("\n=== Updated Node Sequence ===")
        for node in updated_sequence:
            print(f"{node}: {node_directions.get(node, 'Unknown')}")
        
        # Create and save visualization frame
        create_visualization_frame(walls, path, nodes, current_node, updated_sequence, fig, ax)
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(frame)
        
        # Check if target reached
        if current_node == target_node:
            print("\nTarget reached! Saving visualization...")
            break
    
    if frames:
        print("\nSaving visualization to 'maze_navigation.gif'...")
        # Save frames as GIF
        writer = PillowWriter(fps=1)
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        ani = FuncAnimation(fig, lambda frame: create_visualization_frame(walls, path, nodes, 
                                                                      visited_nodes[frame], 
                                                                      update_sequence_from_position(full_sequence, visited_nodes[frame], nodes),
                                                                      fig, ax),
                          frames=len(frames), interval=1000)
        ani.save('maze1_navigation.gif', writer=writer)
        print("Visualization saved!")
    
    plt.close()

if __name__ == "__main__":
    main()