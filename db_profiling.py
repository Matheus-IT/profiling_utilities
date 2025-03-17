from django.db import connection, reset_queries
import functools


class HowManyQueries:
    """
    Utility to be used as a context manager to calculate how many queries are
    been made in a code block
    """

    def __init__(self, show_queries=False, *args, **kwargs):
        self.show_queries = show_queries

    def __enter__(self):
        reset_queries()  # Reset previous queries to measure just the block
        return super().__enter__() if hasattr(super(), '__enter__') else self

    def __exit__(self, exc_type, exc_value, exc_tb):
        num_of_queries = len(connection.queries)
        print('-'*50)
        print(f'In this block were made {num_of_queries} queries')
        print('-'*50)
        if self.show_queries:
            for q in connection.queries:
                _print_query(q)
                print('-'*50)
        super().__exit__(exc_type, exc_value, exc_tb) if hasattr(super(), '__exit__') else None


def how_many_queries(func):
    """Utility to calculate number of db queries as a decorator"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()  # Reset previous queries to measure just the block
        show_queries = kwargs.pop('show_queries')
        value = func(*args, **kwargs)
        num_of_queries = len(connection.queries)

        print('-'*50)
        print(f'In this block were made {num_of_queries} queries')
        print('-'*50)
        if show_queries:
            for q in connection.queries:
                _print_query(q)
                print('-'*50)
        return value
    return wrapper


def _print_query(query):
    """Print the query in a beautified format"""
    query_sql = query.get('sql', '')
    formatted_query = format_sql(query_sql)
    highlighted_query = highlight_sql_keywords(formatted_query)
    print(highlighted_query)
    print('Time:', query['time'])

def format_sql(sql):
    """Format SQL query using sqlparse"""
    import sqlparse
    return sqlparse.format(sql, reindent=True, keyword_case='upper')

def highlight_sql_keywords(sql):
    import re
    """Highlight SQL keywords in the query"""
    keywords = ["SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN", "ORDER BY", "GROUP BY", "LIMIT"]
    for keyword in keywords:
        sql = re.sub(rf'\b{keyword}\b', f'\033[1;32m{keyword}\033[0m', sql, flags=re.IGNORECASE)
    return sql


import json
from contextlib import contextmanager


class ExplainResult(Exception):
    pass


def explain_hook(execute, sql, params, many, context):
    sql = "EXPLAIN (ANALYZE, FORMAT JSON, BUFFERS, VERBOSE, SETTINGS, WAL) " + sql
    execute(sql, params, many, context)
    result = context["cursor"].fetchone()[0]
    raise ExplainResult(result)


@contextmanager
def explain():
    try:
        with connection.execute_wrapper(explain_hook):
            yield
    except ExplainResult as exc:
        print(json.dumps(exc.args[0]))