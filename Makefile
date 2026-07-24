# Windows

# Delete later
# $(PYTHON) maze_analyzer.py maze.txt

PYTHON = python
# PYTHON = python3
SRC = a_maze_ing.py
CONFIG = default_config.txt

FLAKE8 = flake8 .
MYPY = mypy . --warn-return-any \
--warn-unused-ignores \
--ignore-missing-imports \
--disallow-untyped-defs \
--check-untyped-defs
MYPY_STRICT = mypy . --strict
CACHE = __pycache__ .mypy_cache

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(SRC) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(SRC) $(CONFIG)

clean:
	rm -rf $(CACHE)
	# rmdir /s /q __pycache__
	# rmdir /s /q .mypy_cache

lint:
	$(FLAKE8)
	$(MYPY)

lint-strict:
	$(FLAKE8)
	$(MYPY_STRICT)

# DEBUG
run2:
	$(PYTHON) $(SRC) $(CONFIG) --print-debug
	$(PYTHON) maze_analyzer.py --max-dead-ends 0 maze.txt
# DEBUG END