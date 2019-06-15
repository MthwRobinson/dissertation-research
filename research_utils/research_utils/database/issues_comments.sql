CREATE MATERIALIZED VIEW open_source.issue_comments
AS
SELECT c.id as comment_id, c.package, c.organization, c.issue_number, 
c.user_id, c.created_at as comment_time, a.created_at as issue_time
FROM open_source.issues a
INNER JOIN (
  SELECT organization, package, total, oldest
  FROM(
    SELECT organization, package, COUNT(*) as total,
           MIN(created_at) as oldest
    FROM open_source.issues
    WHERE created_at < '2019-01-01'
    AND created_at >= '2018-01-01'
    GROUP BY organization, package
) x
WHERE oldest < '2018-02-01'
AND total > 10
) b
ON (a.organization = b.organization
AND a.package = b.package)
INNER JOIN open_source.comments c
ON c.issue_id = a.id
WHERE a.created_at >= '2018-01-01'
AND a.created_at < '2019-01-01'
