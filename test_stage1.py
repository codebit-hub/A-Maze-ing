# test_stage1.py
from mazegen.generator import MazeGenerator


try:
    # This uses the config.txt you already created
    maze = MazeGenerator("config.txt")
    print("Generating maze...")
    maze.dfs_generate()

    print("\nHexadecimal Output:")
    print(maze.get_maze_hex_string())

    # Get entry/exit coordinates from config
    ex, ey = maze.config.entry
    xx, xy = maze.config.exit

    # Run solver
    solution = maze.solve_shortest_path_bfs(ex, ey, xx, xy)
    print(f"\nSolution Path ({len(solution)} steps):")
    print(solution)


except Exception as e:
    print(f"Error: {e}")