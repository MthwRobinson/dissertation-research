import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.decomposition import PCA


from research_utils.database.database import Database
from research_utils.analytics.lda import TopicModel

def prep_data():
    database = Database()
    data = pd.read_sql(INPUT_QUERY, database.connection)
    tm = TopicModel(25, load=True)
    df = tm.load_topic_model_results()
    for i in range(tm.num_topics):
        df['topic_{}'.format(i)] = [x[i] if x else np.nan for x in df['topics']]

    all_topics = []
    reg_topics = []
    simple_reg_topics = []
    for i in range(tm.num_topics-1):
        all_topics.append('topic_{}'.format(i))
        simple_reg_topics.append('topic_{}'.format(i))
    for j in range(tm.num_topics-1):
        reg_topics.append("topic_{}*topic_{}".format(i, j))

    mean_topics = df.groupby(['organization', 'package']).mean()[all_topics]

    all_data = mean_topics.merge(data, on=['package', 'organization'])
    all_data['crowd_pct_sq'] = np.sqrt(all_data['crowd_pct'])
    all_data['crowd_pct_2'] = all_data['crowd_pct']**2
    all_data['issues_over_time'] = (all_data['total_issues'] / all_data['project_age'])*90
    all_data['avg_clusteringXcrowd_pct'] = all_data['avg_clustering'] * all_data['crowd_pct']
    all_data['avg_min_pathXcrowd_pct'] = all_data['avg_min_path'] * all_data['crowd_pct']
    all_data['gini_coefficientXcrowd_pct'] = all_data['gini_coefficient'] * all_data['crowd_pct']
    all_data['issues_per_user'] = all_data['total_issues'] / all_data['num_users']
    all_data.to_csv('/home/matt/research_data_25.csv', index=False)
    return all_data

def glm_marginal_effect(variable, res, X, all_data):
    """Computes the GLM marginal effects for the variable.

    Parameters
    ----------
    variable : str
        the variable for which we would like to calculate the marginal effect
    res : sm.model
        results of the linear regression
    X : pd.DataFrame
        the input to the linear regression
    all_data : pd.DataFrame
        the full set of input data

    Returns
    -------
    marginal_effect : float
    """
    data = all_data.copy(deep=True)
    param = res.params[variable]
    cross_term = '{}Xcrowd_pct'.format(variable)
    if cross_term in res.params:
        data['effect'] = param + data['crowd_pct'] * res.params[cross_term]
    else:
        data['effect'] = param
    data['prediction'] = res.predict(X)
    data['marginal_effect'] = data['effect'] * data['prediction']
    return data['marginal_effect'].mean()

def compute_pca(X, n_components=50):
    """Compute principal component analysis only on the topic columns

    Parameters
    ----------
    X : pd.DataFrame
        the dataframe that contains the columns for the regression model
    n_compnents : int
        the number of principal components to retain

    Returns
    -------
    final_df : pd.DataFrame
        the data frame for the linear regression, with the topic columns
        replaced by their principal components
    """
    topic_columns = [x for x in X.columns if 'topic' in x]
    topic_matrix = X[topic_columns]
    pca = PCA(n_components=n_components)
    pca_matrix = pca.fit_transform(topic_matrix)
    pca_df = pd.DataFrame(data = pca_matrix, columns = ['pc_{}'.format(i) for i in range(pca_matrix.shape[1])])
    pca_df['index'] = range(len(pca_df))
    X['index'] = range(len(X))
    final_df = X.merge(pca_df)
    del final_df['index']
    for col in final_df:
        if 'topic' in col:
            del final_df[col]
    return final_df

def calc_total_effect(all_data, res, X, crowd_pct=None, avg_clustering=None,
                      avg_min_path=None, gini_coefficient=None):
    """Calculates the total effect of crowd_pct in the GLM model

    Parameters
    ----------
    all_data : pd.DataFrame
        the input data to the regression model
    res : regression results
        the output of the regression model

    Returns
    -------
    total_effect : float
    """
    effects_data = X.copy(deep=True)

    effects_data['crowd_pct'] = all_data['crowd_pct'] if not crowd_pct else crowd_pct
    effects_data['crowd_pct_2'] = effects_data['crowd_pct']**2

    effects_data['avg_clustering'] = all_data['avg_clustering'] if not avg_clustering else avg_clustering
    effects_data['avg_min_path'] = all_data['avg_min_path'] if not avg_min_path else avg_min_path
    effects_data['gini_coefficient'] = all_data['gini_coefficient'] if not gini_coefficient else gini_coefficient

    effects_data['avg_clusteringXcrowd_pct'] = effects_data['crowd_pct'] * effects_data['avg_clustering']
    effects_data['avg_min_pathXcrowd_pct'] = effects_data['crowd_pct'] * effects_data['avg_min_path']
    effects_data['gini_coefficientXcrowd_pct'] = effects_data['crowd_pct'] * effects_data['gini_coefficient']


    params = {}
    param_vars = ['crowd_pct', 'crowd_pct_2', 'avg_clusteringXcrowd_pct',
                  'avg_min_pathXcrowd_pct', 'gini_coefficientXcrowd_pct']
    for var in param_vars:
        params[var] = 0 if var not in res.params else res.params[var]

    columns = [x for x in res.params.keys()]
    pred_data = effects_data[columns]
    predictions = res.predict(pred_data)

    crowd_pct_2_effect =  predictions * params['crowd_pct_2']
    crowd_pct_param = params['crowd_pct'] + (effects_data['avg_clustering'] * params['avg_clusteringXcrowd_pct']
                       + effects_data['gini_coefficient'] * params['gini_coefficientXcrowd_pct']
                       + effects_data['avg_min_path'] * params['avg_min_pathXcrowd_pct'])

    total_effect = predictions * (2 * params['crowd_pct_2'] * effects_data['crowd_pct'] + crowd_pct_param)
    avg_effect = total_effect.mean()
    return avg_effect

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
       a.duration_median, a.duration_mean, a.duration_variance, a.project_age, a.under_30, a.under_60, a.under_90, a.num_users,
       b.crowd_pct, b.crowd, b.total as total_issues,
       c.gini_coefficient, c.avg_clustering, c.avg_min_path, c.max_gini, c.nodes,
       d.total_contributors, e.diversity_10, e.diversity_25, e.diversity_50, e.diversity_100,
       e.distributed, e.one_center, e.two_centers, e.multiple_centers, e.other,
       f.avg_comments, f.avg_first_comment, f.avg_active_time
FROM(
    SELECT package_id, package, organization,
           PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY duration) AS duration_median,
           AVG(duration) AS duration_mean,
           VARIANCE(duration) AS duration_variance,
           EXTRACT(DAY FROM NOW() - MIN(created_at)) AS project_age,
           SUM(CASE WHEN duration < 30 THEN 1 ELSE 0 END) as under_30,
           SUM(CASE WHEN duration < 60 THEN 1 ELSE 0 END) as under_60,
           SUM(CASE WHEN duration < 90 THEN 1 ELSE 0 END) as under_90,
           COUNT(DISTINCT user_id) AS num_users
    FROM(
        SELECT package_id, organization, package, created_at, user_id,
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
    SELECT organization, package, gini_coefficient, avg_clustering,
           avg_min_path, crowd_pct, max_gini, nodes
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
    SELECT AVG(num_comments) as avg_comments,
           AVG(first_comment_time) as avg_first_comment,
           AVG(active_time) as avg_active_time,
           package, organization
    FROM (
        SELECT COUNT(DISTINCT comment_id) as num_comments, issue_id, package, organization,
               EXTRACT(DAY FROM MIN(comment_time) - MAX(issue_time)) AS first_comment_time,
               EXTRACT(DAY FROM MAX(comment_time) - MIN(comment_time)) AS active_time
        FROM open_source.issue_comments
        GROUP BY issue_id, package, organization
    ) x
    GROUP BY package, organization
) f
ON (a.package = f.package AND a.organization = f.organization)
"""
