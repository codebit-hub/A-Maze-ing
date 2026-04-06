# tests/test_maze.py
import unittest
import os
from mazegen.config import MazeConfig
from mazegen.generator import MazeGenerator


class TestMazeGenerator(unittest.TestCase):

    def setUp(self) -> None:
        """Create a temporary valid config file for testing."""
        self.test_file: str = "test_temp_config.txt"
        with open(self.test_file, "w") as f:
            f.write(
                "WIDTH=20\n"
                "HEIGHT=10\n"
                "ENTRY=0,0\n"
                "EXIT=19,9\n"
                "PERFECT=True\n"
            )

    def tearDown(self) -> None:
        """Clean up the temporary file after tests run."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_valid_config_parsing(self) -> None:
        """Test that Pydantic correctly parses valid configuration."""
        config = MazeConfig(self.test_file)
        self.assertEqual(config.width, 20)
        self.assertEqual(config.height, 10)
        self.assertEqual(config.entry, (0, 0))
        self.assertTrue(config.perfect)

    def test_grid_initialization(self) -> None:
        """Test that the generator builds the correct grid dimensions."""
        maze = MazeGenerator(self.test_file)
        # Check height (rows)
        self.assertEqual(len(maze.grid), 10)
        # Check width (columns)
        self.assertEqual(len(maze.grid[0]), 20)

    def test_missing_file_error(self) -> None:
        """Test that a missing file raises a FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            MazeConfig("does_not_exist.txt")


if __name__ == '__main__':
    unittest.main()
