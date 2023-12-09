import sqlite3
import os
import sys
import datetime

from itertools import chain
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtMultimedia

from alarm import alarm

class createReminder(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        uic.loadUi('reminder.ui', self)
        self.parent = parent
        self.cancelBtn.clicked.connect(self.close)
        self.addBtn.clicked.connect(self.add)

    def add(self):
        date = self.dateInput.selectedDate().toString('yyyy-MM-dd')
        time = self.timeInput.time().toString('hh:mm')
        description = self.descriptionInput.toPlainText()

        print('---------')
        print(date)
        print(time)
        print(description)
        print('---------')

        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        result = cur.execute(f"""
        SELECT * FROM reminders
        WHERE date = '{date}' AND time = '{time}'
        """).fetchall()

        if len(result) != 0:
            return

        cur.execute(f"""
        INSERT INTO reminders(date, time, description)
        VALUES('{date}', '{time}', '{description}')
        """)
        con.commit()

        now = datetime.datetime.now()
        self.parent.reminders = cur.execute(f"""
        SELECT * from reminders
        WHERE date = '{now.date()}'
        """).fetchall()
        con.close()

        self.parent.statusBar().showMessage("Напоминание усаешно поставлено", 5000)
        # self.close()


