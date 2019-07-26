DROP MATERIALIZED VIEW reqs_prioritization;
CREATE MATERIALIZED VIEW reqs_prioritization
AS
SELECT DISTINCT
	   *,
       CASE
	   		WHEN duration IS NOT NULL then duration
        	ELSE EXTRACT(DAYS FROM NOW() - created_at)
	   END as adj_duration,
	   CASE
	   		WHEN duration IS NOT NULL then 1
			ELSE 0
		END as closed
FROM(
	SELECT DISTINCT
		   a.package, a.organization, a.package_id, a.user_id, a.created_at, a.closed_at, a.pull_request,
		   EXTRACT(DAYS FROM a.closed_at - a.created_at) as duration,
		   b.gini_coefficient, b.avg_clustering, b.avg_min_path,
		   c.total_stakeholders, d.betweenness_centrality, e.commit_pct
	FROM (
		SELECT *
		FROM open_source.issues
		WHERE created_at >= '2018-01-01'
		AND created_at < '2019-01-01'
		AND package IN (SELECT package FROM open_source.stakeholder_networks)
	) a
	INNER JOIN open_source.stakeholder_networks b
	ON (a.organization = b.organization AND a.package = b.package)
	INNER JOIN(
		SELECT organization, package, COUNT(DISTINCT user_id) as total_stakeholders
		FROM open_source.comments
		WHERE created_at > '2018-01-01'
		AND package IN (SELECT package FROM open_source.stakeholder_networks)
		GROUP BY organization, package
	) c
	ON (a.organization = c.organization AND a.package = c.package)
	INNER JOIN open_source.network_centrality d
	ON (a.organization = d.organization AND a.package = d.package AND a.user_id = d.user_id)
	INNER JOIN open_source.issue_contributors e
	ON (a.package_id = e.package_id AND a.user_id = e.user_id)
) z
