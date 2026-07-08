#!/usr/bin/env python3

import json
import logging
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.critical("GEMINI_API_KEY is missing.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

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
        "required": ["video_id", "cleaned_text", "tech_terms", "book_names"],
    }

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
        temperature=0.0,
    )

    for line in sys.stdin:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            logging.error("Invalid JSON input line: %s", line.strip())
            continue

        prompt = f"""
Clean and enrich this transcript.

Return JSON with exactly these fields:
- video_id
- cleaned_text
- tech_terms
- book_names

video_id: {record.get("video_id")}
raw_text: {record.get("raw_text")}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )

        sys.stdout.write(response.text.strip() + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
