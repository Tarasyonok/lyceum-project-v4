import sqlite3

from random import randint
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class categoriesSettings(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        uic.loadUi('categoriesSettings.ui', self)
        self.parent = parent

        fontId = QFontDatabase.addApplicationFont(r"Roboto/Roboto-Regular.ttf")
        # QMessageBox.information(None, "Message", f"fontId -> {fontId}")

        if fontId == 0:
            fontName = QFontDatabase.applicationFontFamilies(fontId)[0]
            self.font = QFont(fontName, 30)
        else:
            self.font = QFont()

        self.addBtn.setFont(self.font)

        self.addBtn.clicked.connect(self.addCategory)
        self.editBtn.clicked.connect(self.editCategory)
        self.deleteBtn.clicked.connect(self.deleteCategory)

        self.cancelBtn.clicked.connect(self.cancel)

    def addCategory(self):
        self.hide()
        title, ok_pressed = QInputDialog.getText(self, "Введите название категории", "Введите название категории")

        if not ok_pressed:
            return

        if title.strip() == '':
            self.show()
            self.statusBar().showMessage("Название не может быть пустым")
            return

        print(title)

        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        titles = cur.execute("""SELECT title FROM categories""").fetchall()

        for t in titles:
            if title == t[0]:
                self.show()
                self.statusBar().showMessage("Такая категория уже есть")
                return

        color_d = QColorDialog(self)
        # color_d.setCurrentColor(QColor(randint(1, 255), randint(0, 255), randint(0, 255)))
        # color = color_d.exec_().getColor()
        color = color_d.getColor()
        # print(color)
        c1, c2, c3 = color.red(), color.green(), color.blue()
        # print(c1, c2, c3)
        if c1 == c2 == c3 == 0:
            return

        # colors = cur.execute("""SELECT color FROM categories""").fetchall()
        #
        # for c in colors:
        #     if f'{c1}, {c2}, {c3}' == c[0]:
        #         self.show()
        #         self.statusBar().showMessage("Такой цвет уже есть")
        #         return

        cur.execute(f"""INSERT INTO categories(title, color) VALUES('{title}', '{c1} {c2} {c3}')""")
        con.commit()
        con.close()
        self.parent.statusBar().showMessage("Категория успешно добавлена.")
        self.close()

        # name, ok_pressed = QInputDialog.getText(self, "Введите имя",
        #                                         "Как тебя зовут?")
        # if ok_pressed:
        #     print(name)

    def editCategory(self):
        self.hide()
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        titles = cur.execute("""SELECT title FROM categories""").fetchall()
        options = []
        for t in titles:
            options.append(t[0])

        self.title, ok_pressed = QInputDialog.getItem(
            self, "Выберите категорию", "Выберите категорию:",
            options, 0, False)

        if not ok_pressed:
            return

        self.edit = QMainWindow(self)
        self.edit.setWindowTitle("Изменение")
        self.edit.setFixedSize(320, 200)

        self.edit.titleLabel = QLabel(self.edit)
        self.edit.titleLabel.setText("Название:")
        self.edit.titleLabel.move(55, 20)

        self.edit.colorLabel = QLabel(self.edit)
        self.edit.colorLabel.setText("Цвет:")
        self.edit.colorLabel.move(55, 110)

        self.edit.cancelBtn = QPushButton(self.edit)
        self.edit.cancelBtn.setText("Отмена")
        self.edit.cancelBtn.move(20, 160)

        self.edit.cancelBtn.clicked.connect(self.edit.close)

        self.edit.titleInput = QTextEdit(self.edit)
        self.edit.titleInput.setFixedSize(210, 30)
        self.edit.titleInput.move(50, 50)
        self.edit.titleInput.append(self.title)

        color = cur.execute("""SELECT color FROM categories WHERE title = ?""", (self.title,)).fetchone()[0]
        print(color)
        # self.c1, self.c2, self.c3 =
        c1, c2, c3 = map(int, color.split())
        self.c1, self.c2, self.c3 = c1, c2, c3
        hex_color = hex(c1)[2:].rjust(2, '0') + hex(c2)[2:].rjust(2, '0') + hex(c3)[2:].rjust(2, '0')
        print(hex_color)

        self.edit.colorLabel = QLabel(self.edit)
        self.edit.colorLabel.setFixedSize(50, 50)
        self.edit.colorLabel.move(100, 100)
        self.edit.colorLabel.setStyleSheet(f"background-color: #{hex_color}")

        self.edit.colorBtn = QPushButton(self.edit)
        self.edit.colorBtn.setText("Изменить цвет")
        self.edit.colorBtn.move(160, 110)

        self.edit.colorBtn.clicked.connect(self.color_choose)

        self.edit.saveBtn = QPushButton(self.edit)
        self.edit.saveBtn.setText("Сохранить")
        self.edit.saveBtn.move(190, 160)

        self.edit.saveBtn.clicked.connect(self.save_changes)

        self.edit.show()

    def color_choose(self):
        color_d = QColorDialog(self)
        color = color_d.getColor()
        self.c1, self.c2, self.c3 = c1, c2, c3 = color.red(), color.green(), color.blue()
        if c1 == c2 == c3 == 0:
            return
        hex_color = hex(c1)[2:].rjust(2, '0') + hex(c2)[2:].rjust(2, '0') + hex(c3)[2:].rjust(2, '0')
        self.edit.colorLabel.setStyleSheet(f"background-color: #{hex_color}")

    def save_changes(self):
        title = self.edit.titleInput.toPlainText()
        if title.strip() == '':
            self.edit.statusBar().showMessage("Пустое название")
            return

        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        titles = cur.execute("""SELECT title FROM categories""").fetchall()

        for t in titles:
            if title == t[0] and self.title != title:
                self.edit.statusBar().showMessage("Такая категория уже есть")
                return

        cur.execute(f"""
        UPDATE categories SET title = '{title}', color = '{self.c1} {self.c2} {self.c3}'
        WHERE title = '{self.title}'
        """)

        con.commit()
        con.close()
        self.parent.statusBar().showMessage("Категория успешно изменена.")
        self.update_list()
        self.edit.close()
        self.close()

    def deleteCategory(self):
        self.hide()
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        titles = cur.execute("""SELECT title FROM categories""").fetchall()


        titles = cur.execute("""SELECT title FROM categories""").fetchall()
        options = []
        for t in titles:
            options.append(t[0])

        title, ok_pressed = QInputDialog.getItem(
            self, "Выберите категорию", "Выберите категорию:",
            options, 0, False)

        if not ok_pressed:
            return

        x = QMessageBox.question(self, "Внимание", f'Действительно удалить категорию "{title}"?\n (Все дела с этой категорией станут без категории)')
        if x > 50000:
            return
        print(title)

        cur.execute("""DELETE FROM categories WHERE title = ?""", (title,))

        con.commit()
        con.close()

        self.parent.statusBar().showMessage("Категория успешно удалена.")
        self.update_list()
        self.close()

    def cancel(self):
        self.close()

    def update_list(self):
        if self.parent.curr_plan == 'today':
            self.parent.load_today()
        elif self.parent.curr_plan == 'tomorrow':
            self.parent.load_today()
        elif self.parent.curr_plan == 'daily':
            self.parent.load_today()
