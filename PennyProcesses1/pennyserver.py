#!/usr/bin/env python

#-----------------------------------------------------------------------
# pennyserver.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

from os import name
from sys import exit, argv, stderr
from socket import socket
from socket import SOL_SOCKET, SO_REUSEADDR
from pickle import load, dump
from time import process_time
from database import search

#-----------------------------------------------------------------------

def consume_cpu_time(delay):

    i = 0
    initial_time = process_time()
    while (process_time() - initial_time) < delay:
        i += 1  # Do a nonsensical computation.

#-----------------------------------------------------------------------

def handle_client(sock, delay):

    in_flo = sock.makefile(mode='rb')
    author = load(in_flo)
    print('Received author: ' + author)

    # Consume delay seconds of CPU time.
    consume_cpu_time(delay)

    if author.strip() == '':
        books = []
    else:
        books = search(author)  # Exception handling omitted

    out_flo = sock.makefile(mode='wb')
    dump(books, out_flo)
    out_flo.flush()

#-----------------------------------------------------------------------

def main():

    if len(argv) != 3:
        print('Usage: python %s port delay' % argv[0], file=stderr)
        exit(1)

    try:
        port = int(argv[1])
        delay = int(argv[2])

        server_sock = socket()
        if name != 'nt':
            server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        print('Opened server socket')
        server_sock.bind(('', port))
        print('Bound server socket to port')
        server_sock.listen()
        print('Listening')

        while True:
            try:
                sock, address = server_sock.accept()
                with sock:
                    print('Accepted connection at ' + str(address))
                    print('Opened socket')
                    handle_client(sock, delay)
            except Exception as ex:
                print(ex, file=stderr)

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
