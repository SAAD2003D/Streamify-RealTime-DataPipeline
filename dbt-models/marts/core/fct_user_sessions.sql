-- models/marts/core/fct_user_sessions.sql
-- Segments user activity into sessions based on a 30-minute inactivity rule.

{{
    config(
        materialized='table'
    )
}}

with source_events_ordered as (
    -- Select necessary fields and order events for each user
    select
        user_id,
        event_timestamp, -- This must be a TIMESTAMP data type
        -- Include other fields if you want to analyze them per session, e.g., event_type, song_id
        event_type,
        song_id
    from {{ ref('stg_raw_user_events') }}
    where user_id is not null and event_timestamp is not null -- Ensure essential fields are present
    -- QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_timestamp) IS NOT NULL -- Redundant if already ordered
),

previous_event_time as (
    -- Calculate the time of the previous event for each user
    select
        *,
        lag(event_timestamp, 1) over (
            partition by user_id
            order by event_timestamp
        ) as previous_event_timestamp
    from source_events_ordered
),

session_start_indicators as (
    -- Flag events that mark the beginning of a new session
    select
        *,
        case
            when previous_event_timestamp is null then 1 -- First event for a user is always a new session
            when timestamp_diff(event_timestamp, previous_event_timestamp, minute) > 30 then 1 -- Gap > 30 mins
            else 0
        end as is_new_session_marker
    from previous_event_time
),

session_groups as (
    -- Assign a session group ID by calculating a running sum of new session markers
    select
        *,
        sum(is_new_session_marker) over (
            partition by user_id
            order by event_timestamp
            rows between unbounded preceding and current row -- Ensures running sum
        ) as session_group_id
    from session_start_indicators
),

session_details as (
    -- Aggregate events by user and session group to get session metrics
    select
        user_id,
        session_group_id, -- Temporary ID for grouping
        min(event_timestamp) as session_start_time,
        max(event_timestamp) as session_end_time,
        count(*) as total_events_in_session,
        count(distinct song_id) as distinct_songs_in_session -- If song_id is available
    from session_groups
    group by
        user_id,
        session_group_id
)

-- Final selection and creation of a more unique session ID
select
    farm_fingerprint(concat(user_id, cast(session_group_id as string))) as session_id, -- Create a unique session ID
    user_id,
    session_start_time,
    session_end_time,
    timestamp_diff(session_end_time, session_start_time, second) as session_duration_seconds,
    total_events_in_session,
    distinct_songs_in_session
from session_details
order by
    user_id,
    session_start_time