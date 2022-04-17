#!/usr/bin/env python

# ----------------------------------------------------------------------
# regserver.py
# Author: Everett Shen, Trivan Menezes
# ----------------------------------------------------------------------

from sys import stderr, exit
import argparse
from os import name
from time import process_time
from multiprocessing import Process
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from pickle import dump, load
from reghelpers import get_results_from_query as get_overview
from regdetails import get_table_results

# ----------------------------------------------------------------------
def consume_cpu_time(delay):

    i = 0
    initial_time = process_time()
    while (process_time() - initial_time) < delay:
        i += 1  # Do a nonsensical computation.

# sends (True, results) if succceeds, (False, err_message) if fails
def handle_client(sock, delay):
    print('Forked child process')
    consume_cpu_time(delay)
    in_flo = sock.makefile(mode='rb')
    query = load(in_flo)
    # get_detail
    if "class_id" in query:
        print("Received command: get_detail")
        to_return = get_table_results(query["class_id"])
    # get_overviews
    else:
        print("Received command: get_overviews")
        to_return = get_overview(query)

    # if request was successful, turn it into a tuple
    # (if it failed, it is already a tuple)
    if not isinstance(to_return, tuple):
        to_return = (True, to_return)

    out_flo = sock.makefile(mode='wb')
    dump(to_return, out_flo)
    out_flo.flush()
    print('Closed socket in child process')


def main():

    parser = argparse.ArgumentParser(
        description='Server for the registrar application',
        allow_abbrev=False)

    parser.add_argument('port', type=int,
        help='the port at which the server should listen')

    parser.add_argument('delay', type=int,
        help='''the number of seconds that the server should delay
        before responding to each client request''')

    args = parser.parse_args()

    try:
        port = args.port
        delay = args.delay
        #IMPLEMENT BUSY WAIT
        server_sock = socket()
        print('Opened server socket')
        if name != 'nt':
            server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_sock.bind(('', port))
        print('Bound server socket to port')
        server_sock.listen()
        print('Listening')
        while True:
            try:
                sock, _ = server_sock.accept()
                with sock:
                    print('Accepted connection, opened socket')
                    process = Process(target=handle_client,
                        args=[sock, delay])
                    process.start()
                    # handle_client(sock, delay)
                    # print('Closed socket')
            except Exception as ex:
                print(ex, file=stderr)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == '__main__':
    main()
