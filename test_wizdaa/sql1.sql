/*
Table: events
user_id event_date event_type
u1 2024-01-01 click
u1 2024-01-02 click
u2 2024-01-02 click
u1 2024-01-03 view
Description
Write a SQL query that returns:
● Daily active users per day
● A 3-day rolling average of daily active users
Use window functions. Assume Postgres or Snowflake.
*/
with events as (
    select event_date, count(distinct user_id) as daily_active_users
    from events
)
select event_date, daily_active_users,
round(avg(daily_active_users) over(order by event_date rows between 2 preceding and current row), 2) as rolling_avg_daily_active_users
from events