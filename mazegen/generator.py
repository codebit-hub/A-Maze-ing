import os
import sys
import random
import time
from .cell import Cell
from .config import MazeConfig
from . import colors


class MazeGenerator:
    """Core engine for generating and manipulating the maze."""

    def __init__(self, config_filepath: str) -> None:
        """Initializes the generator with a given configuration file."""
        # Load and validate the configuration
        self.config: MazeConfig = MazeConfig(config_filepath)

        # Initialize the 2D grid (list of lists) with empty Cells
        self.grid: list[list[Cell]] = [
            [Cell(x, y) for x in range(self.config.width)]
            for y in range(self.config.height)
        ]

        # Increase recursion depth for large mazes
        sys.setrecursionlimit(10000)

        # Handle the random seed as required
        if self.config.seed is not None:
            random.seed(self.config.seed)
        else:
            self.config.seed = random.randint(0, 99999999)
            random.seed(self.config.seed)

        # Embed the required "42" pattern in the center
        self._embed_42_pattern()


    def _embed_42_pattern(self) -> None:
        """Places the solid '42' block in the center of the maze."""
        # The '42' pattern requires a 7x5 space. We calculate the top-left offset.
        # e.g. x: 20 - 7 = 13 // 2 = 6;
        # e.g. y:15 - 5 = 10 // 2 = 5
        offset_x: int = (self.config.width - 7) // 2
        offset_y: int = (self.config.height - 5) // 2

        # Relative coordinates for the "42" shape
        pattern_42: list[tuple[int, int]] = [
            # '4'
            (0, 0), (2, 0), (0, 1), (2, 1), (0, 2),
            (1, 2), (2, 2), (2, 3), (2, 4),
            # '2'
            (4, 0), (5, 0), (6, 0), (6, 1), (4, 2),
            (5, 2), (6, 2), (4, 3), (4, 4), (5, 4), (6, 4)
        ]

        for rel_x, rel_y in pattern_42:
            tx: int = offset_x + rel_x
            ty: int = offset_y + rel_y

            # Graceful error handling
            if (tx, ty) == self.config.entry or (tx, ty) == self.config.exit:
                raise ValueError("Entry or Exit coordinates overlap with the '42' pattern.")

            # Mark these cells as part of the pattern and pre-visit them
            # so the generation algorithms ignore them completely.
            self.grid[ty][tx].is_42 = True
            self.grid[ty][tx].visited = True
            self.grid[ty][tx].walls = 15


    # Maze Generation Algorithms --------------------------
    # Depth First Search (DFS)
    def dfs_generate(self, animate: bool = False, delay: float = 0.02) -> None:
        """DFS maze generation from a valid random point"""
        # Picking a random starting coordinate
        start_x = random.randint(0, self.config.width - 1)
        start_y = random.randint(0, self.config.height - 1)

        # Rule out '42' block to start from
        while self.grid[start_y][start_x].is_42:
            start_x = random.randint(0, self.config.width - 1)
            start_y = random.randint(0, self.config.height - 1)

        # Carve the maze
        self._make_maze_dfs(start_x, start_y, animate, delay)

        # Make the maze imperfect if PERFECT=False
        if not self.config.perfect:
            self._create_imperfect_loops()


    def _make_maze_dfs(self, x: int, y: int, animate: bool, delay: float) -> None:
        """Recursive DFS algorithm to carve paths"""
        # Mark current cell as visited to skip it
        self.grid[y][x].visited = True

        # Animation ----------------------------
        if animate:
            self.render_terminal()
            time.sleep(delay)

        # Define 4 moves:
        #   x_change, y_change, wall_break_to_leave, wall_break_to_enter
        #   dx, dy, dir_out, dir_in
        options = [
            (0, -1, Cell.NORTH, Cell.SOUTH),
            (1, 0, Cell.EAST, Cell.WEST),
            (0, 1, Cell.SOUTH, Cell.NORTH),
            (-1, 0, Cell.WEST, Cell.EAST)
        ]

        # Shuffle the direction of maze for randomization
        random.shuffle(options)

        # Determine the correct possition to plot
        for dx, dy, dir_out, dir_in in options:
            tx = x + dx
            ty = y + dy

            # Check if target cell is within grid boundaries
            if 0 <= tx < self.config.width and 0 <= ty < self.config.height:
                # Check if visitied to protect '42' block
                if not self.grid[ty][tx].visited:
                    # Remove walls between two cells
                    self.grid[y][x].remove_wall(dir_out)
                    self.grid[ty][tx].remove_wall(dir_in)
                    # Recursively jump into new cell to carve on
                    self._make_maze_dfs(tx, ty, animate, delay)


    def get_maze_hex_string(self) -> str:
        """Converts maze walls into required hexadecimal format"""
        output: str = ""
        for y in range(self.config.height):
            for x in range(self.config.width):
                # Format integer as uppercase Hexadecimal
                # (e.g., 15 -> 'F', 10 -> 'A')
                output += f"{self.grid[y][x].walls:X}"
            output += "\n"
        return output


    # Prim's Algorithm
    def prims_generate(self, animate: bool = False, delay: float = 0.02) -> None:
        """Randomized Prim's maze generation algorithm"""
        # Pick random entry point out of 42 block, but within bounds
        start_x: int = random.randint(0, self.config.width - 1)
        start_y: int = random.randint(0, self.config.height - 1)
        while self.grid[start_y][start_x].is_42:
            start_x: int = random.randint(0, self.config.width - 1)
            start_y: int = random.randint(0, self.config.height - 1)

        # Marking the entry as a visited cell
        self.grid[start_y][start_x].visited = True

        # A list for tracking cells at the edge of the growing maze
        frontier: list[tuple[int, int]] = []

        # Adds neighbors to the frontier
        def add_frontier(x: int, y: int) -> None:
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                tx, ty = x + dx, y + dy
                if 0 <= tx < self.config.width and 0 <= ty < self.config.height:
                    if not self.grid[ty][tx].visited and (tx, ty) not in frontier:
                        frontier.append((tx, ty))
        add_frontier(start_x, start_y)

        # Grow the maze till boarders are reached
        while frontier:
            # Pick a random cell from the edge of maze
            idx: int = random.randint(0, len(frontier) - 1)
            tx, ty = frontier.pop(idx)

            self.grid[ty][tx].visited = True

            # Find all neighbors of the cell that are part of the maze
            in_maze_neighbors = []
            options: list[tuple[int, int, int, int]] = [
                (0, -1, Cell.NORTH, Cell.SOUTH),
                (1, 0, Cell.EAST, Cell.WEST),
                (0, 1, Cell.SOUTH, Cell.NORTH),
                (-1, 0, Cell.WEST, Cell.EAST)
            ]

            for dx, dy, dir_out, dir_in in options:
                nx, ny = tx + dx, ty + dy
                if 0 <= nx < self.config.width and 0 <= ny <self.config.height:
                    # Avoid 42 block
                    if self.grid[ny][nx].visited and not self.grid[ny][nx].is_42:
                        in_maze_neighbors.append((nx, ny, dir_out, dir_in))

            # Connect target cell to one random adjacent maze cell
            if in_maze_neighbors:
                nx, ny, dir_out, dir_in = random.choice(in_maze_neighbors)
                self.grid[ty][tx].remove_wall(dir_out)
                self.grid[ny][nx].remove_wall(dir_in)

                # Animation hook
                if animate:
                    self.render_terminal()
                    time.sleep(delay)

            # Add target's unvisited neighbors to the frontier
            add_frontier(tx, ty)

        # Break the generated perfect maze if PERFECT=False
        if not self.config.perfect:
            self._create_imperfect_loops()


    # Function that creates Imperfect mazes when PERFECT=False
    # out of Perfectly created mazes

    def _create_imperfect_loops(self) -> None:
        """Makes imperfect 'Braid Mazes' with looped dead-ends."""
        # Converts into an imperfect 'Braid Maze' by
        # turning dead ends into round loops.
        for y in range(self.config.height):
            for x in range(self.config.width):
                cell = self.grid[y][x]

                # Never touch the 42 block!
                if cell.is_42:
                    continue

                # Count how many walls are currently closed on this cell
                closed_walls = sum([
                    cell.has_wall(Cell.NORTH),
                    cell.has_wall(Cell.EAST),
                    cell.has_wall(Cell.SOUTH),
                    cell.has_wall(Cell.WEST)
                ])

                # If it has exactly 3 closed walls, it is a Dead End!
                if closed_walls == 3:

                    # Have a 50% chance to open this dead end
                    # to create a loop
                    if random.random() < 0.50:

                        # Find all CLOSED walls that don't lead out
                        # of bounds
                        options = []
                        if y > 0 and cell.has_wall(Cell.NORTH):
                            options.append((0, -1, Cell.NORTH, Cell.SOUTH))
                        if x < self.config.width - 1 and cell.has_wall(Cell.EAST):
                            options.append((1, 0, Cell.EAST, Cell.WEST))
                        if y < self.config.height - 1 and cell.has_wall(Cell.SOUTH):
                            options.append((0, 1, Cell.SOUTH, Cell.NORTH))
                        if x > 0 and cell.has_wall(Cell.WEST):
                            options.append((-1, 0, Cell.WEST, Cell.EAST))

                        # Shuffle the valid walls
                        random.shuffle(options)

                        for dx, dy, dir_out, dir_in in options:
                            tx, ty = x + dx, y + dy

                            # If the neighbor is safe,
                            # break the wall and STOP
                            if not self.grid[ty][tx].is_42:
                                cell.remove_wall(dir_out)
                                self.grid[ty][tx].remove_wall(dir_in)
                                break
                                # We only break ONE wall per dead end!


    # Preliminary Grid Generation Algorithm
    # Plot the dotted test grid
    # def debug_print_grid(self) -> None:
    #     """A temporary visualizer to test Stage 1."""
    #     print(f"\n--- Maze Grid ({self.config.width}x{self.config.height}) ---")
    #     for y in range(self.config.height):
    #         row_str = ""
    #         for x in range(self.config.width):
    #             if (x, y) == self.config.entry:
    #                 row_str += "EN "
    #             elif (x, y) == self.config.exit:
    #                 row_str += "EX "
    #             elif self.grid[y][x].is_42:
    #                 row_str += "██ "
    #             else:
    #                 row_str += " . "
    #         print(row_str)
    #     print("------------------------\n")

    # Solution Finding Algorithms -----------------------
    # Breadth-first search (BFS) - shortest path
    def solve_shortest_path_bfs(self, start_x: int, start_y: int,
        end_x: int, end_y: int) -> str:
        """Finds the absolute shortest path (BFS)"""
        # a set keeps track of visited coordinates
        visited: set = set()
        visited.add((start_x, start_y))

        # A queue (First-In, First-Out).
        # It stores tuples of: (current_x, current_y, "PATH_TAKEN_SO_FAR")
        queue: list[tuple[int, int, str]] = [(start_x, start_y, "")]

        while queue:
            # Pop the first item out of the front of the queue
            x, y, current_path = queue.pop(0)

            # If exist reached, return the path
            if x == end_x and y == end_y:
                return current_path

            # 4 direction we can move to
            moves = [
                (0, -1, Cell.NORTH, "N"),
                (1, 0, Cell.EAST, "E"),
                (0, 1, Cell.SOUTH, "S"),
                (-1, 0, Cell.WEST, "W")
            ]

            for dx, dy, wall_mask, dir_str in moves:
                # Move if there is no wall
                if not self.grid[y][x].has_wall(wall_mask):
                    tx = x + dx
                    ty = y + dy

                    # Move only if not visited before
                    if (tx, ty) not in visited:
                        # Mark as visited and add to back of gueue
                        visited.add((tx, ty))
                        queue.append((tx, ty, current_path + dir_str))

        # Returns empty str if not path possible
        return ""


    def solve_path_dfs(self,
                       start_x: int, start_y: int, end_x: int, end_y: int) -> str:
        """Finds a valid path by Depth-First Search (DFS)"""
        visited = set()
        visited.add((start_x, start_y))

        stack: list[tuple[int, int, str]] = [(start_x, start_y, "")]

        while stack:
            # pop(-1) takes cell from the back of the line
            # this causes the algorithm to dive deep instead of
            # spreadig wide like with BFS
            x, y, current_path = stack.pop(-1)

            if x == end_x and y == end_y:
                return current_path

            moves = [
                (0, -1, Cell.NORTH, "N"),
                (1, 0, Cell.EAST, "E"),
                (0, 1, Cell.SOUTH, "S"),
                (-1, 0, Cell.WEST, "W")
            ]

            # RAndomize the moves for chaotic, winding paths
            random.shuffle(moves)

            for dx, dy, wall_mask, dir_str in moves:
                if not self.grid[y][x].has_wall(wall_mask):
                    tx, ty = x + dx, y + dy
                    if (tx, ty) not in visited:
                        visited.add((tx, ty))
                        stack.append((tx, ty, current_path + dir_str))
        return ""


    # Saving the maze to the external file -----------------------
    def save_maze_to_file(self) -> None:
        """Saves maze to output file as required"""
        try:
            with open(self.config.output_file, 'w') as f:
                # Write hexadecimal block to maze.txt
                # new lines added by get_maze_hex_string
                f.write(self.get_maze_hex_string().strip() + '\n')

                # EXTRA DATA for debugging
                # Entry coordinates
                # ex, ey = self.config.entry
                # f.write(f"{ex}, {ey}\n")

                # Exit coordinates
                # xx, xy = self.config.exit
                # f.write(f"{xx}, {xy}\n")

                # Solution path string
                # f.write(solution_path)

        except PermissionError:
            raise PermissionError("Permission denied: "
                                  f"Cannot write to {self.config.output_file}")

    # ANIMATION
    def _get_path_coords(self,
                start_x: int, start_y: int,
                path_str: str) -> set[tuple[int, int]]:
        """Converts directional string ('NESW') into coords (X, Y)"""
        coords: set[tuple[int, int]] = set()
        cx, cy = start_x, start_y
        for move in path_str:
            if move == 'N': cy -= 1
            elif move == 'S': cy += 1
            elif move == 'E': cx += 1
            elif move == 'W': cx -= 1
            coords.add((cx, cy))
        return coords


    def render_terminal(self, player_pos: tuple[int, int] | None = None,
                        solution_mode: int = 0, wall_color: str = colors.WHITE) -> None:
        """Renders the maze. solution_mode: 0=Off, 1=BFS Shortest, 2=DFS Winding"""
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')

        # Set default player's entry position to start from config.txt
        px, py = player_pos if player_pos else self.config.entry

        # Calculate the solution coordinates
        # Calculate dynamic solution coords based on CURRENT player position!
        solution_coords: set[tuple[int, int]] = set()
        ex, ey = self.config.exit

        if solution_mode == 1:
            path_str = self.solve_shortest_path_bfs(px, py, ex, ey)
            solution_coords = self._get_path_coords(px, py, path_str)
        elif solution_mode == 2:
            path_str = self.solve_path_dfs(px, py, ex, ey)
            solution_coords = self._get_path_coords(px, py, path_str)

        # Draw maze row-by-row
        for y in range(self.config.height):
            # North boarder wall
            line1 = ""
            # West and East boarder walls
            line2 = ""
            for x in range(self.config.width):
                cell: tuple[int, int] = self.grid[y][x]

                # Determine insides the cell
                center: str = "   "
                if (x, y) == (px, py):
                    center = f"{colors.GREEN}🚗 {wall_color}"  # Player
                elif (x, y) == self.config.exit:
                    center = f"{colors.RED} E {wall_color}"    # Exit
                elif (x, y) == self.config.entry:
                    center = f"{colors.BLUE} S {wall_color}"    # Start
                elif (x, y) in solution_coords:
                    center = f"{colors.YELLOW} ● {wall_color}"  # Solution
                elif cell.is_42:
                    center = f"{colors.MAGENTA}███{wall_color}" # 42!

                # Draw North wall (line1)
                if cell.has_wall(Cell.NORTH):
                    line1 += "█████"
                else:
                    line1 += "█   █"

                # Draw West and East walls (line2)
                left = "█" if cell.has_wall(Cell.WEST) else " "
                right = "█" if cell.has_wall(Cell.EAST) else " "

                if cell.walls == 15 and not cell.is_42:
                    # # Solid block if unvisited (shouldn't happen in perfect maze)
                    line2 += "█████"
                else:
                    line2 += f"{left}{center}{right}"

            print(f"{wall_color}{line1}{colors.RESET}")
            print(f"{wall_color}{line2}{colors.RESET}")

        # Draw the final bottom border
        print(f"{wall_color}" + "█████" * self.config.width +
              f"{colors.RESET}")




