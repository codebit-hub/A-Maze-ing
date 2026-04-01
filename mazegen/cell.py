class Cell:
    """Represents a single square in the maze."""

    # Class constants represent walls instead of bitmasks
    NORTH: int = 1  # 0001
    EAST: int  = 2  # 0010
    SOUTH: int = 4  # 0100
    WEST: int  = 8  # 1000

    def __init__(self, x: int, y: int) -> None:
        """Initializes a cell at given coordinates with all walls closed."""
        self.x: int = x
        self.y: int = y
        self.walls: int = 15          # 1111 in binary (all walls up)
        self.visited: bool = False    # Used by generation algorithms
        self.is_42: bool = False      # Used to draw 42 logo

    def remove_wall(self, direction: int) -> None:
        """Removes a specific wall using bitwise AND NOT."""
        #   1111  (Current walls: 15)
        # & 1011  (Mask: ~4) ~ sets the value opposite of 0100
        #   1011  (Result: 11)
        self.walls &= ~direction

    def has_wall(self, direction: int) -> bool:
        """Returns True if the specified wall is currently closed."""
        #   1011  (Cell walls)
        # & 0100  (Checking for South)
        #   0000  (Result is 0) False
        # & 0001  (Checking for North)
        #   0001  (Result is 1) True
        return bool(self.walls & direction)