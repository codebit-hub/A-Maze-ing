# mazegen/config.py
from pydantic import BaseModel, Field, ValidationError

class MazeSettings(BaseModel):
    """Pydantic model that automatically validates our configuration data."""
    # Enforce strict terminal limits: minimum 5x5 (for the 42 logo), maximum 100x100
    width: int = Field(..., ge=10, le=100, description="Maze width between 10 and 100")
    height: int = Field(..., ge=10, le=100, description="Maze height between 10 and 100")

    entry: tuple[int, int]
    exit: tuple[int, int]

    # Provide safe defaults if the user forgets to include these in the text file!
    output_file: str = Field(default="maze_output.txt")
    perfect: bool = Field(default=True)
    seed: int | None = Field(default=None)

class MazeConfig:
    """Parses the text file and passes the raw data to Pydantic for validation."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        raw_data = self._read_file(filepath)

        try:
            # Pydantic takes the raw dictionary and automatically validates everything!
            self.settings = MazeSettings(**raw_data)
        except ValidationError as e:
            # If Pydantic catches an error (e.g. WIDTH=900), it formats a beautiful error message
            raise ValueError(f"Configuration Validation Failed in '{filepath}':\n{e}")

        self._logical_checks()

        # Flatten the validated settings so generator.py doesn't have to change its syntax
        self.width = self.settings.width
        self.height = self.settings.height
        self.entry = self.settings.entry
        self.exit = self.settings.exit
        self.output_file = self.settings.output_file
        self.perfect = self.settings.perfect
        self.seed = self.settings.seed

    def _read_file(self, filepath: str) -> dict:
        """Reads the KEY=VALUE text file and converts it into a Python dictionary."""
        data = {}
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if '=' not in line:
                        raise ValueError(f"Invalid line format: {line}")

                    key, value = line.split('=', 1)
                    key = key.strip().upper()
                    value = value.strip()

                    # Pre-process coordinates from "0,0" to a tuple (0, 0)
                    if key in ["ENTRY", "EXIT"]:
                        coords = value.split(',')
                        if len(coords) != 2:
                            raise ValueError(f"{key} must have exactly two numbers (x,y)")
                        data[key.lower()] = (int(coords[0]), int(coords[1]))
                    else:
                        data[key.lower()] = value
            return data

        except FileNotFoundError:
            raise FileNotFoundError(f"CRITICAL: Configuration file '{filepath}' is completely missing!")

    def _logical_checks(self) -> None:
        """Custom checks that Pydantic can't do natively (like comparing two fields)."""
        if self.settings.entry == self.settings.exit:
            raise ValueError("Entry and Exit coordinates cannot be the exact same spot.")

        ex, ey = self.settings.entry
        if not (0 <= ex < self.settings.width and 0 <= ey < self.settings.height):
            raise ValueError(f"Entry {self.settings.entry} is outside the maze bounds.")

        xx, xy = self.settings.exit
        if not (0 <= xx < self.settings.width and 0 <= xy < self.settings.height):
            raise ValueError(f"Exit {self.settings.exit} is outside the maze bounds.")
