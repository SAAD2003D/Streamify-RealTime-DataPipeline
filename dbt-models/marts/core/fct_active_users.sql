-- models/marts/core/fct_active_users.sql
-- Identifies users with frequent song plays in a rolling 7-day window.

{{
    config(
        materialized='table' 
    )
}}

with play_events_in_window as (
    select
        user_id,
        event_timestamp, -- This must be a TIMESTAMP data type from stg_raw_user_events
        song_id          -- Included if you want to count distinct songs played by active users
    from {{ ref('stg_raw_user_events') }}
    where
        event_type = 'play'
        -- Rolling 7-day window from the current time
        and event_timestamp >= '2024-05-01 00:00:00 UTC' -- Example fixed start
      and event_timestamp < '2024-05-21 00:00:00 UTC' -- Example fixed end -- Avoid including future events if any
)

select
    user_id,
    count(*) as total_plays_last_7_days,          -- Total play events in the window
    count(distinct song_id) as distinct_songs_played_last_7_days, -- Optional: distinct songs
    max(event_timestamp) as last_active_time    -- Last play event time in the window
from play_events_in_window
group by
    user_id
-- Optional: Define a threshold for "active"
-- having count(*) > 5 -- Example: User must have more than 5 plays to be considered active
order by
    total_plays_last_7_days desc,
    last_active_time desc