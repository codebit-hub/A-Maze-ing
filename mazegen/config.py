class MazeConfig:
    """Parses and stores the maze configuration from a text file."""

    def __init__(self, filepath: str) -> None:
        self.width: int = 0
        self.height: int = 0
        self.entry: tuple[int, int] = (0, 0)
        self.exit: tuple[int, int] = (0, 0)
        self.output_file: str = "maze.txt"
        self.perfect: bool = True
        self.seed: int | None = None

        self._parse_file(filepath)
        self._validate()

    def _parse_file(self, filepath: str) -> None:
        """Reads the config file and extracts KEY=VALUE pairs."""
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if '=' not in line:
                        raise ValueError(f"Invalid line format: {line}")

                    # string.split(separator, maxsplit - how many splits to perform)
                    key, value = line.split('=', 1)
                    key = key.strip().upper()
                    value = value.strip()

                    self._assign_value(key, value)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{filepath}' not found.")

    def _assign_value(self, key: str, value: str) -> None:
        """Assigns parsed string values to the correct typed attributes."""
        if key == "WIDTH":
            self.width = int(value)
        elif key == "HEIGHT":
            self.height = int(value)
        elif key == "ENTRY":
            coords: str = value.split(',')
            self.entry = (int(coords[0]), int(coords[1]))
        elif key == "EXIT":
            coords: str = value.split(',')
            self.exit = (int(coords[0]), int(coords[1]))
        elif key == "OUTPUT_FILE":
            self.output_file = value
        elif key == "PERFECT":
            self.perfect = value.lower() == "true"
        elif key == "SEED":
            self.seed = int(value)
        else:
            raise ValueError(f"Unknown configuration key: {key}")

    def _validate(self) -> None:
        """Ensures the parsed data makes logical sense."""
        if self.width < 5 or self.height < 5:
            raise ValueError("Maze dimensions must be at least 5x5 to fit the '42' pattern.")
        if self.entry == self.exit:
            raise ValueError("Entry and Exit coordinates cannot be the same.")
        if not (0 <= self.entry[0] < self.width and 0 <= self.entry[1] < self.height):
            raise ValueError("Entry coordinates are out of bounds.")
        if not (0 <= self.exit[0] < self.width and 0 <= self.exit[1] < self.height):
            raise ValueError("Exit coordinates are out of bounds.")
