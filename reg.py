#!/usr/bin/env python

# ----------------------------------------------------------------------
# reg.py
# Author: Everett Shen, Trivan Menezes
# ----------------------------------------------------------------------

from sys import exit, argv, stderr
import argparse
from socket import socket
from pickle import dump, load
from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QMainWindow
from PyQt5.QtWidgets import QGridLayout, QDesktopWidget, QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# ----------------------------------------------------------------------


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
def init_gui(window, args):
    # layouts
    top_layout = QHBoxLayout()
    top_layout.setContentsMargins(10, 20, 10, 0)

    labels_layout = QVBoxLayout()
    line_edit_layout = QVBoxLayout()
    submit_button_layout = QVBoxLayout()

    top_layout.addLayout(labels_layout)
    top_layout.addLayout(line_edit_layout)
    top_layout.addLayout(submit_button_layout)

    labels_layout = init_labels(labels_layout)
    dept_edit, number_edit, area_edit, title_edit = init_line_edits(
        line_edit_layout)

    # slot to handle when submit button is clicked. Calls 
    # server to query appropriate data
    def submit_button_slot():
        query = {
            'd': dept_edit.text(),
            'n': number_edit.text(),
            'a': area_edit.text(),
            't': title_edit.text()
        }
        # send to server
        call_server_update_data(window, list_view, query,
                                False, args)

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
        print()
        if len(list_widget_row) > 1:
            call_server_update_data(window, list_view, query,
                                    True, args)

    # submit button
    submit_button = QPushButton('Submit')
    submit_button_layout.addWidget(submit_button)
    # submit signal handling
    submit_button.clicked.connect(submit_button_slot)

    # slots to handle events
    dept_edit.returnPressed.connect(submit_button_slot)
    number_edit.returnPressed.connect(submit_button_slot)
    area_edit.returnPressed.connect(submit_button_slot)
    title_edit.returnPressed.connect(submit_button_slot)

    list_view = QListWidget()
    # slots to handle signals
    list_view.itemActivated.connect(class_select_slot)

    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addLayout(top_layout, 0, 0)
    layout.addWidget(list_view, 1, 0)

    # load initial data
    call_server_update_data(window, list_view, {
        'd': dept_edit.text(),
        'n': number_edit.text(),
        'a': area_edit.text(),
        't': title_edit.text()
    },
        False, args)

    # returns tuple of GUI elements
    return layout


# connect to server at given port number and query for the data
# being outputted from there.
def call_server(host, port, query):
    result = (0, 'Unsuccessful Query')

    try:
        with socket() as sock:
            sock.connect((host, port))
            out_flo = sock.makefile(mode='wb')
            dump(query, out_flo)
            out_flo.flush()

            in_flo = sock.makefile(mode='rb')
            result = load(in_flo)

    except EOFError as err:
        result = (0, str(err))

    except Exception as ex:
        result = (0, str(ex))

    return result


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
def call_server_update_data(window, list_view,
                            query, is_class_details, args):
    print('Sent command: ', 'get_details'
          if is_class_details else 'get_overviews')
    return_status, update_text = call_server(
        args.host, int(args.port), query)

    if return_status:
        if is_class_details:
            QMessageBox.information(window,
                                    'Class Details', update_text)
        else:
            update_view(list_view, update_text)
    else:
        QMessageBox.critical(window, 'Server Error', str(update_text))


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

    # initialize GUI elements
    layout = init_gui(window, args)

    frame = QFrame()
    frame.setLayout(layout)

    window.setCentralWidget(frame)
    screen_size = QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)

    window.show()
    exit(app.exec_())


if __name__ == '__main__':
    main()
