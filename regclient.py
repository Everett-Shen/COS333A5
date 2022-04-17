#!/usr/bin/env python

#-----------------------------------------------------------------------
# regclient.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

from sys import exit, argv, stderr
from socket import socket
from pickle import dump, load

#-----------------------------------------------------------------------

def call_server(host, port, query):
  
    try:
        with socket() as sock:

            sock.connect((host, port))

            out_flo = sock.makefile(mode='wb')
            dump(query, out_flo)
            out_flo.flush()

            in_flo = sock.makefile(mode='rb')
            result = load(in_flo)

        if result == '':
            print('The reg server crashed', file=stderr)
        else:
            print(result, end='')

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
        
def main():

    if len(argv) != 3:
        print('Usage: python %s host port' % argv[0])
        exit(1)

    host = argv[1]
    port = int(argv[2])
    query={"class_id": 2}

    call_server(host, port, query)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
