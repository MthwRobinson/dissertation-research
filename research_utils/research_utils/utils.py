import pandas as pd
import statsmodels.api as sm

def build_crowd_pct_variation(all_data, X):
    """Used to created an input data set that holds all variables
    at their average value except for crowd_pct, which is varied.
    Used to show the marginal effect of crowd_pct

    Parameters
    ----------
    all_data : pd.DataFrame
        this is the full set of input data for the models
    X : pd.DataFrame
        this is the input data set specific to the model
        whose marginal effects we are trying ot determine

    Returns
    -------
    crowd_pct_variation : pd.DataFrame
        a dataframe that has the input data with crowd_pct
        varied from 0 to 0.99
    """
    mean_values = all_data.mean()
    data = {x: [] for x in X.columns}
    for i in range(100):
        crowd_pct = float(i/100)
        for field in data:
            if field == 'Intercept':
                data[field].append(1)
            elif 'crowd_pct' not in field:
                if ':' in field:
                    fields = field.split(':')
                    data[field].append(mean_values[fields[0]]*
                                       mean_values[fields[1]])
                else:
                    data[field].append(mean_values[field])
            elif field == 'crowd_pct':
                data[field].append(crowd_pct)
            elif field == 'crowd_pct_2':
                data[field].append(crowd_pct**2)
            elif 'X' in field and 'crowd_pct' in field:
                fields = field.split('X')
                data[field].append(crowd_pct * mean_values[fields[0]])
    crowd_pct_variation = pd.DataFrame(data)
    return crowd_pct_variation


def select_features(X, y, threshold, model_type='ols'):
    """Performs feature selection for the specified model.

    Parameters
    ----------
    X : pd.DataFrame
        the input data
    y : pd.DataFrame
        the response variable
    threshold : float
        the p-value threshold for including variables.
        needs to be between 0 and 1
    model_type : str
        the type of regression. options are 'ols', 'poisson',
        'negative_binomial' and 'gamma'

    Returns
    -------
    features : list
        a list of features to retain in the model
    """
    cols = list(X.columns)
    pmax = 1
    while (len(cols)>0):
        p= []
        X_1 = X[cols]
        if model_type == 'ols':
            model = sm.OLS(y,X_1).fit()
        elif model_type == 'poisson':
            model = sm.GLM(y, X_1, family=sm.families.Poisson()).fit()
        elif model_type == 'negative_binomial':
            model = sm.GLM(y, X_1, family=sm.families.NegativeBinomial()).fit()
        elif model_type == 'gamma':
            model = sm.GLM(y, X_1, family=sm.families.Gamma(link=sm.families.links.log)).fit()
        p = pd.Series(model.pvalues.values,index = cols)
        pmax = max(p)
        feature_with_p_max = p.idxmax()
        if(pmax>threshold):
            cols.remove(feature_with_p_max)
        else:
            break
    features = ' + '.join(cols[1:])
    return features

INPUT_QUERY = """
SELECT a.package_id, a.package, a.organization,
       a.duration_median, a.duration_mean, a.duration_variance, a.project_age, a.under_30, a.under_60, a.under_90,
       b.crowd_pct, b.crowd, b.total as total_issues,
       c.gini_coefficient, c.avg_clustering, c.avg_min_path,
       d.total_contributors, e.diversity_10, e.diversity_25, e.diversity_50, e.diversity_100,
       e.distributed, e.one_center, e.two_centers, e.multiple_centers, e.other,
       f.avg_comments, f.avg_first_comment
FROM(
    SELECT package_id, package, organization,
           PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY duration) AS duration_median,
           AVG(duration) AS duration_mean,
           VARIANCE(duration) AS duration_variance,
           EXTRACT(DAY FROM NOW() - MIN(created_at)) AS project_age,
           SUM(CASE WHEN duration < 30 THEN 1 ELSE 0 END) as under_30,
           SUM(CASE WHEN duration < 60 THEN 1 ELSE 0 END) as under_60,
           SUM(CASE WHEN duration < 90 THEN 1 ELSE 0 END) as under_90
    FROM(
        SELECT package_id, organization, package, created_at,
               EXTRACT(DAY FROM closed_at - created_at) as duration
               FROM open_source.issues
               WHERE closed_at IS NOT NULL AND pull_request IS FALSE
               AND created_at < '2019-01-01'
                AND ('bug' = ANY(lower(labels::text)::text[])
                OR 'feature' = ANY(lower(labels::text)::text[])
            OR 'feature request' = ANY(lower(labels::text)::text[])
            OR 'change' = ANY(lower(labels::text)::text[])
            OR 'suggestion' = ANY(lower(labels::text)::text[])
            OR 'enhancement' = ANY(lower(labels::text)::text[]))

    ) z
    GROUP BY package_id, organization, package
) a
INNER JOIN open_source.crowd_percentage b
ON a.package_id = b.package_id
INNER JOIN (
    SELECT organization, package, gini_coefficient, avg_clustering, avg_min_path, crowd_pct
    FROM open_source.stakeholder_networks
) c
ON (a.package = c.package AND a.organization = c.organization)
INNER JOIN (
    SELECT COUNT(DISTINCT user_id) as total_contributors, package_id
    FROM open_source.issue_contributors
    WHERE commit_pct > 0
    GROUP BY package_id
) d
ON a.package_id = d.package_id
INNER JOIN open_source.packages e
ON a.package_id = e.id
INNER JOIN (
    SELECT AVG(num_comments) as avg_comments, AVG(first_comment_time) as avg_first_comment,
           package, organization
    FROM (
        SELECT COUNT(DISTINCT comment_id) as num_comments, issue_id, package, organization,
               EXTRACT(DAY FROM MIN(comment_time) - MAX(issue_time)) AS first_comment_time
        FROM open_source.issue_comments
        GROUP BY issue_id, package, organization
    ) x
    GROUP BY package, organization
) f
ON (a.package = f.package AND a.organization = f.organization)
"""
