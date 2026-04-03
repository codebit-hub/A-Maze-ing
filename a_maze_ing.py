# a_maze_ing.py
import sys
import os
import tty
import termios

from mazegen.generator import MazeGenerator
from mazegen import colors

def getch() -> str:
    """Captures a single keypress from the terminal (Unix only)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def play_mode(maze: MazeGenerator, wall_color: str) -> None:
    """Interactive loop allowing the user to navigate the maze."""
    px, py = maze.config.entry
    ex, ey = maze.config.exit
    hint_mode = 0

    while True:
        maze.render_terminal(player_pos=(px, py), solution_mode=hint_mode, wall_color=wall_color)
        print(f"\n{colors.YELLOW}=== PLAY MODE ==={colors.RESET}")
        print("Use W, A, S, D to move. Press 'H' to toggle Hint. Press 'Q' to quit.")

        if (px, py) == (ex, ey):
            print(f"\n{colors.GREEN}🎉 YOU ESCAPED THE MAZE! 🎉{colors.RESET}")
            input("Press Enter to return to the menu...")
            return

        move = getch().lower()

        if move == 'q':
            return
        elif move == 'h':
            hint_mode = 1 if hint_mode == 0 else 0
        elif move == 'w' and not maze.grid[py][px].has_wall(maze.grid[py][px].NORTH):
            py -= 1
        elif move == 's' and not maze.grid[py][px].has_wall(maze.grid[py][px].SOUTH):
            py += 1
        elif move == 'a' and not maze.grid[py][px].has_wall(maze.grid[py][px].WEST):
            px -= 1
        elif move == 'd' and not maze.grid[py][px].has_wall(maze.grid[py][px].EAST):
            px += 1

def main() -> None:
    """Main program"""
    if len(sys.argv) == 2:
        config_filepath = sys.argv[1]
    elif len(sys.argv) == 1:
        config_filepath = "config.txt"
        print(f"[i] No config specified. Defaulting to '{config_filepath}'.")
    else:
        print("Usage: python3 a_maze_ing.py [config_file]")
        sys.exit(1)

    try:
        maze = MazeGenerator(config_filepath)
        maze.dfs_generate()

        color_idx = 0
        solution_mode = 0
        animate_gen = False
        is_perfect = maze.config.perfect

        # Track whether the user just saved the file
        just_saved = False

        while True:
            current_color = colors.COLOR_PALETTE[color_idx % len(colors.COLOR_PALETTE)]
            maze.render_terminal(solution_mode=solution_mode, wall_color=current_color)

            anim_str = f"{colors.GREEN}ON{colors.RESET}" if animate_gen else f"{colors.RED}OFF{colors.RESET}"
            perf_str = f"{colors.GREEN}PERFECT (Single Path){colors.RESET}" if is_perfect else f"{colors.YELLOW}IMPERFECT (Loops/Braid){colors.RESET}"

            # Create the dynamic save tag
            save_str = f" {colors.GREEN}[Saved!]{colors.RESET}" if just_saved else ""

            print(f"\n{colors.WHITE}=== A-Maze-Ing Menu ==={colors.RESET}")
            print(" 1. Regenerate Maze (DFS - Winding Paths)")
            print(" 2. Regenerate Maze (Prim's - Spiky Paths)")
            print(" 3. Show Shortest Path Solution (BFS)")
            print(" 4. Show Winding Path Solution (DFS)")
            print(" 5. Hide Solution Path")
            print(" 6. Change Wall Color")
            print(f" 7. Toggle Generation Animation [Current: {anim_str}]")
            print(f" 8. Toggle Perfect Maze         [Current: {perf_str}]")
            print(f" 9. {colors.GREEN}Play Mode (Find the exit!){colors.RESET}")
            print(f"10. Save Maze to File          {save_str}")
            print("11. Quit")

            choice = input("Choice (1-11): ").strip()

            # If they pick anything other than 10, clear the "Saved!" tag
            if choice != '10':
                just_saved = False

            if choice == '1':
                maze = MazeGenerator(config_filepath)
                maze.config.perfect = is_perfect
                maze.dfs_generate(animate=animate_gen)
                solution_mode = 0
            elif choice == '2':
                maze = MazeGenerator(config_filepath)
                maze.config.perfect = is_perfect
                maze.prims_generate(animate=animate_gen)
                solution_mode = 0
            elif choice == '3':
                solution_mode = 1
            elif choice == '4':
                solution_mode = 2
            elif choice == '5':
                solution_mode = 0
            elif choice == '6':
                color_idx += 1
            elif choice == '7':
                animate_gen = not animate_gen
            elif choice == '8':
                is_perfect = not is_perfect
            elif choice == '9':
                play_mode(maze, current_color)
            elif choice == '10':
                maze.save_maze_to_file()
                just_saved = True  # Trigger the tag for the next render
            elif choice == '11':
                print("[+] Goodbye!")
                break
            else:
                print("Invalid choice. Press Enter to try again.")
                input()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
