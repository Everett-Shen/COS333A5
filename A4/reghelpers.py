#!/usr/bin/env python

# ----------------------------------------------------------------------
# reghelpers.py
# Author: Everett Shen, Trivan Menezes
# ----------------------------------------------------------------------

from sys import argv, stderr
from contextlib import closing
from sqlite3 import connect, Error

# ----------------------------------------------------------------------

DATABASE_URL = 'file:reg.sqlite?mode=ro'

def format_row(row):
    output = '{0:>5d}  {1:>3s}   {2:>4s}  {3:>3s} {4}'.format(
        row[0], row[1], row[2], row[3], row[4])
    return output

# prepared_args is an array of arguments for the prepared statement
# returns a list of unsorted rows

# returns a tuple with (False, exception) if something fails
def select_from_table(stmt_str, prepared_args):
    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                to_return = []
                cursor.execute(stmt_str, prepared_args)

                row = cursor.fetchone()
                while row is not None:

                    to_return.append(row)
                    row = cursor.fetchone()

                return to_return

    except Error as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        return (False,
            "A server error occurred. Please \
                contact the system administrator.")

def row_array_to_string(row_array):
    to_return = ""
    for row in row_array:
        to_return += format_row(row)
        to_return += "\n"
    return to_return.rstrip("\n")

def get_table_results(stmt_str, prepared_args):

    rows = select_from_table(stmt_str, prepared_args)
    # checks for error state
    if isinstance(rows, tuple):
        return rows
    rows.sort(key=lambda x: x[2])
    rows.sort(key=lambda x: x[1])
    return rows

BASE_STMT_STR = '''SELECT classes.classid, crosslistings.dept,
    crosslistings.coursenum, courses.area, courses.title 
    FROM classes, crosslistings, courses  
    WHERE classes.courseid = crosslistings.courseid 
    AND classes.courseid = courses.courseid '''
LIKE_STATEMENT_STRING = " LIKE ? ESCAPE \'\\\'"

# appends to prepared_args in place,
# returns string to add to stmt_str
def update_statement(and_stmt, searchstring, prepared_args):

    def format_searchstring(searchstring):
        # convert to lower case
        searchstring = searchstring.lower()
        # escape regex characters
        searchstring = searchstring.replace("%", r"\%")
        searchstring = searchstring.replace("_", r"\_")
        # sandwich with percent signs (for regex)
        return '%{}%'.format(searchstring)

    prepared_args.append(format_searchstring(searchstring))
    return and_stmt + LIKE_STATEMENT_STRING

def get_results_from_query(query):
    stmt_str = BASE_STMT_STR
    prepared_args = []
    if query["d"]:
        stmt_str += update_statement(
            "AND lower(crosslistings.dept)",
                query["d"], prepared_args)
    if query["n"]:
        stmt_str += update_statement(
            "AND lower(crosslistings.coursenum)",
                query["n"], prepared_args)
    if query["a"]:
        stmt_str += update_statement(
            "AND lower(courses.area)",
                query["a"], prepared_args)
    if query["t"]:
        stmt_str += update_statement(
            "AND lower(courses.title)",
                query["t"], prepared_args)

    return get_table_results(stmt_str, prepared_args)
