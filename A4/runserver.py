#!/usr/bin/env python

#-----------------------------------------------------------------------
# runserver.py
# Author: Everett Shen, Trivan Menezes
#-----------------------------------------------------------------------

from sys import exit, stderr
import argparse
from reg import app

def main():

    parser = argparse.ArgumentParser(
        description='Server for the registrar application',
        allow_abbrev=False)

    parser.add_argument('port', type=int,
        help='the port at which the server should listen')

    args = parser.parse_args()

    port = args.port

    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == '__main__':
    main()
