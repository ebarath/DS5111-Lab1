"""Tests for the transcript enrichment pipeline."""

import io
import json
import sys

from bin.enrich_transcripts import (
    LLMStrategy,
    TranscriptEnricher,
    main,
)


class MockLLMStrategy(LLMStrategy):
    """Provide deterministic enrichment without a network call."""

    def enrich(self, transcript_record: dict) -> dict:
        """Return a predictable enriched transcript."""
        return {
            "video_id": transcript_record.get("video_id"),
            "cleaned_text": (
                "Welcome to class. "
                "Today we are testing mock frameworks."
            ),
            "tech_terms": ["mock frameworks"],
            "book_names": [],
        }


class MockGeminiResponse:
    """Represent a minimal mocked Gemini response."""

    def __init__(self, text_payload: str) -> None:
        """Store the mocked response text."""
        self.text = text_payload


def test_transcript_enricher_with_mock_strategy():
    """Verify dependency injection with a local mock strategy."""
    input_record = {
        "video_id": "ds5111_v001",
        "raw_text": (
            "00:01 Welcome to class. "
            "Today we are testing mock frameworks."
        ),
    }

    enricher = TranscriptEnricher(MockLLMStrategy())
    output_record = enricher.process_record(input_record)

    assert output_record["video_id"] == "ds5111_v001"
    assert output_record["cleaned_text"] == (
        "Welcome to class. "
        "Today we are testing mock frameworks."
    )
    assert output_record["tech_terms"] == ["mock frameworks"]
    assert output_record["book_names"] == []


def test_transcript_enricher_processes_jsonl_stream():
    """Verify JSONL input and output with a mock strategy."""
    input_record = {
        "video_id": "ds5111_v001",
        "raw_text": (
            "00:01 Welcome to class. "
            "Today we are testing mock frameworks."
        ),
    }

    input_stream = io.StringIO(
        json.dumps(input_record) + "\n"
    )
    output_stream = io.StringIO()

    enricher = TranscriptEnricher(MockLLMStrategy())
    enricher.process_stream(
        input_stream=input_stream,
        output_stream=output_stream,
    )

    output_lines = output_stream.getvalue().strip().splitlines()

    assert len(output_lines) == 1

    output_record = json.loads(output_lines[0])

    assert output_record["video_id"] == "ds5111_v001"
    assert output_record["tech_terms"] == ["mock frameworks"]
    assert output_record["book_names"] == []


def test_enrich_transcripts_streaming_pipeline(
    monkeypatch,
    capsys,
):
    """Verify main without making a live Gemini request."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def mock_generate_content(
        self,
        model,
        contents,
        config=None,
    ):
        del self
        del model
        del contents
        del config

        mock_data = {
            "video_id": "ds5111_v001",
            "cleaned_text": (
                "Welcome to class. "
                "Today we are testing mock frameworks."
            ),
            "tech_terms": ["mock frameworks"],
            "book_names": [],
        }

        return MockGeminiResponse(json.dumps(mock_data))

    from google.genai.models import Models

    monkeypatch.setattr(
        Models,
        "generate_content",
        mock_generate_content,
    )

    mock_input_row = {
        "video_id": "ds5111_v001",
        "raw_text": (
            "00:01 Welcome to class. "
            "Today we are testing mock frameworks."
        ),
    }

    mock_stdin = io.StringIO(
        json.dumps(mock_input_row) + "\n"
    )

    monkeypatch.setattr(sys, "stdin", mock_stdin)

    main([])

    captured = capsys.readouterr()
    output_lines = captured.out.strip().splitlines()

    assert len(output_lines) == 1

    output_record = json.loads(output_lines[0])

    assert output_record["video_id"] == "ds5111_v001"
    assert output_record["cleaned_text"] == (
        "Welcome to class. "
        "Today we are testing mock frameworks."
    )
    assert output_record["tech_terms"] == ["mock frameworks"]
    assert output_record["book_names"] == []
