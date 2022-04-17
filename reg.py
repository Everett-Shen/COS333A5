#!/usr/bin/env python

# ----------------------------------------------------------------------
# reg.py
# Author: Everett Shen, Trivan Menezes
# ----------------------------------------------------------------------

from sys import exit, argv, stderr
import argparse
from socket import socket
from pickle import dump, load
from threading import Thread
from queue import Queue, Empty
from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QMainWindow
from PyQt5.QtWidgets import QGridLayout, QDesktopWidget, QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# ----------------------------------------------------------------------
# INIT GUI

# validate arguments to main


def validate_args(args):
    if isinstance(args.port, int):
        print('Port number is not an integer', file=stderr)


# initialize the labels to be displayed in the GUI
def init_labels(labels_layout):
    labels_list = []

    dept_label = QLabel('Dept:')
    dept_label.setAlignment(Qt.AlignRight)
    labels_list.append(dept_label)

    number_label = QLabel('Number:')
    number_label.setAlignment(Qt.AlignRight)
    labels_list.append(number_label)

    area_label = QLabel('Area:')
    area_label.setAlignment(Qt.AlignRight)
    labels_list.append(area_label)

    title_label = QLabel('Title:')
    title_label.setAlignment(Qt.AlignRight)
    labels_list.append(title_label)

    labels_layout.addWidget(dept_label)
    labels_layout.addWidget(number_label)
    labels_layout.addWidget(area_label)
    labels_layout.addWidget(title_label)

    return labels_layout


# initialize line edit elements
def init_line_edits(line_edit_layout):
    dept_edit = QLineEdit()
    number_edit = QLineEdit()
    area_edit = QLineEdit()
    title_edit = QLineEdit()

    line_edit_layout.addWidget(dept_edit)
    line_edit_layout.addWidget(number_edit)
    line_edit_layout.addWidget(area_edit)
    line_edit_layout.addWidget(title_edit)

    # return tuple of line edits
    return (dept_edit, number_edit, area_edit, title_edit)


# initialize the GUI elements
def init_gui(args, queue):
    # layouts
    top_layout = QHBoxLayout()
    top_layout.setContentsMargins(10, 20, 10, 0)

    labels_layout = QVBoxLayout()
    line_edit_layout = QVBoxLayout()

    top_layout.addLayout(labels_layout)
    top_layout.addLayout(line_edit_layout)

    labels_layout = init_labels(labels_layout)
    dept_edit, number_edit, area_edit, title_edit = init_line_edits(
        line_edit_layout)

    # slot to handle when submit button is clicked. Calls
    # server to query appropriate data
    def submit_slot():
        query = {
            'd': dept_edit.text(),
            'n': number_edit.text(),
            'a': area_edit.text(),
            't': title_edit.text()
        }
        # send to server
        call_server_update_data(query, False, args, queue)

    # slot to hangle when a class' cell is highlighted. Calls server to
    # query appropriate data
    def class_select_slot(list_widget_item):
        list_widget_row = list_widget_item.text().split(' ')
        classid = ''
        for item in list_widget_row:
            if item != '':
                classid = item
                break

        query = {
            'class_id': classid
        }
        # send to server
        if len(list_widget_row) > 1:
            call_server_update_data(query, True, args, queue)

    # slots to handle events
    dept_edit.textChanged.connect(submit_slot)
    number_edit.textChanged.connect(submit_slot)
    area_edit.textChanged.connect(submit_slot)
    title_edit.textChanged.connect(submit_slot)

    list_view = QListWidget()
    # slots to handle signals
    list_view.itemActivated.connect(class_select_slot)

    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addLayout(top_layout, 0, 0)
    layout.addWidget(list_view, 1, 0)

    # load initial data
    call_server_update_data({
        'd': dept_edit.text(),
        'n': number_edit.text(),
        'a': area_edit.text(),
        't': title_edit.text()
    },
        False, args, queue)

    # returns tuple of GUI elements
    return layout, list_view

# --------------------------------------------------------------------
# THREAD HANDLING CODE

# WorkerThread class - takes in params for call to server and makes
# request on new thread
class WorkerThread (Thread):

    def __init__(self, host_details, query, is_class_details, queue):
        Thread.__init__(self)
        host, port = host_details
        self._host = host
        self._port = port
        self._query = query
        self._queue = queue
        self._is_class_details = is_class_details

    def run(self):
        result = (0, 'Unsuccessful Query')
        try:
            with socket() as sock:
                sock.connect((self._host, self._port))
                out_flo = sock.makefile(mode='wb')
                dump(self._query, out_flo)
                out_flo.flush()

                in_flo = sock.makefile(mode='rb')
                result = load(in_flo)

        except EOFError as err:
            result = (0, str(err))

        except Exception as ex:
            result = (0, str(ex))

        finally:
            self._queue.put((result[0],
                result[1], self._is_class_details))

# --------------------------------------------------------------------
# SERVER CALLING CODE

# update the cells in the list view of classes
def update_view(list_view, class_data):
    list_view.clear()
    if class_data is None:
        return
    for i, line in enumerate(class_data.split('\n')):
        new_item = QListWidgetItem(line)
        new_item.setFont(QFont('Courier', 10))
        list_view.insertItem(i, new_item)

    # auto-highlight an item
    if list_view.count() > 0:
        list_view.item(0).setSelected(True)


# calls server to retrieve class data, and updates class data displayed
# in list view
def call_server_update_data(query, is_class_details, args, queue):
    print('Sent command: ', 'get_details'
          if is_class_details else 'get_overviews')
    worker_thread = WorkerThread(
        (args.host, int(args.port)), query, is_class_details, queue)
    worker_thread.start()

# --------------------------------------------------------------------
# POLL HANDLING

# handle new additions to queue--new data from requests to server
def poll_queue_helper(queue, window, list_view):

    # while the queue has new data, update the GUI with either
    # class details or general class data output
    while True:
        try:
            return_status, update_text, is_class_details = queue.get(
                    block=False)
        except Empty:
            break

        if return_status:
            if is_class_details:
                QMessageBox.information(window,
                                        'Class Details', update_text)
            else:
                update_view(list_view, update_text)
        else:
            QMessageBox.critical(window, 'Server Error',
                str(update_text))

# --------------------------------------------------------------------
# MAIN METHOD


def main():

    parser = argparse.ArgumentParser(
        description='Client for the registrar application',
        allow_abbrev=False)

    parser.add_argument('host', metavar="host",
                        help='show only those \
                            classes whose department contains dept')
    parser.add_argument('port', type=int, metavar="port",
                        help='show only those \
                            classes whose course number contains num')

    args = parser.parse_args()

    app = QApplication(argv)

    window = QMainWindow()
    window.setWindowTitle('Princeton University Class Search')

    # create queue for multi-threaded behavior; pass it into GUI init
    queue = Queue()

    # initialize GUI elements
    layout, list_view = init_gui(args, queue)

    # check poll every 100 milliseconds, update GUI with new poll data
    def poll_queue():
        poll_queue_helper(queue, window, list_view)
    timer = QTimer()
    timer.timeout.connect(poll_queue)
    timer.setInterval(100)
    timer.start()

    # final GUI init steps
    frame = QFrame()
    frame.setLayout(layout)
    window.setCentralWidget(frame)
    screen_size = QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)

    window.show()
    exit(app.exec_())


if __name__ == '__main__':
    main()
