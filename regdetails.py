#!/usr/bin/env python

# ----------------------------------------------------------------------
# regdetails.py
# Author: Everett Shen, Trivan Menezes
# ----------------------------------------------------------------------

from sys import argv, stderr
import textwrap
from collections import namedtuple
from reghelpers import select_from_table

# ----------------------------------------------------------------------

BASE_STMT_STR = '''SELECT classes.courseid, classes.days,
    classes.starttime, classes.endtime, classes.bldg,
    classes.roomnum, courses.area, courses.title, courses.descrip,
    courses.prereqs
    FROM classes, crosslistings, courses
    WHERE classes.classid = ?
    AND classes.courseid = crosslistings.courseid 
    AND classes.courseid = courses.courseid'''

DEPT_STMT_STR = '''SELECT crosslistings.dept, crosslistings.coursenum
    FROM classes, crosslistings
    WHERE classes.classid = ?
    AND crosslistings.courseid = classes.courseid'''

PROF_STMT_STR = '''SELECT profname FROM classes, coursesprofs, profs
    WHERE classes.classid = ?
    AND classes.courseid = coursesprofs.courseid
    AND coursesprofs.profid = profs.profid'''

# dept, coursenum, and profnames are arrays

def format_details(baserows, deptdata, profnames):
    wrapper = textwrap.TextWrapper(
        width=72, replace_whitespace=False)

    # use named tuple to avoid pylint "too many local vars" warning
    BaseRowNamedTuple = namedtuple('BaseRowNamedTuple',
    'courseid days starttime endtime bldg \
    roomnum area title descrip prereqs')
    named_base_row = BaseRowNamedTuple(*baserows)

    to_return = ""
    to_return += "{}: {}\n\n".format("Course Id",
        named_base_row.courseid)
    to_return += "{}: {}\n".format("Days", named_base_row.days)
    to_return += "{}: {}\n".format("Start time",
        named_base_row.starttime)
    to_return += "{}: {}\n".format("End time", named_base_row.endtime)
    to_return += "{}: {}\n".format("Building", named_base_row.bldg)
    to_return += "{}: {}\n\n".format("Room", named_base_row.roomnum)

    for (i, _) in enumerate(deptdata):
        to_return += "{}: {} {}\n".format("Dept and Number",
            deptdata[i][0], deptdata[i][1])

    to_return += "\n{}: {}\n\n".format("Area", named_base_row.area)
    to_return += '\n'.join(
        wrapper.wrap(text="{}: {}\n\n".format("Title",
            named_base_row.title)))
    to_return += '\n\n'
    to_return += '\n'.join(
        wrapper.wrap(text="{}: {}\n\n".format("Description",
            named_base_row.descrip)))
    to_return += '\n\n'
    to_return += '\n'.join(
        wrapper.wrap(text="{}: {}\n".format("Prerequisites",
            named_base_row.prereqs)))
    to_return += '\n'

    for professor in profnames:
        to_return += "\n{}: {}".format("Professor", professor[0])

    to_return += '\n'
    return to_return


def get_table_results(classid):
    base_rows = select_from_table(BASE_STMT_STR, [classid])
    # determines if an error happened (check first here so we don't
    # print error message 3 times)
    for row in [base_rows]:
        if isinstance(row, tuple):
            return row
    dept_rows = select_from_table(DEPT_STMT_STR, [classid])
    prof_rows = select_from_table(PROF_STMT_STR, [classid])

    # determines if an error happened
    for row in [dept_rows, prof_rows]:
        if isinstance(row, tuple):
            return row

    # check size of base_rows
    if len(base_rows) == 0:
        print('{}: no class with classid {} exists'.format(
            argv[0], classid), file=stderr)
        return (False,
            "No class with class id {} exists".format(classid))

    base_rows = base_rows[0]

    dept_rows.sort(key=lambda x: x[1])
    dept_rows.sort(key=lambda x: x[0])

    prof_rows.sort(key=lambda x: x[0])

    to_return = ""
    to_return += format_details(
        base_rows,
        dept_rows,
        prof_rows
    )

    return to_return
