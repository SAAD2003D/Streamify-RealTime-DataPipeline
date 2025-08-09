-- models/staging/stg_raw_user_events.sql
-- Selects relevant columns and casts the timestamp to a proper TIMESTAMP type

select
    user_id,
    event_type,
    -- Attempt to parse various common ISO8601 string formats
    -- Adjust this PARSE_TIMESTAMP format string to match your actual timestamp data
    -- This example tries a common format with milliseconds and 'T' separator.
    -- If it's already a BQ TIMESTAMP, just use: CAST(timestamp AS TIMESTAMP) as event_timestamp,
    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', timestamp) as event_timestamp,
    song_id,
    song_title,
    artist_name
    -- Add other columns like device, location if needed for later models
from {{ source('streamify_bq_source', 'raw_user_events') }}
where
    user_id is not null and
    timestamp is not null and
    event_type is not null