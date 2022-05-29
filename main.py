import sys, ctypes
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox,QMainWindow
from PyQt5.QtWidgets import QLabel, QLineEdit
from PyQt5.QtCore import pyqtSignal, QObject
from random import randrange

setstell1= '''
QPushButton {
    color: rgb(248, 248, 255);border: 2px solid rgb(248, 248, 255);background: rgb(28, 28, 28);
}
QWidget {
    background-color:rgb(28,28, 28);
    }
QLabel {
color: rgb(248, 248, 255)
}
QLineEdit {
color: rgb(248, 248, 255)
}
QComboBox {
color: rgb(248, 248, 255);border: 2px solid rgb(248, 248, 255);background: rgb(28, 28, 28);
}
QComboBox QAbstractItemView {
color: rgb(248, 248, 255);border: 2px solid rgb(248, 248, 255);background: rgb(28, 28, 28);
}
'''


class setting(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(600, 200, 700, 600)
        self.setWindowTitle('Setting')
        self.setStyleSheet('background: rgb(248, 248, 255);')

        self.Fiel_line = QLabel(self)
        self.Fiel_line.setText("Set path form periods program fiel:")
        self.Fiel_line.move(100, 50)

        self.Fiel_line_in = QLineEdit(self)
        self.Fiel_line_in.move(100, 75)
        self.Fiel_line_in.setMaxLength(50)

        self.star_line = QLabel(self)
        self.star_line.setText("Set path form star fiel:")
        self.star_line.move(100, 150)

        self.star_line_in = QLineEdit(self)
        self.star_line_in.move(100, 175)
        self.star_line_in.setMaxLength(50)

        self.butn = QPushButton(self)
        self.butn.setText("ok")
        self.butn.show()

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        user = ctypes.windll.user32
        self.x = user.GetSystemMetrics(0)
        self.y = user.GetSystemMetrics(1)

    def initUI(self):
        user = ctypes.windll.user32
        self.setGeometry(0, 0, user.GetSystemMetrics(0), user.GetSystemMetrics(1))
        self.setWindowTitle('Звёздный помошник')
        self.setStyleSheet('background: rgb(248, 248, 255);')

        self.line_coord = QLabel(self)
        self.line_coord.setText("Coords (J2000):")
        self.line_coord.move(100, 50)

        self.line_coord_in = QLineEdit(self)
        self.line_coord_in.move(300, 50)

        self.line_Per = QLabel(self)
        self.line_Per.setText("Period (d):")
        self.line_Per.move(100, 100)

        self.line_Per_in = QLineEdit(self)
        self.line_Per_in.move(300, 100)

        self.line_E = QLabel(self)
        self.line_E.setText("Epoch:")
        self.line_E.move(100, 150)

        self.line_E_in = QLineEdit(self)
        self.line_E_in.move(300, 150)

        self.line_F = QLabel(self)
        self.line_F.setText("Fiel path:")
        self.line_F.move(100, 200)

        self.line_F_in = QLineEdit(self)
        self.line_F_in.move(300, 200)
        self.line_F_in.setMaxLength(40)

        self.butn1 = QPushButton("go", self)
        self.butn1.move(800, 500)
        self.butn1.resize(100, 50)
        self.butn1.clicked.connect(self.count)

        self.butn2 = QPushButton("Clear", self)
        self.butn2.move(1700, 100)
        self.butn2.resize(100, 50)
        self.butn2.clicked.connect(self.claer)

        self.butn3 = QPushButton("Dark", self)
        self.butn3.move(1700, 50)
        self.butn3.resize(100, 50)
        self.butn3.clicked.connect(self.dark)

        self.box = QComboBox(self)
        self.box.setGeometry(100, 250, 100, 25)
        self.box.addItem("Atlass")
        self.box.addItem("ZTF")
        self.box.addItem("Other")

        self.val_Ep = QLabel(self)
        self.val_Ep.setText("Исправленная Epoch")
        self.val_Ep.move(100, 300)

        self.val_Ep_in = QLineEdit(self)
        self.val_Ep_in.move(300, 300)

    def claer(self):
        self.line_F_in.clear()
        self.line_coord_in.clear()
        self.line_E_in.clear()
        self.line_Per_in.clear()

    def count(self):
        self.butn1.setText("Готово")

    def dark(self):
        if self.butn3.text() == "Dark":
            self.butn3.setText("White")
            self.setStyleSheet(setstell1)
        else:
            self.butn3.setText("Dark")
            self.setStyleSheet('background: rgb(248, 248, 255);')

class win(QMainWindow):
    def __init__(self):
        super().__init__()

    def w1(self):
        self.w1 = setting()
        self.w1.butn.clicked.connect(self.w2)
        self.w1.butn.clicked.connect(self.w1.close)
        self.w1.show()


    def w2(self):
        self.w2 = Example()
        self.w2.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    st = win()
    st.w1()
    sys.exit(app.exec())

