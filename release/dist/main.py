import sys
import os
import sqlite3

from PyQt6.QtWidgets import QWidget, QApplication, QTableWidgetItem, QMessageBox
from UI.main_ui import Ui_Form
from UI.addEditCoffeeForm_ui import Ui_Form_2


class CoffeeInformation(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect(os.path.join("data", "coffee.sqlite"))
        self.load_table()
        self.pushButton.clicked.connect(self.open_add_or_edit_form)
        self.second_form_is_open = False

    def load_table(self):
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

        cur = self.con.cursor()
        result = cur.execute('SELECT * FROM coffee_information').fetchall()
        if not result:
            return
        self.tableWidget.setColumnCount(7)
        labels = ['ID',
                  'название сорта',
                  'степень обжарки',
                  'молотый/в зёрнах',
                  'описание вкуса',
                  'цена(руб)',
                  'объём упаковки(г)'
                  ]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.setColumnWidth(0, 10)
        self.tableWidget.setColumnWidth(1, 120)
        self.tableWidget.setColumnWidth(2, 120)
        self.tableWidget.setColumnWidth(3, 120)
        self.tableWidget.setColumnWidth(4, 236)
        self.tableWidget.setColumnWidth(5, 70)
        self.tableWidget.setColumnWidth(6, 120)
        n = 0
        for elem in result:
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1
            )
            self.tableWidget.setItem(n, 0, QTableWidgetItem(str(elem[0])))
            self.tableWidget.setItem(n, 1, QTableWidgetItem(str(elem[1])))
            self.tableWidget.setItem(n, 2, QTableWidgetItem(str(elem[2])))
            self.tableWidget.setItem(n, 3, QTableWidgetItem(str(elem[3])))
            self.tableWidget.setItem(n, 4, QTableWidgetItem(str(elem[4])))
            self.tableWidget.setItem(n, 5, QTableWidgetItem(str(elem[5])))
            self.tableWidget.setItem(n, 6, QTableWidgetItem(str(elem[6])))
            n += 1

    def open_add_or_edit_form(self):
        try:
            self.add_or_edit_form = AddEditCoffeeForm(self, self.con)
        except Exception as e:
            print(e)
        self.add_or_edit_form.show()
        self.second_form_is_open = True

    def closeEvent(self, event):
        if self.second_form_is_open is True:
            self.add_or_edit_form.close()


class AddEditCoffeeForm(QWidget, Ui_Form_2):
    def __init__(self, parent, con):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.con = con
        self.initUI()

    def initUI(self):
        self.add_button.clicked.connect(self.add_to_db)
        self.edit_button.clicked.connect(self.edit_db_string)
        self.comboBox.currentTextChanged.connect(self.load_info_for_edit)
        self.update_combo_box()
        fields = [
            'variety_name',
            'degree_of_roasting',
            'ground_or_beans',
            'description_of_taste',
            'price',
            'packaging_volume'
        ]
        self.fields = ','.join(fields)

    def update_combo_box(self):
        self.comboBox.clear()
        cur = self.con.cursor()
        result = cur.execute('SELECT id FROM coffee_information').fetchall()
        if not result:
            return
        for item in result:
            self.comboBox.addItem(str(item[0]))

    def load_info_for_edit(self):
        cur_id = self.comboBox.currentText()
        if cur_id == '':
            return
        cur_id = int(cur_id)
        cur = self.con.cursor()
        result = cur.execute('SELECT * FROM coffee_information WHERE id = ?', (cur_id, )).fetchall()
        result = result[0]
        self.lineEdit_2.setText(result[1])
        self.comboBox_5.setCurrentText(result[2])
        self.comboBox_4.setCurrentText(result[3])
        self.lineEdit_9.setText(result[4])
        self.lineEdit_8.setText(str(result[5]))
        self.lineEdit_7.setText(str(result[6]))

    def add_to_db(self):
        sort = self.lineEdit.text()
        if not sort:
            sort = 'н/д'
        stepen = self.comboBox_2.currentText()
        molot = self.comboBox_3.currentText()
        desc = self.lineEdit_4.text()
        if not desc:
            desc = 'н/д'
        price = self.lineEdit_5.text()
        if not price:
            price = 'н/д'
        vol = self.lineEdit_6.text()
        if not vol:
            vol = 'н/д'

        cur = self.con.cursor()
        text = f'INSERT INTO coffee_information({self.fields}) VALUES(?,?,?,?,?,?)'
        cur.execute(text, (sort, stepen, molot, desc, price, vol))
        self.con.commit()
        self.parent.load_table()

        self.update_combo_box()
        QMessageBox.information(self, 'Успех! ', 'Успешно добавлено')

    def edit_db_string(self):
        sort = self.lineEdit_2.text()
        if not sort:
            sort = 'н/д'
        stepen = self.comboBox_5.currentText()
        molot = self.comboBox_4.currentText()
        desc = self.lineEdit_9.text()
        if not desc:
            desc = 'н/д'
        price = self.lineEdit_8.text()
        if not price:
            price = 'н/д'
        vol = self.lineEdit_7.text()
        if not vol:
            vol = 'н/д'
        string_id = int(self.comboBox.currentText())

        cur = self.con.cursor()
        text = '''UPDATE
    coffee_information
SET
    variety_name = ?,
    degree_of_roasting = ?,
    ground_or_beans = ?,
    description_of_taste = ?,
    price = ?,
    packaging_volume = ?
WHERE id = ?'''
        cur.execute(text, (sort, stepen, molot, desc, price, vol, string_id))
        self.con.commit()
        self.parent.load_table()

        QMessageBox.information(self, 'Успех! ', 'Успешно отредактировано')

    def closeEvent(self, event):
        self.parent.second_form_is_open = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CoffeeInformation()
    ex.show()
    sys.exit(app.exec())
