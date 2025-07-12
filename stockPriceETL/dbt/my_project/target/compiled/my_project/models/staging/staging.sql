

with source as (
    select * from "db"."dev"."raw_weather_data"
),

de_dup as (
    select *,   
        row_number() over(partition by time order by inserted_at) as rm 
    from source
)

SELECT
    id,
    city,
    temperature,
    weather_description,
    wind_speed,
    time AS weather_time_local,
    (inserted_at + (utc_offset || ' hours')::interval) AS inserted_at_local
FROM de_dup
WHERE rm = 1