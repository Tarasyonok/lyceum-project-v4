import datetime
import sqlite3
import os
import sys

from itertools import chain
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtMultimedia



class alarm(QMainWindow):
    def __init__(self, parent, time, description):
        super().__init__()
        uic.loadUi('alarm.ui', self)
        self.parent = parent
        self.time.setText(time)
        self.description.setText(description)
        if description.strip() == '':
            self.description.hide()

        CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(CURRENT_DIR, "sound1.mp3")
        self.player = QtMultimedia.QMediaPlayer()
        url = QUrl.fromLocalFile(filename)
        self.player.setMedia(QtMultimedia.QMediaContent(url))
        self.player.play()
        self.closeBtn.clicked.connect(self.closeEvent)
        self.repeatBtn.clicked.connect(self.repeat_alarm)

        self.player.stateChanged.connect(self.repeat_alarm)


    def closeEvent(self, event):
        self.player.stop()
        event.accept()

    def repeat_alarm(self):
        print(datetime.datetime.now().date(), datetime.datetime.now().time(), self.description.toPlainText())
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        cur.execute(f"""
        INSERT INTO reminders(date, time, description)
        VALUES('{datetime.datetime.now().date()}', '{str(datetime.datetime.now().time())[:5]}', '{self.description.toPlainText()}')
        """)
        con.commit()

        self.parent.statusBar().showMessage("Напоминание перенесено на 10 минут", 5000)

        self.close()

        # def handle_state_changed(state):
        #     if state == QtMultimedia.QMediaPlayer.PlayingState:
        #         print("started")
        #     elif state == QtMultimedia.QMediaPlayer.StoppedState:
        #         print("finished")
        #
        # player.stateChanged.connect(handle_state_changed)


    # def open_add(self):
    #     self.opa = QMainWindow()
    #     uic.loadUi('alarm.ui', self.opa)
    #     self.opa.show()









