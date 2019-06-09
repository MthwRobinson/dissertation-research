CREATE MATERIALIZED VIEW open_source.issue_contributors
AS
SELECT y.package_id, y.user_id, contributor
FROM open_source.issues y
INNER JOIN (
  SELECT x.package_id,
         x.user_id,
         CASE
          WHEN commit_pct > 0.05 THEN TRUE
          ELSE FALSE
         END as contributor
  FROM(
    SELECT a.user_id, a.package_id, CAST(commits AS DECIMAL)/ total_commits AS commit_pct
    FROM open_source.contributors a
    INNER JOIN(
      SELECT SUM(commits) AS total_commits, package_id
      FROM open_source.contributors
      GROUP BY package_id
   ) b
   ON a.package_id = b.package_id
  ) x
) z
ON (y.package_id = z.package_id AND y.user_id = z.user_id)
