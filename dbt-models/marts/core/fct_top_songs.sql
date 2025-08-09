-- models/marts/core/fct_top_songs.sql
-- This model identifies the top N most played songs.
-- It assumes 'stg_song_counts' provides total play counts per song.

{{
    config(
        materialized='table'
    )
}}

select
    song_id,
    song_title,
    artist_name,
    play_count as total_play_count
from {{ ref('stg_song_counts') }} -- Referencing the staging model for song counts
where play_count > 0 -- Optional: filter out songs with zero plays
order by total_play_count desc
-- limit 100 -- Optional: if you only want to store the top N songs