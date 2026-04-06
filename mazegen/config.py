from typing import Any
from pydantic import BaseModel, Field, ValidationError


class MazeSettings(BaseModel):
    """Pydantic model that automatically validates our configuration data."""
    width: int = Field(
        ..., ge=17, le=35, description="Maze width between 17 and 35"
    )
    height: int = Field(
        ..., ge=7, le=12, description="Maze height between 7 and 12"
    )
    entry: tuple[int, int]
    exit: tuple[int, int]

    output_file: str = Field(default="maze_output.txt", min_length=1)
    perfect: bool = Field(default=True)
    seed: int | None = Field(default=None)


class MazeConfig:
    """Parses the text file and passes the raw data to Pydantic."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        raw_data = self._read_file(filepath)

        try:
            self.settings = MazeSettings(**raw_data)

        except ValidationError as e:
            custom_errors = []
            for err in e.errors():
                field_name = str(err.get("loc", ["UNKNOWN"])[0]).upper()
                err_type = err.get("type")

                if err_type == "missing":
                    custom_errors.append(
                        f"[!] Missing Required Settings: '{field_name}'. "
                        f"Please add {field_name}=... to your file."
                    )
                elif err_type in ["type_error.integer", "int_parsing"]:
                    custom_errors.append(
                        f"[!] Invalid Value: '{field_name}' must be "
                        "a whole number."
                    )
                elif err_type in ["greater_than_equal", "less_than_equal"]:
                    if field_name == "WIDTH":
                        custom_errors.append(
                            f"[!] Out of Bounds: '{field_name}' must be "
                            "between 17 and 35."
                        )
                    if field_name == "HEIGHT":
                        custom_errors.append(
                            f"[!] Out of Bounds: '{field_name}' must be "
                            "between 7 and 12."
                        )
                elif err_type == "string_too_short":
                    custom_errors.append(
                        f"[!] Invalid Value: '{field_name}' "
                        "cannot be empty. Provide a file name "
                        "(e.g. OUTPUT_FILE=maze.txt)"
                    )
                elif err_type in ["tuple_type", "type_error.tuple"]:
                    custom_errors.append(
                        f"[!] Invalid Format: '{field_name}' must be "
                        f"formatted as x,y (e.g., {field_name}=0,0)."
                    )
                elif err_type in ["bool_type", "type_error.bool",
                                  "bool_parsing"]:
                    custom_errors.append(
                        f"[!] Invalid Value: '{field_name}' must be "
                        "True or False."
                    )
                else:
                    custom_errors.append(
                        f"[!] Issue with '{field_name}': {err.get('msg')}"
                    )

            error_str = "\n".join(custom_errors)
            raise ValueError(
                f"Validation Failed in '{filepath}':\n{error_str}"
            )

        self._logical_checks()

        self.width = self.settings.width
        self.height = self.settings.height
        self.entry = self.settings.entry
        self.exit = self.settings.exit
        self.output_file = self.settings.output_file
        self.perfect = self.settings.perfect
        self.seed = self.settings.seed

    def _logical_checks(self) -> None:
        """Custom checks that Pydantic can't do natively."""
        if self.settings.entry == self.settings.exit:
            raise ValueError("Entry and Exit coordinates cannot be identical.")

        ex, ey = self.settings.entry
        if not (0 <= ex < self.settings.width
                and 0 <= ey < self.settings.height):
            raise ValueError(f"Entry {self.settings.entry} is out of bounds.")

        xx, xy = self.settings.exit
        if not (0 <= xx < self.settings.width
                and 0 <= xy < self.settings.height):
            raise ValueError(f"Exit {self.settings.exit} is out of bounds.")

    def _read_file(self, filepath: str) -> dict[str, Any]:
        """Reads KEY=VALUE file and converts it into a Python dict."""
        data: dict[str, Any] = {}
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

                    if not value:
                        data[key.lower()] = ""
                        continue

                    if key in ["ENTRY", "EXIT"]:
                        coords = value.split(',')
                        if len(coords) == 2:
                            try:
                                data[key.lower()] = (
                                    int(coords[0]), int(coords[1])
                                )
                            except ValueError:
                                data[key.lower()] = value
                        else:
                            data[key.lower()] = value
                    else:
                        data[key.lower()] = value
            return data

        except FileNotFoundError:
            raise FileNotFoundError(
                f"CRITICAL: Config file '{filepath}' is missing!"
            )
