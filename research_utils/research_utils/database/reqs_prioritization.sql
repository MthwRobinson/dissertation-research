DROP MATERIALIZED VIEW open_source.reqs_prioritization;
CREATE MATERIALIZED VIEW open_source.reqs_prioritization
AS
SELECT DISTINCT
	   a.package, a.organization, a.package_id, a.user_id, a.created_at, a.closed_at, a.pull_request, a.labels,
	   EXTRACT(DAYS FROM a.closed_at - a.created_at) as duration,
	   e.commit_pct,
	   b.gini_coefficient, b.avg_clustering, b.avg_min_path,
	   d.betweenness_centrality,
	   c.crowd_pct, c.crowd, c.total
FROM (
	SELECT *
	FROM open_source.issues
	WHERE id IN (SELECT issue_id FROM open_source.issue_contributors)
) a
INNER JOIN open_source.issue_contributors e
ON a.id = e.issue_id
INNER JOIN open_source.crowd_percentage c
ON (a.package_id = c.package_id)
INNER JOIN (
	SELECT organization, package, gini_coefficient, avg_clustering, avg_min_path
	FROM open_source.stakeholder_networks
) b
ON (a.organization = b.organization AND a.package = b.package)
INNER JOIN open_source.network_centrality d
ON (a.organization = d.organization AND a.package = d.package AND a.user_id = d.user_id)

