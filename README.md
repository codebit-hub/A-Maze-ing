*This project has been created as part of the 42 curriculum by dporhomo, amanukho.*

## Description
A highly robust, terminal-based Maze Generator and Solver operating entirely through a Command Line Interface (CLI). This project generates complex mazes, embeds a mandatory "42" structure in the center, and outputs the results in a strict hexadecimal format. It features multiple generation algorithms, dynamic visual terminal animations, and a fully interactive "Play Mode."

### Project Goals:
The primary objective of this project is to explore and implement fundamental data structures and graph theory algorithms in Python. Specifically, it targets the following core priorities:
1. **Algorithmic Proficiency:** Generating profoundly contrasting maze topologies by implementing and comparing distinct generation algorithms (Randomized Depth-First Search vs. Prim's Algorithm).
2. **Dynamic Pathfinding & Simulation:** Demonstrating real-time maze-solving algorithms (BFS and DFS) that calculate and render dynamic solution paths based on the user's active coordinates within the interactive simulation.
3. **Data Export & Interoperability:** Exporting the generated maze structures, specific coordinates, and calculated solutions into a strict, machine-readable text format (hexadecimal) for downstream processing, automated validation, and analysis.
4. **Robustness & Professional Packaging:** Ensuring application stability through strict type-checking (`pydantic`) and transitioning the codebase into a fully distributable, pip-installable Python package conforming to industry standards.

---

## Advanced Features
* **Multiple Generation Algorithms:** Generates mazes using Randomized Depth-First Search (DFS) or Randomized Prim's Algorithm.
* **Dynamic Pathfinding:** Solves mazes using Breadth-First Search (BFS) for the absolute shortest path or DFS for a winding solution path.
* **Display Options & Play Mode:** Interactive terminal rendering allows users to navigate the maze manually using `W, A, S, D` controls. Includes a real-time hint system that actively recalculates the solution path from the user's current coordinates to the exit on every step.
* **Braid Mazes:** Generates "Imperfect" mazes containing loops and disconnected walls to eliminate dead ends.

---

## Technical Choices & Algorithms

### Maze Generation Algorithms & Rationale
We chose to implement two highly distinct generation algorithms to provide mathematical and visual variety:
1. **Randomized Depth-First Search (DFS):** Chosen because it creates beautiful, winding, "river-like" paths with long corridors and a high "routing" factor, making it ideal for a confusing visual maze.
2. **Randomized Prim's Algorithm:** Chosen because it radiates outward from the center, creating a "spiky," crystalline structure with many short, immediate dead ends, contrasting perfectly with the layout of DFS.

To handle `PERFECT=False`, we implemented a **Braid Maze Algorithm**. Instead of randomly smashing walls (which breaks grid integrity), our algorithm identifies "Dead Ends" (cells with exactly 3 walls) and selectively knocks down one wall to connect it to an adjacent, valid path. This mathematically guarantees multiple loops while ensuring corridors are never visually wider than 2 cells.

### Configuration File Structure
The program strictly relies on a text-based configuration file (e.g., `config.txt`) structured as `KEY=VALUE` pairs. Each line is strictly validated by Pydantic.
**Format & Constraints:**
* `WIDTH`: (Required) Integer between 17 and 35. Enforced to fit safely within standard terminal window sizes without line-wrapping.
* `HEIGHT`: (Required) Integer between 7 and 12.
* `ENTRY`: (Required) Coordinates formatted exactly as `x,y` (e.g., `0,0`). Cannot overlap with the "42" logo or the exit.
* `EXIT`: (Required) Coordinates formatted exactly as `x,y`.
* `OUTPUT_FILE`: (Optional) String representing the output filename. Defaults to `maze_output.txt`. Cannot be empty.
* `PERFECT`: (Optional) Boolean (`True` or `False`). Defaults to `True`.
* `SEED`: (Optional) Integer for reproducible maze generation. Defaults to a random integer.

### Code Reusability
The core maze logic has been fully decoupled from the Command Line Interface (CLI) and packaged as a standalone, pip-installable Python module named `mazegen`.
The `MazeGenerator` class (inside `mazegen/generator.py`) is entirely reusable. It can be imported into any future Python project to instantly configure, generate, solve, and export mazes programmatically without relying on the terminal user interface.

---

## Team & Project Management

**Roles:**
* **`dporhomo`:** Core architecture, algorithm implementation (DFS/Prim's/Braid), packaging (`setup.py` / `Makefile`), and interactive CLI development.
* **`amanukho`:** Testing, QA validation, edge-case generation, and ensuring strict compliance with the 42 subject output requirements.

**Planning & Evolution:**
Our anticipated plan was to construct the core data structures first, implement DFS, integrate the MiniLibX (MLX) graphical library for rendering, and finally package the project. However, this evolved significantly during development. While we successfully built the algorithmic backend, we encountered severe X11 rendering issues on Linux with MLX (the application executed successfully, but the window remained completely black).
Rather than stalling the project on hardware and driver issues, we pivoted our planning. We transitioned entirely to an advanced Terminal Rendering engine and built an interactive CLI "Play Mode" to satisfy the animation and visual UI bonuses cross-platform.

**What Worked Well & What Could Be Improved:**
The modularity of the `MazeGenerator` class worked incredibly well, allowing us to seamlessly swap between DFS and Prim's algorithms without rewriting rendering logic. The pivot to the terminal "Play Mode" with dynamic BFS hints was a major success and highly engaging.
What could be improved is our initial time allocation for the MLX library. Dedicating less time to troubleshooting upstream C-library graphics issues would have allowed us to implement even more maze algorithms (like Kruskal's or the Aldous-Broder algorithm).

**Specific Tools Used:**
* **`pydantic`**: For robust, strictly-typed configuration validation and edge-case handling.
* **`pytest` & `unittest`**: For building the automated testing suite.
* **`mypy` & `flake8`**: For enforcing strict PEP-8 styling and static type safety.
* **`build` & `setuptools`**: For generating the standard `.whl` and `.tar.gz` distributions.
* **`make`**: For automating environment setup, linting, testing, and execution.

---

## Resources
* [Wikipedia: Maze generation algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
* [Python 3 Official Documentation](https://docs.python.org/3/) (Specific utilization of `termios`, `tty`, and `sys` modules).

**AI Usage:**
Artificial Intelligence (LLMs) was utilized strictly as a pair-programming and debugging assistant to ensure industry-standard compliance. Specifically, AI was used to:
* Troubleshoot and resolve strict static typing (`mypy`) import errors and module pathing edge cases.
* Optimize `Makefile` configurations (e.g., resolving relinking issues, target dependencies, and `pytest` pathing).
* Assist in translating default `pydantic` validation exceptions into user-friendly, customized terminal error messages.

---

## Instructions

### Running from Source
**To run the interactive program from the source code:**
Ensure you have `make` installed. The Makefile will automatically handle the creation of the Python virtual environment and the installation of all dependencies.

1. Clone the repository and navigate into the folder.
2. Run `make run` to instantly build the environment, install the package, and launch the interactive menu.

### Makefile Commands
The project includes a `Makefile` to automate all tasks within an isolated virtual environment (`venv`):
* `make all` / `make install`: Sets up the virtual environment, upgrades pip, and installs all required dependencies and the package itself.
* `make run`: Ensures dependencies are installed and executes the main interactive script (`a_maze_ing.py config.txt`).
* `make build`: Packages the `mazegen` project into `.whl` and `.tar.gz` distribution formats and outputs them to the root directory.
* `make debug`: Runs the main script using Python's built-in interactive debugger (`pdb`).
* `make lint`: Executes `flake8` for PEP-8 compliance and `mypy` for static type checking (configured to ignore missing third-party stubs).
* `make lint-strict`: Executes `flake8` and `mypy` with aggressive `--strict` type-checking enabled.
* `make test`: Runs the automated testing suite using `pytest` against the `tests/` directory.
* `make clean`: Removes all cache directories (`__pycache__`), build artifacts (`build/`, `dist/`), and output text files.
* `make fclean`: Executes `clean` and completely deletes the virtual environment (`venv/`).
* `make re`: Executes `fclean` followed by `all` to rebuild the environment from scratch.

## Using the `mazegen` Package in Your Projects
The maze generation logic has been fully decoupled from the command line interface (CLI) and packaged as a standalone, pip-installable module.

If you are an evaluator or a user wanting to test the `.whl` package from scratch, follow these exact steps:

### Step 1: Setup a Fresh Workspace
Create an empty folder, set up a Python virtual environment, and activate it:
```bash
mkdir test_maze_pkg
cd test_maze_pkg
python3 -m venv venv_test
source venv_test/bin/activate
```

### Step 2: Install the Package
Copy the `mazegen-1.0.0-py3-none-any.whl` file from the main repository into this new folder. Then, install it using pip:
```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Step 3: Create the Configuration File
The `MazeGenerator` uses `pydantic` to strictly enforce configuration parameters. Create a file named `config.txt` in your folder:
```bash
touch config.txt
```
Open `config.txt` and paste the following parameters (ensure there are no spaces around the comma in the coordinates):
```text
WIDTH=15
HEIGHT=15
ENTRY=0,0
EXIT=14,14
PERFECT=True
SEED=42
```

### Step 4: Create Your Python Script
Create a Python file to instantiate the generator, access the raw data structure, and solve the maze:
```bash
touch main.py
```
Open `main.py` and paste the following code:
```python
from mazegen.generator import MazeGenerator

# 1. Instantiate the generator (loads parameters from your config file)
maze = MazeGenerator("config.txt")

# 2. Generate the maze using your preferred algorithm
maze.dfs_generate()

# 3. Access the generated structure
# The grid is a 2D list of `Cell` objects accessible via maze.grid[y][x].
# Let's check the walls of the Entrance cell (0, 0):
entrance_cell = maze.grid[0][0]
print(f"Entrance Cell raw wall integer: {entrance_cell.walls}")

# 4. Access a generated solution path
ex, ey = maze.config.entry
xx, xy = maze.config.exit
shortest_path = maze.solve_shortest_path_bfs(ex, ey, xx, xy)

print(f"To solve the maze, follow this path: {shortest_path}")
```

### Step 5: Execute!
Run your script:
```bash
python3 main.py
```

---
