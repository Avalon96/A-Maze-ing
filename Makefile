# Windows

PYTHON = python
# PYTHON = python3
SRC = main.py
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
	rmdir /s /q __pycache__
	rmdir /s /q .mypy_cache
# 	rm -rf $(CACHE)

lint:
	$(FLAKE8)
	$(MYPY)

lint-strict:
	$(FLAKE8)
	$(MYPY_STRICT)

# DEBUG
run2:
	$(PYTHON) $(SRC) $(CONFIG) --print-debug
# DEBUG END