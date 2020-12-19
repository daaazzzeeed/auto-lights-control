from PyQt5 import QtWidgets, uic
import sys


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('loginWindowLayout.ui', self)

        self.logged_in = False

        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.lineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.lineEdit_2 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2')
        self.button.clicked.connect(self.login)
        self.show()

    def login(self):
        try:
            login = self.lineEdit.text()
            password = self.lineEdit_2.text()

            auth_data_file = open('auth_data.txt', 'r')
            auth_data = auth_data_file.readlines()
            auth_data = [item.replace('\n', '').split(',') for item in auth_data]

            for auth_detail in auth_data:
                if auth_detail[0] == login and auth_detail[1] == password:
                    self.logged_in = True
            if self.logged_in:
                f = open('logged_in.txt', 'w+')
                f.write(str(self.logged_in))
                f.close()
                self.close()
            else:
                self.lineEdit.setText('Invalid login or password')
                self.lineEdit_2.setText('')
                f = open('logged_in.txt', 'w+')
                f.write(str(self.logged_in))
                f.close()
        except Exception as e:
            print('Parameters not entered: ' + e.args)


def run_login():
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.setWindowTitle('Login to a system')
    window.setFixedSize(600, 240)
    app.exec()
