#!/usr/bin/env python3
"""Enrich transcript records using an interchangeable LLM strategy."""

from abc import ABC, abstractmethod
import json
import logging
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types


class LLMStrategy(ABC):
    """Define the interface for transcript enrichment strategies."""

    @abstractmethod
    def enrich(self, transcript_record: dict) -> dict:
        """Enrich one transcript record and return the resulting record."""
        raise NotImplementedError


class GeminiStrategy(LLMStrategy):
    """Enrich transcript records using Google's Gemini API."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.5-flash",
    ) -> None:
        """Initialize the Gemini client and structured-output configuration."""
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

        self.schema = {
            "type": "object",
            "properties": {
                "video_id": {"type": "string"},
                "cleaned_text": {"type": "string"},
                "tech_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "book_names": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": [
                "video_id",
                "cleaned_text",
                "tech_terms",
                "book_names",
            ],
        }

        self.config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self.schema,
            temperature=0.0,
        )

    def enrich(self, transcript_record: dict) -> dict:
        """Enrich one transcript record using Gemini."""
        prompt = f"""
Clean and enrich this transcript.

Return JSON with exactly these fields:
- video_id
- cleaned_text
- tech_terms
- book_names

video_id: {transcript_record.get("video_id")}
raw_text: {transcript_record.get("raw_text")}
"""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.config,
        )

        return json.loads(response.text)


def main() -> None:
    """Read JSONL records from stdin and write enriched JSONL to stdout."""
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.critical("GEMINI_API_KEY is missing.")
        sys.exit(1)

    strategy = GeminiStrategy(api_key=api_key)

    for line in sys.stdin:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            logging.error("Invalid JSON input line: %s", line.strip())
            continue

        try:
            enriched_record = strategy.enrich(record)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            logging.error(
                "Failed to enrich record %s: %s",
                record.get("video_id"),
                error,
            )
            continue

        sys.stdout.write(json.dumps(enriched_record) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
