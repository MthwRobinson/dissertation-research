CREATE MATERIALIZED VIEW open_source.reqs_prioritization
AS
SELECT DISTINCT
	   user_id, package, organization, commit_pct,
	   avg_clustering, avg_min_path, gini_coefficient,
	   total_stakeholders, total_open, betweenness_centrality,
	   CASE
	   		WHEN duration IS NOT NULL then duration
        ELSE EXTRACT(DAYS FROM NOW() - created_at),
	   END as duration,
	   CASE
	   		WHEN duration IS NOT NULL then 1
			ELSE 0
		END as closed
FROM(
	SELECT a.user_id, b.package, b.organization,
		   avg_clustering, avg_min_path, gini_coefficient,
		   EXTRACT(days FROM AGE(closed_at::TIMESTAMP, created_at::TIMESTAMP)) as duration,
		   created_at, closed_at,
		   c.total_stakeholders, d.total_open, e.betweenness_centrality,
       pull_request
	FROM open_source.issues a
	INNER JOIN open_source.stakeholder_networks b
	ON (a.organization = b.organization AND a.package = b.package)
	INNER JOIN open_source.network_centrality e
	ON (a.organization = e.organization AND a.package = e.package AND a.user_id = e.user_id)
	INNER JOIN(
		SELECT organization, package, COUNT(DISTINCT user_id) as total_stakeholders
		FROM open_source.comments
		WHERE created_at > '2018-01-01'
		GROUP BY organization, package
	) c
	ON (a.organization = c.organization AND a.package = c.package)
	INNER JOIN (
		SELECT organization, package, COUNT(*) as total_open
		FROM open_source.issues
		WHERE created_at < '2018-01-01'
		AND (closed_at > '2018-01-01' OR closed_at IS NULL)
		GROUP BY organization, package
	) d
	ON (a.organization = d.organization AND a.package = d.package)
	WHERE a.created_at > '2018-01-01' and a.created_at < '2019-01-01'
) x
