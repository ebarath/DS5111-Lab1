#!/usr/bin/env python3

import json
import sys


REQUIRED_FIELDS = {
    "video_id": str,
    "cleaned_text": str,
    "tech_terms": list,
    "book_names": list,
}


def validate_record(record):
    for field_name, field_type in REQUIRED_FIELDS.items():
        if field_name not in record:
            raise ValueError(f"Missing required field: {field_name}")
        if not isinstance(record[field_name], field_type):
            raise TypeError(f"{field_name} must be {field_type.__name__}")

    for item in record["tech_terms"]:
        if not isinstance(item, str):
            raise TypeError("tech_terms must contain only strings")

    for item in record["book_names"]:
        if not isinstance(item, str):
            raise TypeError("book_names must contain only strings")


def main():
    for line in sys.stdin:
        record = json.loads(line)
        validate_record(record)

    print("Schema validation passed.")


if __name__ == "__main__":
    main()
