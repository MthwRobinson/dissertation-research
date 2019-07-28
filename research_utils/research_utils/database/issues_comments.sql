DROP MATERIALIZED VIEW open_source.issue_comments;
CREATE MATERIALIZED VIEW open_source.issue_comments
AS
SELECT c.id as comment_id, c.package, c.organization, c.issue_number,
c.user_id, c.created_at as comment_time, a.created_at as issue_time,
a.id as issue_id
FROM open_source.issues a
INNER JOIN (
  SELECT organization, package, total
  FROM(
    SELECT organization, package,
	  	   COUNT(*) as total
	FROM open_source.issues
    WHERE created_at < '2019-01-01'
	AND ('bug' = ANY(lower(labels::text)::text[])
	OR 'feature' = ANY(lower(labels::text)::text[])
	OR 'feature request' = ANY(lower(labels::text)::text[])
	OR 'change' = ANY(lower(labels::text)::text[])
	OR 'suggestion' = ANY(lower(labels::text)::text[])
	OR 'enhancement' = ANY(lower(labels::text)::text[]))
    GROUP BY organization, package
) x
WHERE total >= 30
) b
ON (a.organization = b.organization
AND a.package = b.package)
INNER JOIN open_source.comments c
ON c.issue_id = a.id
