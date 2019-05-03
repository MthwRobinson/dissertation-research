CREATE SCHEMA IF NOT EXISTS open_source;

CREATE TABLE IF NOT EXISTS open_source.packages (
  id integer,
  package_name text,
  org_name text,
  url text
);
