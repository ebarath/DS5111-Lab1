#!/usr/bin/env python3

import sys
import re
import logging

logging.basicConfig(
    filename="pipeline_autid.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

pattern = re.compile(r'^[A-Za-z0-9_-]{11}$')

for line in sys.stdin:
    youtube_id = line.strip()

    if pattern.match(youtube_id):
        print(youtube_id)
    else:
        logging.info(f"Invalid YouTube ID: {youtube_id}")
