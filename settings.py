from PyQt5 import QtWidgets, uic
import sys


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('motion_detection_ui.ui', self)

        self.checkbox_value = -1

        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')  # Find the button
        self.lineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.lineEdit_2 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2')
        self.lineEdit_3 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_3')
        self.lineEdit_4 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_4')

        self.checkbox = self.findChild(QtWidgets.QCheckBox, 'checkBox')
        self.checkbox_2 = self.findChild(QtWidgets.QCheckBox, 'checkBox_2')
        self.checkbox_3 = self.findChild(QtWidgets.QCheckBox, 'checkBox_3')
        self.checkbox_4 = self.findChild(QtWidgets.QCheckBox, 'checkBox_4')

        self.button.clicked.connect(self.printButtonPressed)  # Remember to pass the definition/method,
                                                              # not the return value!
        self.checkbox.clicked.connect(self.checkbox_checked)
        self.checkbox_2.clicked.connect(self.checkbox_2_checked)
        self.checkbox_3.clicked.connect(self.checkbox_3_checked)
        self.checkbox_4.clicked.connect(self.checkbox_4_checked)
        self.show()

    def checkbox_checked(self):
        self.checkbox_value = 1

    def checkbox_2_checked(self):
        self.checkbox_value = 5

    def checkbox_3_checked(self):
        self.checkbox_value = 10

    def checkbox_4_checked(self):
        self.checkbox_value = 30

    def printButtonPressed(self):
        try:
            thresh = int(self.lineEdit.text())
            area = int(self.lineEdit_2.text())
            kernel_size = self.lineEdit_3.text().split(',')
            kernel_size = (kernel_size[0], kernel_size[1])
            f = open('settings.txt', 'w')
            f.write(str(thresh) + ';' + str(area) + ';' + str(kernel_size[0]) + ',' + str(kernel_size[1]) + ';' + str(self.checkbox_value))
            f.close()
            self.close()
        except Exception as e:
            print('Parameters not entered: ' + e.args)


def run_settings():
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.setWindowTitle('Motion detection settings')
    window.setFixedSize(320, 240)
    app.exec()
