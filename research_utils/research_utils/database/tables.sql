CREATE SCHEMA IF NOT EXISTS dissertation;

CREATE TABLE IF NOT EXISTS dissertation.groups (
  id text,
  name text,
  members integer,
  past_event_count integer
);

CREATE TABLE IF NOT EXISTS dissertation.events (
  id text,
  group_id text,
  name text,
  event_time timestamp,
  yes_rsvp_count integer
);

CREATE TABLE IF NOT EXISTS dissertation.attendees (
  member_id text,
  event_id text
);
