#!/usr/bin/env python3

"""Enrich transcript records using an object-oriented LLM strategy."""

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

        response_schema = {
            "type": "object",
            "properties": {
                "video_id": {
                    "type": "string",
                },
                "cleaned_text": {
                    "type": "string",
                },
                "tech_terms": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "book_names": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
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
            response_schema=response_schema,
            temperature=0.0,
        )

    def enrich(self, transcript_record: dict) -> dict:
        """Send one transcript record to Gemini and return parsed output."""
        prompt = (
            "Clean and enrich this transcript.\n\n"
            "Return JSON with exactly these fields:\n"
            "- video_id\n"
            "- cleaned_text\n"
            "- tech_terms\n"
            "- book_names\n\n"
            f"video_id: {transcript_record.get('video_id')}\n"
            f"raw_text: {transcript_record.get('raw_text')}\n"
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.config,
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        enriched_record = json.loads(response.text)

        if not isinstance(enriched_record, dict):
            raise TypeError("Gemini response must be a JSON object.")

        return enriched_record


class TranscriptEnricher:
    """Process transcript records using an injected LLM strategy."""

    def __init__(self, strategy: LLMStrategy) -> None:
        """Store the selected enrichment strategy."""
        self.strategy = strategy

    def process_record(self, transcript_record: dict) -> dict:
        """Enrich a single transcript record."""
        return self.strategy.enrich(transcript_record)

    def process_stream(
        self,
        input_stream: TextIO,
        output_stream: TextIO,
    ) -> None:
        """Read JSONL records, enrich them, and write JSONL output."""
        for line in input_stream:
            stripped_line = line.strip()

            if not stripped_line:
                continue

            try:
                transcript_record = json.loads(stripped_line)
            except json.JSONDecodeError:
                logging.error(
                    "Invalid JSON input line: %s",
                    stripped_line,
                )
                continue

            if not isinstance(transcript_record, dict):
                logging.error(
                    "Input JSON must be an object: %s",
                    stripped_line,
                )
                continue

            try:
                enriched_record = self.process_record(transcript_record)
            except (
                json.JSONDecodeError,
                TypeError,
                ValueError,
                RuntimeError,
            ) as error:
                logging.error(
                    "Unable to enrich transcript %s: %s",
                    transcript_record.get("video_id"),
                    error,
                )
                continue

            output_stream.write(
                json.dumps(enriched_record) + "\n"
            )
            output_stream.flush()


def parse_arguments(
    arguments: list[str] | None = None,
) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Enrich transcript JSONL records using an LLM strategy."
        ),
    )

    parser.add_argument(
        "--engine",
        choices=["gemini"],
        default="gemini",
        help="LLM enrichment engine to use.",
    )

    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Model name used by the selected engine.",
    )

    return parser.parse_args(arguments)


def create_strategy(
    engine: str,
    model_name: str,
) -> LLMStrategy:
    """Create the requested LLM strategy."""
    if engine == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        return GeminiStrategy(
            api_key=api_key,
            model_name=model_name,
        )

    raise ValueError(f"Unsupported engine: {engine}")


def main(arguments: list[str] | None = None) -> None:
    """Run the transcript enrichment pipeline."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    parsed_arguments = parse_arguments(arguments)

    try:
        strategy = create_strategy(
            engine=parsed_arguments.engine,
            model_name=parsed_arguments.model,
        )
    except ValueError as error:
        logging.critical("%s", error)
        raise SystemExit(1) from error

    enricher = TranscriptEnricher(strategy)
    enricher.process_stream(
        input_stream=sys.stdin,
        output_stream=sys.stdout,
    )


if __name__ == "__main__":
    main()
