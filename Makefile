default:
	@echo "Available commands: make update, make lint, make test"

update:
	. env/bin/activate; pip install -r requirements.txt

lint:
	. env/bin/activate; pylint bin/clean_ids.py

test: lint
	. env/bin/activate; pytest -vv tests

