default:
	@echo "Available commands: make update, make lint, make test"

update:
	. env/bin/activate; pip install -r requirements.txt

lint:
	. env/bin/activate; pylint bin/clean_ids.py

test: lint
	. env/bin/activate; pytest -vv tests

test_enrich:
	@. env/bin/activate && cat mock_transcripts.jsonl | python -u bin/enrich_transcripts.py | python bin/validate_schema.py
.PHONY: load
load:
	@echo "Initiating Cloud Data Warehouse Synchronizer Node..."
	cat data/enriched_transcripts.jsonl | python bin/load_snowflake.py
