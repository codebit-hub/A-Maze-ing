import os
import sys
import random
import time
from mazegen.cell import Cell
from mazegen.config import MazeConfig
from mazegen import colors


class MazeGenerator:
    """Core engine for generating and manipulating the maze."""

    def __init__(self, config_filepath: str) -> None:
        """Initializes the generator with a given configuration file."""
        self.config: MazeConfig = MazeConfig(config_filepath)

        self.grid: list[list[Cell]] = [
            [Cell(x, y) for x in range(self.config.width)]
            for y in range(self.config.height)
        ]

        sys.setrecursionlimit(10000)

        if self.config.seed is not None:
            random.seed(self.config.seed)
        else:
            self.config.seed = random.randint(0, 99999999)
            random.seed(self.config.seed)

        self._embed_42_pattern()

    def _embed_42_pattern(self) -> None:
        """Places the solid '42' block in the center of the maze."""
        offset_x: int = (self.config.width - 7) // 2
        offset_y: int = (self.config.height - 5) // 2

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

            if (tx, ty) == self.config.entry or (tx, ty) == self.config.exit:
                raise ValueError(
                    "Entry/Exit coordinates overlap with '42' pattern."
                )

            self.grid[ty][tx].is_42 = True
            self.grid[ty][tx].visited = True
            self.grid[ty][tx].walls = 15

    def dfs_generate(self, animate: bool = False, delay: float = 0.02) -> None:
        """DFS maze generation from a valid random point."""
        start_x = random.randint(0, self.config.width - 1)
        start_y = random.randint(0, self.config.height - 1)

        while self.grid[start_y][start_x].is_42:
            start_x = random.randint(0, self.config.width - 1)
            start_y = random.randint(0, self.config.height - 1)

        self._make_maze_dfs(start_x, start_y, animate, delay)

        if not self.config.perfect:
            self._create_imperfect_loops()

    def _make_maze_dfs(
        self, x: int, y: int, animate: bool, delay: float
    ) -> None:
        """Recursive DFS algorithm to carve paths."""
        self.grid[y][x].visited = True

        if animate:
            self.render_terminal()
            time.sleep(delay)

        options = [
            (0, -1, Cell.NORTH, Cell.SOUTH),
            (1, 0, Cell.EAST, Cell.WEST),
            (0, 1, Cell.SOUTH, Cell.NORTH),
            (-1, 0, Cell.WEST, Cell.EAST)
        ]

        random.shuffle(options)

        for dx, dy, dir_out, dir_in in options:
            tx = x + dx
            ty = y + dy

            if 0 <= tx < self.config.width and 0 <= ty < self.config.height:
                if not self.grid[ty][tx].visited:
                    self.grid[y][x].remove_wall(dir_out)
                    self.grid[ty][tx].remove_wall(dir_in)
                    self._make_maze_dfs(tx, ty, animate, delay)

    def get_maze_hex_string(self) -> str:
        """Converts maze walls into required hexadecimal format."""
        output: str = ""
        for y in range(self.config.height):
            for x in range(self.config.width):
                output += f"{self.grid[y][x].walls:X}"
            output += "\n"
        return output

    def prims_generate(
        self, animate: bool = False, delay: float = 0.02
    ) -> None:
        """Randomized Prim's maze generation algorithm."""
        start_x: int = random.randint(0, self.config.width - 1)
        start_y: int = random.randint(0, self.config.height - 1)
        while self.grid[start_y][start_x].is_42:
            start_x = random.randint(0, self.config.width - 1)
            start_y = random.randint(0, self.config.height - 1)

        self.grid[start_y][start_x].visited = True
        frontier: list[tuple[int, int]] = []

        def add_frontier(x: int, y: int) -> None:
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                tx, ty = x + dx, y + dy
                if (0 <= tx < self.config.width
                        and 0 <= ty < self.config.height):
                    if (not self.grid[ty][tx].visited
                            and (tx, ty) not in frontier):
                        frontier.append((tx, ty))

        add_frontier(start_x, start_y)

        while frontier:
            idx: int = random.randint(0, len(frontier) - 1)
            tx, ty = frontier.pop(idx)

            self.grid[ty][tx].visited = True

            in_maze_neighbors = []
            options: list[tuple[int, int, int, int]] = [
                (0, -1, Cell.NORTH, Cell.SOUTH),
                (1, 0, Cell.EAST, Cell.WEST),
                (0, 1, Cell.SOUTH, Cell.NORTH),
                (-1, 0, Cell.WEST, Cell.EAST)
            ]

            for dx, dy, dir_out, dir_in in options:
                nx, ny = tx + dx, ty + dy
                if (0 <= nx < self.config.width
                        and 0 <= ny < self.config.height):
                    if (self.grid[ny][nx].visited
                            and not self.grid[ny][nx].is_42):
                        in_maze_neighbors.append((nx, ny, dir_out, dir_in))

            if in_maze_neighbors:
                nx, ny, dir_out, dir_in = random.choice(in_maze_neighbors)
                self.grid[ty][tx].remove_wall(dir_out)
                self.grid[ny][nx].remove_wall(dir_in)

                if animate:
                    self.render_terminal()
                    time.sleep(delay)

            add_frontier(tx, ty)

        if not self.config.perfect:
            self._create_imperfect_loops()

    def _create_imperfect_loops(self) -> None:
        """Makes imperfect 'Braid Mazes' with looped dead-ends."""
        for y in range(self.config.height):
            for x in range(self.config.width):
                cell = self.grid[y][x]

                if cell.is_42:
                    continue

                closed_walls = sum([
                    cell.has_wall(Cell.NORTH),
                    cell.has_wall(Cell.EAST),
                    cell.has_wall(Cell.SOUTH),
                    cell.has_wall(Cell.WEST)
                ])

                if closed_walls == 3:
                    if random.random() < 0.50:
                        options = []
                        if y > 0 and cell.has_wall(Cell.NORTH):
                            options.append((0, -1, Cell.NORTH, Cell.SOUTH))
                        if (x < self.config.width - 1
                                and cell.has_wall(Cell.EAST)):
                            options.append((1, 0, Cell.EAST, Cell.WEST))
                        if (y < self.config.height - 1
                                and cell.has_wall(Cell.SOUTH)):
                            options.append((0, 1, Cell.SOUTH, Cell.NORTH))
                        if x > 0 and cell.has_wall(Cell.WEST):
                            options.append((-1, 0, Cell.WEST, Cell.EAST))

                        random.shuffle(options)

                        for dx, dy, dir_out, dir_in in options:
                            tx, ty = x + dx, y + dy
                            if not self.grid[ty][tx].is_42:
                                cell.remove_wall(dir_out)
                                self.grid[ty][tx].remove_wall(dir_in)
                                break

    def solve_shortest_path_bfs(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> str:
        """Finds the absolute shortest path (BFS)."""
        visited: set[tuple[int, int]] = set()
        visited.add((start_x, start_y))

        queue: list[tuple[int, int, str]] = [(start_x, start_y, "")]

        while queue:
            x, y, current_path = queue.pop(0)

            if x == end_x and y == end_y:
                return current_path

            moves = [
                (0, -1, Cell.NORTH, "N"),
                (1, 0, Cell.EAST, "E"),
                (0, 1, Cell.SOUTH, "S"),
                (-1, 0, Cell.WEST, "W")
            ]

            for dx, dy, wall_mask, dir_str in moves:
                if not self.grid[y][x].has_wall(wall_mask):
                    tx = x + dx
                    ty = y + dy

                    if (tx, ty) not in visited:
                        visited.add((tx, ty))
                        queue.append((tx, ty, current_path + dir_str))

        return ""

    def solve_path_dfs(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> str:
        """Finds a valid path by Depth-First Search (DFS)."""
        visited: set[tuple[int, int]] = set()
        visited.add((start_x, start_y))

        stack: list[tuple[int, int, str]] = [(start_x, start_y, "")]

        while stack:
            x, y, current_path = stack.pop(-1)

            if x == end_x and y == end_y:
                return current_path

            moves = [
                (0, -1, Cell.NORTH, "N"),
                (1, 0, Cell.EAST, "E"),
                (0, 1, Cell.SOUTH, "S"),
                (-1, 0, Cell.WEST, "W")
            ]

            random.shuffle(moves)

            for dx, dy, wall_mask, dir_str in moves:
                if not self.grid[y][x].has_wall(wall_mask):
                    tx, ty = x + dx, y + dy
                    if (tx, ty) not in visited:
                        visited.add((tx, ty))
                        stack.append((tx, ty, current_path + dir_str))
        return ""

    def save_maze_to_file(self) -> None:
        """Saves maze to output file as required."""
        try:
            with open(self.config.output_file, 'w') as f:
                f.write(self.get_maze_hex_string().strip() + '\n')
                f.write('\n')

                ex, ey = self.config.entry
                f.write(f"{ex}, {ey}\n")

                xx, xy = self.config.exit
                f.write(f"{xx}, {xy}\n")

                solution_path = self.solve_shortest_path_bfs(ex, ey, xx, xy)
                f.write(f"{solution_path}\n")

        except PermissionError:
            raise PermissionError(
                "Permission denied: "
                f"Cannot write to {self.config.output_file}"
            )

    def _get_path_coords(
        self, start_x: int, start_y: int, path_str: str
    ) -> set[tuple[int, int]]:
        """Converts directional string ('NESW') into coords (X, Y)."""
        coords: set[tuple[int, int]] = set()
        cx, cy = start_x, start_y
        for move in path_str:
            if move == 'N':
                cy -= 1
            elif move == 'S':
                cy += 1
            elif move == 'E':
                cx += 1
            elif move == 'W':
                cx -= 1
            coords.add((cx, cy))
        return coords

    def render_terminal(
        self,
        player_pos: tuple[int, int] | None = None,
        solution_mode: int = 0,
        wall_color: str = colors.WHITE
    ) -> None:
        """Renders the maze. 0=Off, 1=BFS Shortest, 2=DFS Winding."""
        os.system('clear' if os.name == 'posix' else 'cls')

        px, py = player_pos if player_pos else self.config.entry

        solution_coords: set[tuple[int, int]] = set()
        ex, ey = self.config.exit

        if solution_mode == 1:
            path_str = self.solve_shortest_path_bfs(px, py, ex, ey)
            solution_coords = self._get_path_coords(px, py, path_str)
        elif solution_mode == 2:
            path_str = self.solve_path_dfs(px, py, ex, ey)
            solution_coords = self._get_path_coords(px, py, path_str)

        for y in range(self.config.height):
            line1 = ""
            line2 = ""
            for x in range(self.config.width):
                cell: Cell = self.grid[y][x]

                center: str = "   "
                if (x, y) == (px, py):
                    center = f"{colors.GREEN}🚗 {wall_color}"
                elif (x, y) == self.config.exit:
                    center = f"{colors.RED} E {wall_color}"
                elif (x, y) == self.config.entry:
                    center = f"{colors.BLUE} S {wall_color}"
                elif (x, y) in solution_coords:
                    center = f"{colors.YELLOW} ● {wall_color}"
                elif cell.is_42:
                    center = f"{colors.MAGENTA}███{wall_color}"  # 42!

                if cell.has_wall(Cell.NORTH):
                    line1 += "█████"
                else:
                    line1 += "█   █"

                left = "█" if cell.has_wall(Cell.WEST) else " "
                right = "█" if cell.has_wall(Cell.EAST) else " "

                if cell.walls == 15 and not cell.is_42:
                    line2 += "█████"
                else:
                    line2 += f"{left}{center}{right}"

            print(f"{wall_color}{line1}{colors.RESET}")
            print(f"{wall_color}{line2}{colors.RESET}")

        print(
            f"{wall_color}" + "█████" * self.config.width + f"{colors.RESET}"
        )
