# test_stage1.py
from mazegen.generator import MazeGenerator
from mazegen import colors

try:
    maze = MazeGenerator("config.txt")
    maze.dfs_generate()

    # Render with cyan walls, showing the solution path!
    maze.render_terminal(show_solution=True, wall_color=colors.CYAN)

except Exception as e:
    print(f"Error: {e}")
