""" Connects to the Postgres database """
from copy import deepcopy
import json
import logging
import os

import daiquiri
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

class Database(object):
    """
    Connects to the Postgres database
    Connection settings appear in configuration.py
    Secrets must be stored in a .pgpass file
    """
    def __init__(self):
        # Configure the logger
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        # Find the path to the file
        self.path = os.path.dirname(os.path.realpath(__file__))

        # Database connection and configurations
        self.columns = {}
        self.schema = 'open_source'
        self.database = 'postgres'
        self.connection = psycopg2.connect(user = 'postgres',
                                           dbname = 'postgres',
                                           host = 'localhost')

    def run_query(self, sql, commit=True):
        """ Runs a query against the postgres database """
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
        if commit:
            self.connection.commit()

    def initialize(self):
        """ Creates the tables for the dissertation.  """
        filename = self.path + '/tables.sql'
        with open(filename, 'r') as f:
            sql = f.read().format(schema=self.schema)
        self.run_query(sql)

    def backup_table(self, table):
        """ Creates a backup of the specified table """
        sql = """
            DROP TABLE IF EXISTS {schema}.{table}_backup;
            CREATE TABLE {schema}.{table}_backup
            AS SELECT *
            FROM {schema}.{table}
        """.format(schema=self.schema, table=table)
        self.run_query(sql)

    def revert_table(self, table):
        """ Reverts a table to the backup """
        sql = """
            DROP TABLE IF EXISTS {schema}.{table};
            CREATE TABLE {schema}.{table}
            AS SELECT *
            FROM {schema}.{table}
        """.format(schema=self.schema, table=table)
        self.run_query(sql)

    def truncate_table(self, table):
        """ Truncates a table """
        sql = "TRUNCATE %s.%s"%(self.schema, table)
        self.run_query(sql)

    def get_columns(self, table):
        """ Pulls the column names for a table """
        sql = """
            SELECT DISTINCT column_name
            FROM information_schema.columns
            WHERE table_schema='{schema}'
            AND table_name='{table}'
        """.format(schema=self.schema, table=table)
        df = pd.read_sql(sql, self.connection)
        columns = [x for x in df['column_name']]
        return columns

    def load_item(self, item, table):
        """ Load items from a dictionary into a Postgres table """
        # Find the columns for the table
        if table not in self.columns:
            self.columns[table] = self.get_columns(table)
        columns = self.columns[table]

        # Determine which columns in the item are valid
        item_ = deepcopy(item)
        for key in item:
            if key not in columns:
                del item_[key]

        # Construct the insert statement
        n = len(item_)
        row = "(" + ', '.join(['%s' for i in range(n)]) + ")"
        cols = "(" + ', '.join([x for x in item_]) + ")"
        sql = """
            INSERT INTO {schema}.{table}
            {cols}
            VALUES
            {row}
        """.format(schema=self.schema, table=table, cols=cols, row=row)

        # Insert the data
        values = tuple([item_[x] for x in item_])
        with self.connection.cursor() as cursor:
            cursor.execute(sql, values)
        self.connection.commit()

    def load_items(self, items, table):
        """
        Loads a list of items into the database
        This is faster than running load_item in a loop
        because it reduces the number of server calls
        """
        # Find the columns for the table
        if table not in self.columns:
            self.columns[table] = self.get_columns(table)
        columns = self.columns[table]

        # Determine which columns in the item are valid
        item_ = deepcopy(items[0])
        for key in items[0]:
            if key not in columns:
                del item_[key]

        # Construct the insert statement
        n = len(item_)
        cols = "(" + ', '.join([x for x in item_]) + ")"
        sql = """
            INSERT INTO {schema}.{table}
            {cols}
            VALUES
            %s
        """.format(schema=self.schema, table=table, cols=cols)

        # Insert the data
        all_values = []
        for item in items:
            item_ = deepcopy(item)
            for key in item:
                if key not in columns:
                    del item_[key]
            values = tuple([item_[x] for x in item_])
            all_values.append(values)

        with self.connection.cursor() as cursor:
            execute_values(cursor, sql, all_values)
        self.connection.commit()

    def delete_item(self, table, item_id, secondary=None):
        """ Deletes an item from a table """
        sql = "DELETE FROM {schema}.{table} WHERE id='{item_id}'".format(
            schema=self.schema,
            table=table,
            item_id=item_id
        )
        if secondary:
            for key in secondary:
                sql += " AND %s='%s'"%(key, secondary[key])
        self.run_query(sql)

    def get_item(self, table, item_id, secondary=None):
        """ Fetches an item from the database """
        sql = "SELECT * FROM {schema}.{table} WHERE id='{item_id}'".format(
            schema=self.schema,
            table=table,
            item_id=item_id
        )
        df = pd.read_sql(sql, self.connection)
        if secondary:
            for key in secondary:
                sql += " AND %s='%s'"%(key, secondary[key])

        if len(df) > 0:
            return dict(df.loc[0])
        else:
            return None

    def update_column(self, table, item_id, column, value):
        """ Updates the value of the specified column """
        sql = """
            UPDATE {schema}.{table}
            SET {column} = %s
            WHERE id = '{item_id}'
        """.format(schema=self.schema, table=table,
                   column=column, item_id=item_id)

        with self.connection.cursor() as cursor:
            cursor.execute(sql, (value,))
        self.connection.commit()

    def read_table(self, table, columns=None, sort=None, order='desc',
        limit=None, page=None, query=[], where=[], count=False):
        """ Reads a table into a dataframe.

        Parameters
        ----------
            table: string, the name of table in the database
            columns: list[string], which columns we want to pull
            sort: string, the column to sort by
            order: 'asc' or 'desc', the sort order
            limit: int, the number of rows to return
            page: int, which page of results we want (determined
                by the limit)
            query: list of tuples, the first element in the tuple
                is the field to search over and the second element
                is the search term
            where: list of tuples, the first element is the field
                the condition applies to and the second element
                is the condition. the condtions have the form
                options for the condition are '<=', '<', '=',
                '>', '>='
                (ex. [('start_datetime, {'leq': '2018-01-01'})])
            count: bool, if true, returns the count of the query
                rather than a results table

        Returns
        -------
            a dataframe with the results of the query

        """
        if not columns:
            cols = '*'
        else:
            cols = ', '.join(columns)
        sql = """
            SELECT {cols}
            FROM {schema}.{table}
        """.format(cols=cols, schema=self.schema, table=table)
        if query or where:
            clauses = _build_query_clauses(query)
            clauses += _build_where_conditions(where)
            sql += " WHERE " + " AND ".join(clauses)
        if sort:
            sql += " ORDER BY %s %s NULLS LAST "%(sort, order)
        if limit:
            sql += " LIMIT %s "%(limit)
        if page and limit:
            offset = (page-1)*limit
            sql += " OFFSET %s "%(offset)
        if count:
            count_sql = """
                SELECT COUNT(*) as count
                FROM ({sql}) x
            """.format(sql=sql)
            df = pd.read_sql(count_sql, self.connection)
            return df.loc[0]['count']
        else:
            df = pd.read_sql(sql, self.connection)
            return df

    def count_rows(self, table, query=[], where=[]):
        """ Returns the number of rows, given a query. """
        count = self.read_table(table=table, query=query,
                                where=where, count=True)
        return count

    def to_json(self, df):
        """ Converts a dataframe to a json list """
        return [json.loads(df.loc[i].to_json()) for i in df.index]

    def fetch_list(self, sql):
        """ Returns a sql query as a jsonfied list """
        df = pd.read_sql(sql, self.connection)
        results = self.to_json(df)
        response = {'results': results}
        return response

def _build_query_clauses(query=None):
    """  Builds query conditions for the read_table method

    Parameters
    ----------
        query: list of tuples, the first element in the tuple
            is the field to search over and the second element
            is the search term

    Returns
    -------
        list, a list of SQL clauses
    """
    clauses = []
    # Add the conditions from the search term
    if query:
        query_conditions = []
        field = query[0]
        search_terms = query[1].split()
        for term in search_terms:
            search = " lower(%s) like lower('%s%s%s') "%(
                field,
                '%', term, '%'
            )
            query_conditions.append(search)
        query_clause = " AND ".join(query_conditions)
        clauses.append("({})".format(query_clause))
    return clauses

def _build_where_conditions(where):
    """ Builds where conditions for the read_table method

    Parameters
    ----------
        where: list of tuples, the first element is the field
            the condition applies to and the second element
            is the condition. the condtions have the form
            options for the condition are '<=', '<', '=',
            '>', '>='
            (ex. [('start_datetime, {'leq': '2018-01-01'})])

    Returns
    -------
        list, a list of SQL clauses
    """
    where_conditions = []
    for item in where:
        column = item[0]
        conditions = item[1]
        for equality in conditions:
            value = conditions[equality]
            condition = " {col} {equality} {value} ".format(
                col=column,
                equality=equality,
                value=value
            )
            where_conditions.append(condition)
    return where_conditions
