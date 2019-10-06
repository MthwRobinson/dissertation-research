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
  pull_request boolean,
  topics_10 numeric[],
  topics_25 numeric[],
  topics_50 numeric[],
  topics_100 numeric[],
  topics_200 numeric[]
);

CREATE TABLE IF NOT EXISTS open_source.comments (
  id text,
  organization text,
  package text,
  issue_id text,
  issue_number integer,
  user_id text,
  user_login text,
  body text,
  updated_at timestamp,
  created_at timestamp
);

CREATE TABLE IF NOT EXISTS open_source.contributors (
  id text,
  package_id text,
  organization text,
  package text,
  user_id text,
  login text,
  commits integer
);

CREATE TABLE IF NOT EXISTS open_source.stakeholder_networks (
  organization text,
  package text,
  stakeholder_network bytea,
  gini_coefficient numeric,
  avg_clustering numeric,
  avg_min_path numeric,
  ks_pval numeric
);

CREATE TABLE IF NOT EXISTS open_source.network_centrality (
  organization text,
  package text,
  user_id text,
  betweenness_centrality numeric
);
