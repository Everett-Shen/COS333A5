#!/usr/bin/env python

#-----------------------------------------------------------------------
# penny.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

from sys import argv, stderr, exit
from socket import socket
from pickle import load, dump
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout
from PyQt5.QtWidgets import QPushButton, QTextEdit

#-----------------------------------------------------------------------

def get_arguments():

    if len(argv) != 3:
        print('Usage: penny host port', file=stderr)
        exit(1)
    try:
        host = argv[1]
        port = int(argv[2])
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    return (host, port)

#-----------------------------------------------------------------------

def create_widgets():

    author_label = QLabel('Author: ')
    author_lineedit = QLineEdit()
    submit_button = QPushButton('Submit')
    books_textedit = QTextEdit()
    books_textedit.setReadOnly(True)

    layout = QGridLayout()
    layout.addWidget(author_label, 0, 0)
    layout.addWidget(author_lineedit, 0, 1)
    layout.addWidget(submit_button, 0, 2)
    layout.addWidget(books_textedit, 1, 0, 1, 3)
    layout.setRowStretch(0, 0)
    layout.setRowStretch(1, 1)
    layout.setColumnStretch(0, 0)
    layout.setColumnStretch(1, 1)
    layout.setColumnStretch(2, 0)

    frame = QFrame()
    frame.setLayout(layout)

    window = QMainWindow()
    window.setWindowTitle('Penny: Author Search')
    window.setCentralWidget(frame)
    screen_size = QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)

    return (window, author_lineedit, submit_button, books_textedit)

#-----------------------------------------------------------------------

def author_slot_helper(host, port, author_lineedit, books_textedit):

    author = author_lineedit.text()
    books_textedit.clear()

    try:
        with socket() as sock:
            sock.connect((host, port))

            out_flo = sock.makefile(mode='wb')
            dump(author, out_flo)
            out_flo.flush()

            in_flo = sock.makefile(mode='rb')
            books = load(in_flo)

        if len(books) == 0:
            books_textedit.insertPlainText('(None)')
        else:
            pattern = '<strong>%s</strong>: %s ($%.2f)<br>'
            for book in books:
                books_textedit.insertHtml(pattern % book.to_tuple())

    except Exception as ex:
        books_textedit.insertPlainText(str(ex))

    books_textedit.repaint()

#-----------------------------------------------------------------------

def main():

    # Get the command-line arguments.

    host, port = get_arguments()

    # Create and lay out the widgets.

    app = QApplication(argv)
    window, author_lineedit, submit_button, books_textedit = (
        create_widgets())

    # Handle signals.

    def author_slot():
        author_slot_helper(host, port, author_lineedit, books_textedit)
    submit_button.clicked.connect(author_slot)

    # Start up.

    window.show()
    author_slot()  # Populate books_textedit initially.
    exit(app.exec_())

if __name__ == '__main__':
    main()
