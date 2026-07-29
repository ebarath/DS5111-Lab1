FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY bin/ ./bin/
COPY data/ ./data/

RUN mkdir -p pipeline/logs/

CMD ["sh", "-c", "python bin/clean_ids.py | python bin/extract_transcripts.py | python bin/enrich_transcripts.py | python bin/load_snowflake.py"]
