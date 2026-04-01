import sys
from mazegen.generator import MazeGenerator


def main() -> None:
    "Main program"
    # Take only 1 agrs
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config_filepath = sys.argv[1]

    try:
        # Initialize generator/parse the config
        maze = MazeGenerator(config_filepath)

        # Generate maze layout (DFS)
        maze.dfs_generate()

        # Solve the maze (BFS)
        ex, ey = maze.config.entry
        xx, xy = maze.config.exit
        solution = maze.solve_shortest_path_bfs(ex, ey, xx, xy)

        if not solution:
            print("[!] Warning: Generated maze has "
                  "no valid path from Entry to Exit.")
        else:
            print(f"[i] Solution path found: {solution}")

        # Save to file
        maze.save_maze_to_file()
        print("[+] Success! Maze generated and saved "
              f"to '{maze.config.output_file}'.")

    # Error handling
    except FileNotFoundError as e:
        print(f"[!] File Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"[!] Permission Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"[!] Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
