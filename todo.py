import datetime
import sqlite3
import csv
import os
# Вайолет Эвергарден
# Нура рикуо
# Arknights
from itertools import chain
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from createTask import createTask
from editTask import editTask
from categoriesSettings import categoriesSettings
from createReminder import createReminder
from alarm import alarm




class todo(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('todo.ui', self)
        self.tasksList.setIconSize(QSize(20, 20))
        self.tasksList.setFont(QFont("Times", 12, QFont.Black))

        self.addBtn.clicked.connect(self.add_task)

        # self.tasksList.itemClicked.connect(self.update_box)
        self.tasksList.itemDoubleClicked.connect(self.update_box)
        # self.tasksList.itemClicked.connect(self.update_box)

        self.today.clicked.connect(self.load_today)
        self.tomorrow.clicked.connect(self.load_tomorrow)
        self.daily.clicked.connect(self.load_daily)

        self.categoriesSettingsBtn.clicked.connect(self.open_categories_settings)
        self.reminderBtn.clicked.connect(self.create_reminder)
        self.intoCsvBtn.clicked.connect(self.make_csv_plan)

        self.deleteBtn.clicked.connect(self.delete_task)
        self.markAsDoneBtn.clicked.connect(self.btn_update_box)
        self.editBtn.clicked.connect(self.show_edit_task)

        with open('LocalStorage.txt', 'r', encoding="utf8") as ls:
            last_come_date = ls.readline().strip()
            if last_come_date != str(datetime.datetime.now().date()):
                self.change_plans()


        self.hide_right_part()

        self.curr_plan = ''

        self.load_today()
        self.load_timer()

        self.loadImages()
        self.load_font()

    def loadImages(self):
        self.deleteBtn.setIcon(QIcon(r"images/bin.png"))
        self.editBtn.setIcon(QIcon(r"images/pen.png"))

    def load_font(self):
        fontId = QFontDatabase.addApplicationFont(r"Roboto/Roboto-Regular.ttf")
        # QMessageBox.information(None, "Message", f"fontId -> {fontId}")
        if fontId == 0:
            fontName = QFontDatabase.applicationFontFamilies(fontId)[0]
            self.font = QFont(fontName, 15)
        else:
            self.font = QFont()

        self.tasksList.setFont(self.font)

        self.today.setFont(self.font)
        self.tomorrow.setFont(self.font)
        self.daily.setFont(self.font)

        self.categoriesSettingsBtn.setFont(self.font)
        self.reminderBtn.setFont(self.font)
        self.intoCsvBtn.setFont(self.font)

        self.addBtn.setFont(self.font)

        self.title.setFont(self.font)
        self.category.setFont(self.font)
        self.repeat.setFont(self.font)
        self.description.setFont(self.font)
        self.markAsDoneBtn.setFont(self.font)

        self.titleLabel.setFont(self.font)
        self.categoryLabel.setFont(self.font)
        self.repeatLabel.setFont(self.font)
        self.descriptionLabel.setFont(self.font)

        self.planLabel.setFont(self.font)



    def keyPressEvent(self, event):
        print(event.key())
        if event.key() == 16777220 and self.tasksList.currentItem():
            print(self.tasksList.currentItem())
            self.show_right_part(self.tasksList.currentItem())


    def load_timer(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        now = datetime.datetime.now()
        print(now.date())

        self.timer = QTimer()
        self.curr_time = QTime(now.hour, now.minute, now.second)
        self.time = QTime(self.curr_time)
        self.timer.timeout.connect(self.time_management)
        self.timer.start(1000)

        self.reminders = cur.execute(f"""
        SELECT * from reminders
        WHERE date = '{now.date()}'
        """).fetchall()


    def time_management(self):
        self.time = self.time.addSecs(1)
        if self.time.hour() == 0 and self.time.minute() == 0:
            self.change_plans()
        for r in self.reminders:
            h, m = map(int, r[2].split(':'))
            # print(self.time.hour(), h, self.time.minute(), m)
            if self.time.hour() == h and self.time.minute() == m:
                self.alarm_widet = alarm(self, r[2], r[3])
                self.alarm_widet.show()
                # print('reached')

                con = sqlite3.connect("database.sqlite")
                cur = con.cursor()

                cur.execute(f"""
                DELETE FROM reminders
                WHERE id = {r[0]}
                """)
                con.commit()
                self.reminders.remove(r)

        # print(self.time.toString())

    def load_tasks(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        if self.curr_plan == 'today':
            result = cur.execute(f"""
            SELECT Today.title, IFNULL(categories.color, '255 255 255'), isDone
            FROM Today
            LEFT JOIN categories
            ON Today.category = categories.id
            """).fetchall()

        elif self.curr_plan == 'tomorrow':
            result1 = cur.execute(f"""
            SELECT Tomorrow.title, IFNULL(categories.color, '255 255 255')
            FROM Tomorrow
            LEFT JOIN categories
            ON Tomorrow.category = categories.id
            """).fetchall()

            result2 = cur.execute(f"""
            SELECT Daily.title, IFNULL(categories.color, '255 255 255')
            FROM Daily
            LEFT JOIN categories
            ON Daily.category = categories.id
            """).fetchall()

            result3 = cur.execute(f"""
            SELECT Today.title, IFNULL(categories.color, '255 255 255')
            FROM Today
            LEFT JOIN categories
            ON Today.category = categories.id
            WHERE Today.isDone = 0
            """).fetchall()
            result = chain(result1, result2, result3)
        elif self.curr_plan == 'daily':
            result = cur.execute(f"""
            SELECT Daily.title, IFNULL(categories.color, '255 255 255')
            FROM Daily
            LEFT JOIN categories
            ON Daily.category = categories.id
            """).fetchall()


        self.tasksList.clear()
        titles = []
        for elem in result:
            if elem[0] not in titles:
                titles.append(elem[0])
                # print(elem)
                item = QListWidgetItem()
                # if elem[1]:
                c1, c2, c3 = map(int, elem[1].split())
                if 1 - (0.299 * c1 + 0.587 * c2 + 0.114 * c3) / 255 < 0.5:
                    item.setForeground(QColor(0, 0, 0))
                    if self.curr_plan == 'today':
                        if elem[2] == 0:
                            icon = QIcon(r'images/blackCheckboxOff.png')
                        else:
                            icon = QIcon(r'images/blackCheckboxOn.png')
                        item.setIcon(icon)
                else:
                    item.setForeground(QColor(255, 255, 255))
                    if self.curr_plan == 'today':
                        if elem[2] == 0:
                            icon = QIcon(r'images/whiteCheckboxOff.png')
                        else:
                            icon = QIcon(r'images/whiteCheckboxOn.png')
                        item.setIcon(icon)
                item.setBackground(QColor(c1, c2, c3))
                # print(c1, c2, c3)


                item.setText(elem[0])
                self.tasksList.addItem(item)
        con.close()

    def load_today(self):
        if self.curr_plan != 'today':
            self.hide_right_part()
        self.curr_plan = 'today'
        self.planLabel.setText("План на сегодня")
        self.load_tasks()

    def load_tomorrow(self):
        if self.curr_plan != 'tomorrow':
            self.hide_right_part()
        self.curr_plan = 'tomorrow'
        self.planLabel.setText("План на завтра")
        self.load_tasks()

    def load_daily(self):
        if self.curr_plan != 'daily':
            self.hide_right_part()
        self.curr_plan = 'daily'
        self.planLabel.setText("Ежедневные дела")
        self.load_tasks()

    def update_box(self, item):
        if self.curr_plan != 'today':
            return
        text = item.text()

        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        result = cur.execute(f"""
        SELECT Today.isDone, IFNULL(categories.color, '255 255 255')
        FROM Today
        LEFT JOIN categories
        ON Today.category = categories.id
        WHERE Today.title = '{text}'
        """).fetchone()

        c1, c2, c3 = map(int, result[1].split())

        if 1 - (0.299 * c1 + 0.587 * c2 + 0.114 * c3) / 255 < 0.5:
            if result[0] == 0:
                icon = QIcon(r'images/blackCheckboxOn.png')
            else:
                icon = QIcon(r'images/blackCheckboxOff.png')
        else:
            if result[0] == 0:
                icon = QIcon(r'images/whiteCheckboxOn.png')
            else:
                icon = QIcon(r'images/whiteCheckboxOff.png')

        item.setIcon(icon)

        if result[0] == 1:
            cur.execute("""UPDATE Today SET isDone = 0 WHERE title = ?""", (text,))
            self.markAsDoneBtn.setText("Пометить как сделанное")
        else:
            cur.execute("""UPDATE Today SET isDone = 1 WHERE title = ?""", (text,))
            self.markAsDoneBtn.setText("Пометить как не сделанное")
        con.commit()
        con.close()

    def btn_update_box(self):
        self.update_box(self.tasksList.currentItem())


    def add_task(self):
        self.create_task = createTask(self, self.curr_plan)
        self.create_task.show()


    def hide_right_part(self):
        self.titleLabel.hide()
        self.title.hide()

        self.categoryLabel.hide()
        self.category.hide()

        self.repeatLabel.hide()
        self.repeat.hide()

        self.descriptionLabel.hide()
        self.description.hide()

        self.deleteBtn.hide()
        self.markAsDoneBtn.hide()
        self.editBtn.hide()

    def show_right_part(self, item):
        index = self.tasksList.indexFromItem(item).row()

        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        if self.curr_plan == 'today':
            info = cur.execute(f"""SELECT * FROM Today""").fetchall()
        elif self.curr_plan == 'tomorrow':
            info1 = cur.execute(f"""SELECT * FROM Tomorrow""").fetchall()
            info2 = cur.execute(f"""SELECT * FROM Daily""").fetchall()
            info3 = cur.execute(f"""SELECT * FROM Today WHERE isDone = 0""").fetchall()
            info = list((chain(info1, info2, info3)))
        elif self.curr_plan == 'daily':
            info = cur.execute(f"""SELECT * FROM Daily""").fetchall()

        result = info[index]

        print(result)

        if result[3]:
            cat = cur.execute(f"""
            SELECT IFNULL(title, 'Без категории') FROM Categories
            WHERE id = {result[3]}
            """).fetchone()[0]
        else:
            cat = 'Без категории'

        print(cat)

        # print(index)

        # result = cur.execute(f"""
        # SELECT {self.curr_plan}.title, IFNULL(categories.title, 'Без категории'), {self.curr_plan}.description
        # FROM {self.curr_plan}
        # LEFT JOIN categories
        # ON {self.curr_plan}.category = categories.id
        # WHERE {self.curr_plan}.id = {curr_id}
        # """).fetchone()

        # if self.curr_plan == 'daily':
        #     repeat = cur.execute(f"""
        #     SELECT repeat FROM Daily
        #     WHERE id = {curr_id}
        #     """).fetchone()

        # res = cur.execute("""
        # SELECT films.id, films.title, films.year, IFNULL(genres.title, films.genre), films.duration FROM films
        # LEFT JOIN genres
        # ON films.genre = genres.id
        # ORDER BY films.id DESC
        # """).fetchall()


        self.task_id = result[0]

        self.titleLabel.show()
        self.title.clear()
        self.title.append(result[1])
        self.title.show()

        self.categoryLabel.show()
        self.category.clear()
        self.category.append(cat)
        self.category.show()

        if self.curr_plan == 'daily':
            self.repeatLabel.show()
            self.repeat.clear()
            self.repeat.append(result[-1])
            self.repeat.show()
            self.deleteBtn.setFixedSize(100, 30)
            self.editBtn.setFixedSize(100, 30)

        self.descriptionLabel.show()
        self.description.clear()
        self.description.append(result[2])
        self.description.show()

        if self.curr_plan != 'tomorrow':
            self.deleteBtn.show()
            self.editBtn.show()
        if self.curr_plan == 'today':
            self.deleteBtn.setFixedSize(30, 30)
            self.editBtn.setFixedSize(30, 30)
            if result[4]:
                self.markAsDoneBtn.setText("Пометить как не сделанное")
            else:
                self.markAsDoneBtn.setText("Пометить как сделанное")
            self.markAsDoneBtn.show()


    def open_categories_settings(self):
        self.categories_settings = categoriesSettings(self)
        self.categories_settings.show()

    def delete_task(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        # x = QMessageBox.question(self, "Внимание",
        #                          f'Действительно удалить категорию "{title}"?\n (Все дела с этой категорией станут без категории)')
        # if x > 50000:
        #     return

        cur.execute(f"""
        DELETE FROM {self.curr_plan}
        WHERE id = {self.task_id}
        """)

        con.commit()

        self.load_tasks()

        self.hide_right_part()

        self.statusBar().showMessage("Дело успешно удалено")


    def show_edit_task(self):
        self.edit_task = editTask(self, self.curr_plan, self.task_id)
        self.edit_task.show()

    def create_reminder(self):
        self.reminder = createReminder(self)
        self.reminder.show()

    def change_plans(self):
        # with open('LocalStorage.txt', encoding="utf8") as csvfile:
        #     reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        #     for index, row in enumerate(reader):
        #         if index > 10:
        #             break
        #         print(row)

        con = sqlite3.connect('database.sqlite')
        cur = con.cursor()

        result1 = cur.execute("""SELECT title, description, category, deadline FROM today WHERE isDone = 0""").fetchall()
        result2 = cur.execute("""SELECT title, description, category, deadline FROM tomorrow""").fetchall()
        result3 = cur.execute("""SELECT title, description, category, 0 FROM daily""").fetchall()

        result = chain(result1, result2, result3)

        cur.execute("""DELETE FROM today""")

        con.commit()

        now = datetime.datetime.now()
        date1 = now.year * 100000 + now.month * 1000 + now.day

        titles = []
        for r in set(result):
            print(r)
            if r[3] and str(r[3]) != '0':
                y, m, d = map(int, r[3].split('-'))
                date2 = y * 100000 + m * 1000 + d
                deadline = "'" + r[3] + "'"
            else:
                date2 = 'NULL'

            if date2 == 'NULL' or date2 > date1 and r[0] not in titles:
                titles.append(r[0])
                cur.execute(f"""
                INSERT INTO today(title, description, category, isDone, deadline)
                VALUES('{r[0]}', '{r[1]}', {r[2]}, 0, {r[3]})
                """)

        con.commit()

        cur.execute("""DELETE FROM tomorrow""")

        con.commit()


    def make_csv_plan(self):
        user = os.getenv("USERPROFILE")
        filename = user + r"\Desktop\plan.csv"
        with open(filename, 'w', newline='', encoding="utf8") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(['Название', 'Описание', 'Категория', 'Выполнено/Не выполнено'])

            con = sqlite3.connect('database.sqlite')
            cur = con.cursor()

            result = cur.execute("""SELECT title, description, category, isDone FROM today""")

            result = cur.execute("""
            SELECT Today.title, Today.description, IFNULL(categories.title, 'Без категории'),
            CASE WHEN Today.isDone = 1
            THEN 'Выполнено'
            ELSE 'Не выполнено'
            END
            FROM Today
            LEFT JOIN categories
            ON Today.category = categories.id
            """)

            for r in result:
                writer.writerow(r)
        self.statusBar().showMessage(f"План находится в {filename}", 5000)

    def closeEvent(self, event):
        with open('LocalStorage.txt', 'w', encoding="utf8") as ls:
            ls.write(str(datetime.datetime.now().date()))

        try:
            self.create_task.hide()
        except Exception:
            pass
        try:
            self.edit_task.hide()
        except Exception:
            pass
        try:
            self.reminder.hide()
        except Exception:
            pass
        try:
            self.categories_settings.hide()
        except Exception:
            pass
        try:
            self.alarm_widet.hide()
        except Exception:
            pass
        event.accept()









