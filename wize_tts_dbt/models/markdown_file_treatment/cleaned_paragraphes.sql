{{ 
    config(
        materialized = 'table' 
    ) 
}}

WITH raw_text AS (
    SELECT
        note_name,
        content_id,
        paragrapge_order,
        paragraphe_content
    FROM {{ ref('paragraphes') }} -- This refers to the source table where paragraphs are stored
),
cleaned_text AS (
    SELECT
        note_name,
        content_id,
        paragrapge_order,
        paragraphe_content,
        
        -- Remove curly quotes and replace with straight quotes
        REPLACE(REPLACE(paragraphe_content, '“', '"'), '”', '"') AS content_step_1,

        -- Replace nested quotes and ensure standard quote usage (for dialogue)
        REPLACE(
            REPLACE(REPLACE(REPLACE(paragraphe_content, '“', '"'), '”', '"'), '"""', '«'),
            '"""', '»'
        ) AS content_step_2,

        -- Remove excessive asterisks or symbols like "* * *"
        REPLACE(
            REPLACE(
                REPLACE(REPLACE(paragraphe_content, '“', '"'), '”', '"'),
                '"""', '«'
            ),
            '* * *', ''
        ) AS content_step_3,

        -- Normalize ellipses ("...") by ensuring they are represented consistently
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(paragraphe_content, '“', '"'), '”', '"'
                ),
                '"""', '«'
            ),
            '...', '...'
        ) AS content_step_4,

        -- Remove unnecessary spaces between words or after punctuation
        REGEXP_REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(REPLACE(paragraphe_content, '“', '"'), '”', '"'),
                    '"""', '«'
                ),
                '...', '...'
            ),
   