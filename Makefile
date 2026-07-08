ENV = env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip
PYTEST = $(ENV)/bin/pytest
PYLINT = $(ENV)/bin/pylint

.PHONY: default env update lint test run test_enrich clean

default:
	@echo "Available commands: make env, make update, make lint, make test, make run"

env:
	python3 -m venv $(ENV)

update:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

lint:
	$(PYLINT) bin/ lib/ tests/

test:
	$(PYTEST) -vv tests/

run:
	cat test_ids | $(PYTHON) -u bin/clean_ids.py

test_enrich:
	cat mock_transcripts.jsonl | $(PYTHON) -u bin/enrich_transcripts.py | $(PYTHON) bin/validate_schema.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
