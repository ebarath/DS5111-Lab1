#!/usr/bin/env python3
"""Enrich transcript records using interchangeable LLM strategies."""

from abc import ABC, abstractmethod
import argparse
import json
import logging
import os
import sys
from typing import TextIO

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

        schema = {
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
            response_schema=schema,
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


class TranscriptEnricher:
    """Process transcript records using an injected LLM strategy."""

    def __init__(self, strategy: LLMStrategy) -> None:
        """Store the enrichment strategy."""
        self.strategy = strategy

    def process_stream(
        self,
        input_stream: TextIO,
        output_stream: TextIO,
    ) -> None:
        """Read JSONL input, enrich valid records, and write JSONL output."""
        for line in input_stream:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                logging.error("Invalid JSON input line: %s", line.strip())
                continue

            try:
                enriched_record = self.strategy.enrich(record)
            except (ValueError, TypeError, json.JSONDecodeError) as error:
                logging.error(
                    "Failed to enrich record %s: %s",
                    record.get("video_id"),
                    error,
                )
                continue

            output_stream.write(json.dumps(enriched_record) + "\n")
            output_stream.flush()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Enrich transcript JSONL records."
    )
    parser.add_argument(
        "--engine",
        choices=["gemini"],
        default="gemini",
        help="LLM engine used for transcript enrichment.",
    )

    return parser.parse_known_args()[0]


def build_strategy(engine: str) -> LLMStrategy:
    """Create the requested LLM strategy."""
    if engine == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        return GeminiStrategy(api_key=api_key)

    raise ValueError(f"Unsupported enrichment engine: {engine}")


def main() -> None:
    """Configure and run the transcript enrichment pipeline."""
    load_dotenv()
    args = parse_args()

    try:
        strategy = build_strategy(args.engine)
    except ValueError as error:
        logging.critical("%s", error)
        sys.exit(1)

    enricher = TranscriptEnricher(strategy)
    enricher.process_stream(sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()
