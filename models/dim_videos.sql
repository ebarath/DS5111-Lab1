{{ config(materialized='table') }}

-- Step 2: Dimension Table (Metrics & Aggregations)

SELECT
    VIDEO_ID,
    CLEANED_TEXT,
    ARRAY_SIZE(TECH_TERMS_ARRAY) AS TECH_TERM_COUNT,
    ARRAY_SIZE(BOOK_NAMES_ARRAY) AS BOOK_NAME_COUNT,
    ARRAY_SIZE(SPLIT(CLEANED_TEXT, ' ')) AS WORD_COUNT,
    INSERTED_AT AS PROCESSED_AT
FROM {{ ref('stg_youtube_transcripts') }}