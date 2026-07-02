# ReYMeN Agent — Makefile
# Kullanim: make install / make test / make lint / make clean

.PHONY: install test lint format clean docker-build

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Windows detect
ifneq (,$(findstring Windows,$(OS)))
	PYTHON = $(VENV)\Scripts\python
	PIP = $(VENV)\Scripts\pip
	RM = del /q
else
	RM = rm -f
endif

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -e ".[dev,full]"
	pre-commit install

install-min:
	$(PIP) install -e .

test:
	$(PYTHON) -m pytest tests/ \
		--ignore=tests/hermes_legacy \
		--ignore=tests/ReYMeN_reference \
		--ignore=tests/hermes_reference \
		--tb=short -q --timeout=120 \
		--cov=reymen --cov-report=term-missing

lint:
	ruff check reymen/ tests/ reymen_launcher.py
	ruff format --check reymen/ tests/ reymen_launcher.py

format:
	ruff check --fix reymen/ tests/ reymen_launcher.py
	ruff format reymen/ tests/ reymen_launcher.py

security:
	bandit -r reymen/ -ll --skip B101,B603,B602

clean:
	find . -type d -name "__pycache__" -exec $(RM) -r {} + 2>/dev/null || true
	$(RM) -rf .pytest_cache .ruff_cache .mypy_cache 2>/dev/null || true
	$(RM) -rf *.egg-info build dist 2>/dev/null || true

docker-build:
	docker build -t reymen-agent .

docker-run:
	docker-compose up -d

all: lint test security
