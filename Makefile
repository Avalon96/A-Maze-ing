# Windows

# PYTHON = python3
PYTHON = python
SRC = main.py
CONFIG = default_config.txt

FLAKE8 = flake8 .
MYPY = mypy . --warn-return-any \
--warn-unused-ignores \
--ignore-missing-imports \
--disallow-untyped-defs \
--check-untyped-defs
MYPY_STRICT = mypy . --strict

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(SRC) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(SRC) $(CONFIG)

clean:
	rmdir /s /q __pycache__
	rmdir /s /q .mypy_cache
# 	rm -rf __pycache__ .mypy_cache

lint:
	$(FLAKE8)
	$(MYPY)

lint-strict:
	$(MYPY_STRICT)
