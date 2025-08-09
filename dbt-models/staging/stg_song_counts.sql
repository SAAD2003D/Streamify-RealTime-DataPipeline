-- models/staging/stg_song_counts.sql
-- Selects and potentially standardizes columns from the source song_counts table

select
    song_id,
    song_title,
    artist_name,
    play_count
from {{ source('streamify_bq_source', 'song_count') }}
-- You could add where clauses here if needed, e.g., where play_count > 0