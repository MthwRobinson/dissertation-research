CREATE MATERIALIZED VIEW open_source.issue_contributors
AS
  SELECT x.package_id,
         x.user_id,
        commit_pct
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
