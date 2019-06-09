CREATE MATERIALIZED VIEW open_source.issue_contributors
AS
 SELECT DISTINCT
  y.package_id,
  y.user_id,
  y.issue_id,
  CASE 
    WHEN commit_pct IS NOT NULL THEN commit_pct
    ELSE 0 
  END AS commit_pct
FROM (
  SELECT user_id, package_id, id as issue_id
  FROM open_source.issues
) y
LEFT JOIN
( SELECT a.user_id,
          a.package_id,
          a.commits::numeric / b.total_commits::numeric AS commit_pct
  FROM open_source.contributors a
  JOIN ( SELECT sum(contributors.commits) AS total_commits,
          contributors.package_id
          FROM open_source.contributors
  GROUP BY contributors.package_id) b 
  ON a.package_id = b.package_id
) x
ON (x.package_id = y.package_id AND x.user_id = y.user_id )
