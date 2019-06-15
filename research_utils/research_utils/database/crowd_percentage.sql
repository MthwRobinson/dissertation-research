CREATE MATERIALIZED VIEW open_source.crowd_percentage
AS
SELECT a.package_id, c.package_name as package, c.org_name as organization,
      CAST(a.crowd AS DECIMAL)/b.total as crowd_pct, b.total
FROM(
  SELECT COUNT(*) as crowd, package_id
  FROM open_source.issue_contributors
  WHERE crowd_pct = 0
  GROUP BY package_id
) a
INNER JOIN (
  SELECT COUNT(*) as total, package_id
  FROM open_source.issue_contributors
  GROUP BY package_id
) b
ON a.package_id = b.package_id
INNER JOIN open_source.packages c
ON a.package_id = c.id
