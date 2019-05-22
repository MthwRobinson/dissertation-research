CREATE SCHEMA IF NOT EXISTS open_source;

CREATE TABLE IF NOT EXISTS open_source.packages (
  id text,
  org_name text,
  package_name text,
  url text,
  language text
);

CREATE TABLE IF NOT EXISTS open_source.users (
  id text,
  login text,
  user_type text
);

CREATE TABLE IF NOT EXISTS open_source.issues (
  id text,
  package_id text,
  organization text,
  package text,
  user_id text,
  user_login text,
  issue_number integer,
  title text,
  created_at timestamp,
  updated_at timestamp,
  closed_at timestamp,
  labels text[],
  assignee text,
  assignees text[],
  pull_request boolean
);
