CREATE SCHEMA IF NOT EXISTS open_source;

CREATE TABLE IF NOT EXISTS open_source.packages (
  id text,
  org_name text,
  package_name text,
  url text,
  language text
);
