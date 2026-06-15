#!/usr/bin/env python3
"""Clean YouTube IDs from standard input."""

import logging
import re
import sys

logging.basicConfig(
    filename="pipeline_autid.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

YOUTUBE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def main():
    """Print valid YouTube IDs and log invalid lines."""
    for input_line in sys.stdin:
        youtube_id = input_line.strip()

        if YOUTUBE_ID_PATTERN.match(youtube_id):
            print(youtube_id)
        else:
            logging.info("Invalid YouTube ID: %s", youtube_id)


if __name__ == "__main__":
    main()
