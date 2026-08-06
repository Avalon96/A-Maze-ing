.PHONY: install run debug clean lint lint-strict analyze

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
OUTPUT = maze.txt
ANALYZER = maze_analyzer.py
BONUS = --max-dead-ends 0

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(SRC) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(SRC) $(CONFIG)

clean:
ifeq ($(OS),Windows_NT)
	@if exist "$(PYCACHE)" rmdir /s /q "$(PYCACHE)"
	@if exist "$(MYPY_CACHE)" rmdir /s /q "$(MYPY_CACHE)"
else
	find . -type d -name "$(PYCACHE)" -exec rm -rf {} +
	find . -type d -name "$(MYPY_CACHE)" -exec rm -rf {} +
endif

lint:
	$(FLAKE8)
	$(MYPY)

lint-strict:
	$(FLAKE8)
	$(MYPY_STRICT)

analyze: run
	$(PYTHON) $(ANALYZER) $(BONUS) $(OUTPUT)