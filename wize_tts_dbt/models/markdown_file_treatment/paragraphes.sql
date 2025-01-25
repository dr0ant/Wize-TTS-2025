{{ 
    config(
        materialized = 'table' 
    ) 
}}

WITH paragraphs_extracted AS (
    SELECT
        nc.note_name,
        nc.content_id,
        ROW_NUMBER() OVER (PARTITION BY nc.content_id ORDER BY position) AS paragrapge_order,
        paragraph AS paragraphe_content,
        position
    FROM
        wizetts.note_content AS nc,
        LATERAL REGEXP_SPLIT_TO_TABLE(nc.content, E'\n\n') WITH ORDINALITY AS t(paragraph, position)
)
SELECT
    note_name,
    content_id,
    paragrapge_order,
    paragraphe_content,
    position AS paragraph_position,
    NOW() as update_date
FROM paragraphs_extracted
ORDER BY content_id, paragraph_position