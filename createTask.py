import sqlite3
import datetime

from itertools import chain
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class createTask(QMainWindow):
    def __init__(self, parent, task_type):
        super().__init__()
        uic.loadUi('createEditTask.ui', self)
        self.parent = parent

        self.task_type = task_type

        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        categories = cur.execute("""SELECT title from categories""")

        self.categoryInput.addItem("Без категории")
        for category in categories:
            self.categoryInput.addItem(category[0])

        if self.task_type != 'daily':
            self.repeatLabel.hide()
            for btn in self.weekButtons.buttons():
                btn.hide()
                btn.clicked.connect(self.toggle_day)
        else:
            self.week = {"ПН": 1, "ВТ": 1, "СР": 1, "ЧТ": 1, "ПТ": 1, "СБ": 1, "ВС": 1}
            for btn in self.weekButtons.buttons():
                btn.clicked.connect(self.toggle_day)
            # self.MondayBtn.hide()
            # self.TuesdayBtn.hide()
            # self.WednesDay.hide()
            # self.ThursdayBtn.hide()
            # self.FridayBtn.hide()
            # self.SaturdayBtn.hide()
            # self.SundayBtn.hide()

        self.cancelBtn.clicked.connect(self.cancel)
        self.saveBtn.clicked.connect(self.save)

        if self.task_type == 'daily':
            self.deadlineInput.hide()
            self.deadlineFrame.hide()
            self.deadlineCheckBox.hide()
        elif self.task_type == 'today':
            self.deadlineInput.setMinimumDate(QDate.currentDate())
            self.deadlineCheckBox.stateChanged.connect(self.toggle_deadline)
        else:
            self.deadlineInput.setMinimumDate(QDate.currentDate().addDays(1))
            self.deadlineCheckBox.stateChanged.connect(self.toggle_deadline)


    def toggle_deadline(self, x):
        self.deadlineInput.setEnabled(bool(x))

    def cancel(self):
        self.close()

    def toggle_day(self):
        if self.week[self.sender().text()]:
            if sum(self.week.values()) == 1:
                self.statusBar().showMessage("Должен быть выбран хотя бы один день недели.", 5000)
                return
            self.sender().setStyleSheet(f"background-color: #fff; border: 5px solid #fff;")
            self.week[self.sender().text()] = 0
        else:
            self.sender().setStyleSheet(f"background-color: #0f0; border: 5px solid #0f0;")
            self.week[self.sender().text()] = 1

    def save(self):
        title = self.titleInput.text()
        if title.strip() == '':
            self.statusBar().showMessage("Название не может быть пустым")
            return



        # if self.deadlineCheckBox.isChecked() and

        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        category_title = self.categoryInput.currentText()
        description = self.descriptionInput.toPlainText()
        # if self.task_type != 'daily':
        #     deadline = self.deadlineInput.date()
        #     print(deadline.date())
        if self.task_type == 'daily':
            repeat = []

            for d in self.week:
                if self.week[d]:
                    repeat.append(d)
            repeat = ', '.join(repeat)

        # print(title, category_title, description)
        if category_title == 'Без категории':
            category = 'NULL'
        else:
            category = cur.execute("""
            SELECT id FROM categories
            WHERE title = ?
            """, (category_title,)).fetchone()[0]


        titles = []

        for i in range(self.parent.tasksList.count()):
            titles.append(self.parent.tasksList.item(i).text())

        print(title, titles)
        for t in titles:
            if title == t:
                self.statusBar().showMessage("Такое дело уже есть в списке")
                return

        if self.deadlineCheckBox.isChecked():
            deadline = "'" + self.deadlineInput.date().toString("yyyy-MM-dd") + "'"
        else:
            deadline = 'null'
        print(deadline)
        if self.task_type == 'today':
            # titles = cur.execute(f"""SELECT title FROM Today""")
            # for t in titles:
            #     if title == t[0]:
            #         self.statusBar().showMessage("Такое дело уже есть в списке")
            #         return
            cur.execute(f"""
            INSERT INTO Today(title, description, category, isDone, deadline)
            VALUES('{title}', '{description}', {category}, 0, {deadline})
            """)
        elif self.task_type == 'tomorrow':

            # for t in titles:
            #     if title == t[0]:
            #         self.statusBar().showMessage("Такое дело уже есть в списке")
            #         return

            cur.execute(f"""
            INSERT INTO Tomorrow(title, description, category, deadline)
            VALUES('{title}', '{description}', {category}, {deadline})
            """)
        elif self.task_type == 'daily':
            # titles = cur.execute(f"""SELECT title FROM Daily""")
            # for t in titles:
            #     if title == t[0]:
            #         self.statusBar().showMessage("Такое дело уже есть в списке")
            #         return

            cur.execute(f"""
            INSERT INTO Daily(title, description, category, repeat)
            VALUES('{title}', '{description}', {category}, '{repeat}')
            """)

        con.commit()
        con.close()

        if self.task_type == 'today':
            self.parent.load_today()
        elif self.task_type == 'tomorrow':
            self.parent.load_tomorrow()
        elif self.task_type == 'daily':
            self.parent.load_daily()

        con.close()
        self.close()
