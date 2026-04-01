# Variables
PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt

.PHONY: install run debug clean lint lint-strict build

install:
	# Upgrades pip and
	# installs the local mazegen package
	# along with build tools
	$(PYTHON) -m pip install --upgrade pip build wheel flake8 mypy
	$(PYTHON) -m pip install -e .

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	# Removes python cache files and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ mazegen.egg-info/

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build: clean
	# Builds the .whl and .tar.gz files required by the subject
	$(PYTHON) -m build