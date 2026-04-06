This project has been created as part of the 42 curriculum by `dporhomo` and `amanukho`

## Description
A highly robust, terminal-based Maze Generator and Solver operating entirely through a Command Line Interface (CLI). This project generates complex mazes, embeds a mandatory "42" structure in the center, and outputs the results in a strict hexadecimal format. It features multiple generation algorithms, dynamic visual terminal animations, and a fully interactive "Play Mode."

### Project Goals:
The primary objective of this project is to explore and implement fundamental data structures and graph theory algorithms in Python. Specifically, it targets the following core priorities:
1. **Algorithmic Proficiency:** Generating profoundly contrasting maze topologies by implementing and comparing distinct generation algorithms (Randomized Depth-First Search vs. Prim's Algorithm).
2. **Dynamic Pathfinding & Simulation:** Demonstrating real-time maze-solving algorithms (BFS and DFS) that calculate and render dynamic solution paths based on the user's active coordinates within the interactive simulation.
3. **Data Export & Interoperability:** Exporting the generated maze structures, specific coordinates, and calculated solutions into a strict, machine-readable text format (hexadecimal) for downstream processing, automated validation, and analysis.
4. **Robustness & Professional Packaging:** Ensuring application stability through strict type-checking (`pydantic`) and transitioning the codebase into a fully distributable, pip-installable Python package conforming to industry standards.

---

## Instructions: Running from Source
**To run the interactive program from the source code:**
Ensure you have `make` installed. The Makefile will automatically handle the creation of the Python virtual environment and the installation of dependencies.

1. Clone the repository and navigate into the folder.
2. Run `make run` to instantly build the environment, install the package, and launch the interactive menu.

**Other Makefile Commands:**
* `make build`: Packages the project into `.whl` and `.tar.gz` formats for distribution.
* `make test`: Runs the automated testing suite.
* `make lint`: Runs static type checking (`mypy`) and linting (`flake8`).
* `make clean` / `make fclean`: Removes cache, build artifacts, and the virtual environment.

---

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

## Technical Choices & Algorithms
We chose to implement two highly distinct generation algorithms to provide visual variety:
1. **Randomized Depth-First Search (DFS):** Chosen because it creates beautiful, winding, "river-like" paths with long corridors.
2. **Randomized Prim's Algorithm:** Chosen because it radiates outward, creating a "spiky," crystalline structure with many short dead ends.

To handle `PERFECT=False`, we implemented a **Braid Maze Algorithm**. Instead of randomly smashing walls, the algorithm identifies "Dead Ends" (cells with 3 walls) and selectively knocks down one wall to connect it to an adjacent path. This mathematically ensures multiple loops while preserving the visual integrity of the corridors (ensuring corridors are never wider than 2 cells).

---

## Team & Project Management
* **`dporhomo`:** Core architecture, algorithm implementation (DFS/Prim's/Braid), packaging (`setup.py` / `Makefile`), and interactive CLI development.
* **`amanukho`:** Testing, QA validation, edge-case generation, and ensuring strict compliance with the 42 subject output requirements.

**What Went Well:**
The project was completed in full scope with all bonuses achieved. We are incredibly proud of the "Play Mode," which allows the user to navigate a "🚗" through the maze using W,A,S,D keys. We also implemented a dynamic hint system that calculates the BFS path directly from the user's current coordinates, simulating a real-world GPS application.

**What Could Be Improved:**
We initially anticipated completing the MiniLibX (MLX) graphical bonus. While the library was easily installed via the provided `.whl`, we encountered severe X11 rendering issues on Linux where the window remained completely black despite successful execution. Rather than getting blocked by hardware/driver issues, we pivoted our strategy and successfully implemented real-time **Terminal Animation** during generation to satisfy the animation bonus requirement cross-platform.

---

## Resources & Tools Used
* Python 3 Standard Library (`sys`, `os`, `tty`, `termios`)
* `pydantic` (For robust configuration validation and edge-case handling)
* `pytest` & `unittest` (For automated testing)
* `mypy` & `flake8` (For strict static type checking and formatting)
* `build` & `setuptools` (For generating `.whl` and `.tar.gz` distributions)
```
