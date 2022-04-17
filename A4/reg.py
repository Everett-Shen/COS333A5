#!/usr/bin/env python

#-----------------------------------------------------------------------
# reg.py
# Author: Everett Shen, Trivan Menezes
#-----------------------------------------------------------------------

from flask import Flask, request, make_response, render_template
from reghelpers import get_results_from_query as get_overview
from regdetails import get_table_results

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')

#-----------------------------------------------------------------------

HEADER = '''
            <tr>
                <th>ClassId</th>
                <th>Dept</th>
                <th>Num</th>
                <th>Area</th>
                <th align="left">Title</th>
            </tr>
    '''
PATTERN = '''
            <tr>
                <td>
                    <a href="regdetails?classid={}" target="_blank">{}
                    </a>
                </td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>
    '''

#-----------------------------------------------------------------------

# landing page
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    html = render_template('index.html')
    response = make_response(html)
    return response

# search results route - return HTML fragment for class data from query
@app.route('/searchresults', methods=['GET'])
def search_results():
    # convert arguments in URL to query for database
    query = {}
    abbreviations=["d","n","a","t"]
    for i, value in enumerate(["dept","coursenum","area","title"]):
        curr_val = request.args.get(value)
        if curr_val:
            query[abbreviations[i]] = request.args.get(value)
        else:
            query[abbreviations[i]] = ""
    error_msg = ''
    # query database and handle data
    classes = get_overview(query)
    if isinstance(classes, tuple):
        _, error_msg = classes

    # construct HTML to return
    html = ''
    # handle error message
    if error_msg != '':
        html += '<p>{}</p>'.format(error_msg)
    # return rows data about classes
    else:
        html += '<tbody>'
        html += HEADER

        for entry in classes:
            html += PATTERN.format(
                entry[0],
                entry[0],
                entry[1],
                entry[2],
                entry[3],
                entry[4])
        html += '</tbody>'

    response = make_response(html)
    return response

# regdetails route - opens on new page and shows to the user the
# details about a class
@app.route('/regdetails', methods=['GET'])
def regdetails():
    # handle error message
    error_msg = ''
    #check if classid exists
    classid=request.args.get("classid")
    if not classid:
        error_msg = "missing classid"
        class_details=""
    elif not classid.isdigit():
        error_msg = "non-integer classid"
        class_details=""
    else:
        class_details = get_table_results(classid)
        if isinstance(class_details, tuple):
            _, error_msg = class_details
    # return HTML template with details data
    html = render_template('regdetails.html',
        error_msg=error_msg,
        classid=request.args.get("classid"),
        class_details=class_details)
    response = make_response(html)
    return response
    