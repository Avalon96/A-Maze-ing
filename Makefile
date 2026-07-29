PYTHON = python3
ifeq ($(OS),Windows_NT)
	PYTHON = python
endif

SRC = a_maze_ing.py
CONFIG = default_config.txt

FLAKE8 = flake8 .
MYPY = mypy . --warn-return-any \
--warn-unused-ignores \
--ignore-missing-imports \
--disallow-untyped-defs \
--check-untyped-defs
MYPY_STRICT = mypy . --strict
PYCACHE = __pycache__
MYPY_CACHE = .mypy_cache

DEBUG = --print-debug

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(SRC) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(SRC) $(CONFIG)

clean:
ifeq ($(OS),Windows_NT)
	@if exist "$(PYCACHE)" @rmdir /s /q "$(PYCACHE)"
	@if exist "$(MYPY_CACHE)" @rmdir /s /q "$(MYPY_CACHE)"
else
	rm -rf $(PYCACHE) $(MYPY_CACHE)
endif

lint:
	$(FLAKE8)
	$(MYPY)

lint-strict:
	$(FLAKE8)
	$(MYPY_STRICT)

# DEBUG
run2:
	$(PYTHON) $(SRC) $(CONFIG) $(DEBUG)
	$(PYTHON) maze_analyzer.py --max-dead-ends 0 maze.txt
# DEBUG END