# Variables
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
MYPY = $(VENV)/bin/mypy
FLAKE8 = $(VENV)/bin/flake8
PYTEST = $(VENV)/bin/pytest
STAMP = $(VENV)/.installed

all: install

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

$(STAMP): $(VENV)/bin/activate pyproject.toml
	$(PIP) install --upgrade pip build wheel pydantic flake8 \
	mypy pytest types-setuptools
	$(PIP) install -e .
	touch $(STAMP)

install: $(STAMP)

run: install
	$(PYTHON) a_maze_ing.py config.txt

build: install
	$(PYTHON) -m build --sdist --wheel --outdir .
	@echo "\n[+] Package built! Files are in the root directory."

debug: install
	$(PYTHON) -m pdb a_maze_ing.py config.txt

lint: install
	$(FLAKE8) . --exclude $(VENV),build,dist,.pytest_cache
	$(MYPY) . --exclude $(VENV) \
	--explicit-package-bases \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict: install
	$(FLAKE8) . --exclude $(VENV),build,dist,.pytest_cache
	$(MYPY) . --exclude $(VENV) --explicit-package-bases --strict

test: install
	PYTHONPATH=. $(PYTEST) tests/

clean:
	rm -rf __pycache__ mazegen/__pycache__ tests/__pycache__
	rm -rf *.egg-info build dist .mypy_cache .pytest_cache
	rm -f maze_output.txt
	rm -f mazegen-*.whl mazegen-*.tar.gz

fclean: clean
	rm -rf $(VENV)

re: fclean all

.PHONY: all install run build debug lint lint-strict test clean fclean re
