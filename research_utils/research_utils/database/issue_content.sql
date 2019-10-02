CREATE MATERIALIZED VIEW open_source.issue_content
AS
SELECT a.created_at as issue_time, a.id as issue_id, a.title,
       a.body, a.organization, a.package, a.issue_number
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
WHERE a.body IS NOT NULL
