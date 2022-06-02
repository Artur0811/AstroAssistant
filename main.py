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
color: rgb(248, 248, 255);background: rgb(28, 28, 28);
}
QComboBox {
color: rgb(248, 248, 255);border: 2px solid rgb(248, 248, 255);background: rgb(28, 28, 28);
}
QComboBox QAbstractItemView {
color: rgb(248, 248, 255);border: 2px solid rgb(248, 248, 255);background: rgb(28, 28, 28);
}
'''

class LightCurve:
    def __init__(self, per, path, on, by, epoch, filter, new_fiel):
        self.period = per
        self.path = path
        self.val_on = on
        self.by = by
        self.epoch = epoch
        self.filter = filter
        self.new_fiel = new_fiel
    def make_epoch(self, ep):
        m = float(self.epoch)
        while True:
            s = (m - ep) / float(self.period)
            s_c = round(s) - 1
            if -0.01<(s- s_c)%1 < 0.01:
                return m
            else:
                m+=0.01

    def make_LightCurve_not_per(self):
        with open(self.path) as f:
            a = f.read().split("\n")
        if self.by ==  "ZTF":
            c = self.new_fiel + "\ "[0] +self.by+self.filter+".txt"
            b = c
            with open(b, "w") as f:
                for i in range(17, len(a)):
                    if a[i]!= '':
                        f.writelines(a[i].split()[3].replace("00000", "")+ " " + (a[i].split()[4])+ "\n")
        if self.by == "Atlass":
            o = self.new_fiel+'\ '[0]+self.by+'o.txt'
            o1 = o
            c = self.new_fiel+'\ '[0] +self.by+'c.txt'
            c1 = c
            with open(o1,'w') as f1:
                with open(c1,'w') as f2:
                    for i in range(1, len(a)):
                        if a[i] != '':
                            r = a[i].split()
                            print(r[1])
                            if '-' not in r[1] and len(r[3]) <6:
                                if r[5] == 'c':
                                    f2.writelines(r[0] +' '+ r[1]+'\n')
                                if r[5] == "o":
                                    f1.writelines(r[0] +' '+ r[1]+'\n')

        else:
            pass
    def  make_LightCurve_with_per(self):
        with open(self.path) as f:
            a = f.read().split("\n")
        c = self.new_fiel + "\ "[0] + self.by + self.filter + "P.txt"
        b = c
        if self.val_on == "Минимуме":
            min_ = [0, 0]
            if self.by == "ZTF":
                for i in range(17, len(a)):
                    if a[i] != '':
                        a[i] = [a[i].split()[3], a[i].split()[4].replace("00000", "")]
                        if float(a[i][1]) > min_[1]:
                            min_ = [float(a[i][0]), float(a[i][1])]
                correct_epoch = self.make_epoch(min_[0])
        else:
            max_ = [30, 30]
            if self.by == "ZTF":
                for i in range(17, len(a)):
                    if a[i] != '':
                        a[i] = [a[i].split()[3], a[i].split()[4].replace("00000", "")]
                        if float(a[i][1]) < max_[1]:
                            max_ = [float(a[i][0]), float(a[i][1])]
                correct_epoch = self.make_epoch(max_[0])
            if self.by == "Atlass":
                for i in range(17, len(a)):
                    r = a[i].split()
                    if a[i] != '' and "-" not in r[1] and float(r[2]) < 1.5 and len(r[3]) < 6:
                        a[i] = [r[0], r[1], r[5]]
                        if float(a[i][1]) < max_[1]:
                            max_ = [float(a[i][0]), float(a[i][1])]
                correct_epoch = self.make_epoch(max_[0])

                ft1= self.new_fiel + "\ "[0] + self.by + "oP.txt"
                ft2 = self.new_fiel + "\ "[0] + self.by + "cP.txt"
                f1 = ft1
                f2 = ft2
                with open(f1, "w") as f1:
                    with open(f2, "w") as f2:
                        for i in range(1, len(a)):
                            if a[i] != '':
                                rez = (float(a[i][0]) - correct_epoch) / float(self.period)
                                rez_c = round(rez) - 1
                                if a[i][2] == "c":
                                    f2.writelines(str(rez - rez_c)[:8] + " " + a[i][1] + '\n')
                                    f2.writelines(str(rez - rez_c-1)[:8] + " " + a[i][1] + '\n')
                                else:
                                    f1.writelines(str(rez - rez_c)[:8] + " " + a[i][1] + '\n')
                                    f1.writelines(str(rez - rez_c - 1)[:8] + " " + a[i][1] + '\n')


        if self.by != "Atlass":
            with open(b, "w") as f:
                for i in range(17, len(a)):
                    if a[i] != "":
                        rez = (float(a[i][0]) - correct_epoch) / float(self.period)
                        rez_c = round(rez) - 1
                        f.writelines(str(rez - rez_c)[:8] + " " + a[i][1] + '\n')
                        f.writelines(str(rez - rez_c-1)[:8] + " " + a[i][1] + '\n')
        return correct_epoch

class vari(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(500, 400, 500, 400)

        self.btn_Reg = QPushButton(self)
        self.btn_Reg.setText("REGISTR")
        self.btn_Reg.setGeometry(50, 50, 175, 300)

        self.btn_OBR = QPushButton(self)
        self.btn_OBR.setText("OBR")
        self.btn_OBR.setGeometry(275, 50, 175, 300)

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
        self.butn.move(325, 400)

    def start(self):
        with open("seting.txt", "w") as f:
            f.writelines(self.star_line_in.text()+"\n")
            f.writelines(self.Fiel_line_in.text())
        self.close()

class errWind(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setGeometry(500, 400, 400, 250)
        self.setStyleSheet('background: rgb(248, 248, 255);')
        self.setWindowTitle('ERR')

        self.btn = QPushButton(self)
        self.btn.setText("OK")
        self.btn.satGeometry(400, 300, 100, 30)
        self.btn.clicked.connect(self.ok)

    def ok(self):
        self.close()

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        user = ctypes.windll.user32
        self.x = user.GetSystemMetrics(0)
        self.y = user.GetSystemMetrics(1)
        with open("seting.txt") as f:
            self.name_per_fiel = f.read().split("\n")[1]
        self.err_key = 0

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

        self.line_Epoch_in = QLineEdit(self)
        self.line_Epoch_in.move(300, 150)
        self.line_Epoch_in.setMaxLength(50)

        self.line_F = QLabel(self)
        self.line_F.setText("Fiel path:")
        self.line_F.move(100, 200)

        self.line_F_in = QLineEdit(self)
        self.line_F_in.move(300, 200)
        self.line_F_in.setMaxLength(80)

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

        self.data_line= QLabel(self)
        self.data_line.setText("Данные от:")
        self.data_line.move(100, 250)

        self.data_box = QComboBox(self)
        self.data_box.setGeometry(300, 250, 100, 25)
        self.data_box.addItem("Atlass")
        self.data_box.addItem("ZTF")
        self.data_box.addItem("Other")

        self.val_Ep = QLabel(self)
        self.val_Ep.setText("Исправленная Epoch:")
        self.val_Ep.move(100, 300)

        self.val_Ep_in = QLineEdit(self)
        self.val_Ep_in.move(300, 300)

        self.type_line = QLabel(self)
        self.type_line.move(100, 350)
        self.type_line.setText("Ноль в:")

        self.type_box = QComboBox(self)
        self.type_box.move(300, 350)
        self.type_box.resize(100, 25)
        self.type_box.addItem("Максимуме")
        self.type_box.addItem("Минимуме")

        self.filter_box = QComboBox(self)
        self.filter_box.setGeometry(300, 400, 100, 25)
        self.filter_box.addItems(["g", "r", "o", "c"])

        self.filter_line = QLabel(self)
        self.filter_line.setText("Filter")
        self.filter_line.move(100, 400)

    def claer(self):
        self.line_F_in.clear()
        self.line_coord_in.clear()
        self.line_Epoch_in.clear()
        self.line_Per_in.clear()

    def count(self):
        if self.line_F_in.text() == "" or self.line_F_in.text() == "Обязательное поле":
            self.line_F_in.setText("Обязательное поле")
            self.line_F_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.err_key =1
        else:
            self.line_F_in.setStyleSheet('background: rgb(248, 248, 255);')
            if self.line_Epoch_in.text() == "" and self.line_Per_in.text() != "" or self.line_Epoch_in.text() == "Обязательное поле" and self.line_Per_in.text() != "":
                self.line_Epoch_in.setText("Обязательное поле")
                self.line_Epoch_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
                self.line_Per_in.setStyleSheet('background: rgb(248, 248, 255);')
                self.err_key =2

            elif self.line_Epoch_in.text() != "" and self.line_Per_in.text() == "" or self.line_Epoch_in.text() != "" and self.line_Per_in.text() == "Обязательное поле":
                self.line_Per_in.setText("Обязательное поле")
                self.line_Epoch_in.setStyleSheet('background: rgb(248, 248, 255);')
                self.err_key = 3
                self.line_Per_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")

            elif self.line_Epoch_in.text() != "" and self.line_Per_in.text() != "":
                self.err_key =0

                otvet = LightCurve(self.line_Per_in.text(), self.line_F_in.text(), self.type_box.currentText(),
                                   self.data_box.currentText(), self.line_Epoch_in.text(),
                                   self.filter_box.currentText(), self.name_per_fiel)
                rezult = otvet.make_LightCurve_with_per()
                self.val_Ep_in.setText(str(rezult)[:10])

            else:
                otvet = LightCurve("",self.line_F_in.text(), "", self.data_box.currentText(), "",self.filter_box.currentText() ,self.name_per_fiel)
                otvet.make_LightCurve_not_per()

    def dark(self):
        if self.butn3.text() == "Dark":
            self.butn3.setText("White")
            self.setStyleSheet(setstell1)
            self.line_Per_in.setStyleSheet('color: rgb(248, 248, 255);background: rgb(28, 28, 28);')
            self.line_F_in.setStyleSheet('color: rgb(248, 248, 255);background: rgb(28, 28, 28);')
            self.line_Epoch_in.setStyleSheet('color: rgb(248, 248, 255);background: rgb(28, 28, 28);')
            if self.err_key == 1:
                self.line_F_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.err_key ==2:
                self.line_Epoch_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.err_key == 3:
                self.line_Per_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
        else:
            self.butn3.setText("Dark")
            self.setStyleSheet('background: rgb(248, 248, 255);')
            self.line_Per_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.line_F_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.line_Epoch_in.setStyleSheet('background: rgb(248, 248, 255);')
            if self.err_key == 1:
                self.line_F_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.err_key ==2:
                self.line_Epoch_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.err_key == 3:
                self.line_Per_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")


class win(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()

    def w1(self):
        self.w1 = setting()
        with open("seting.txt") as f:
            if f.read() == "":
                self.w1.butn.clicked.connect(self.w1.start)
                self.w1.show()
                self.w1.butn.clicked.connect(self.w2)
            else:
                self.w2()

    def w2(self):
        self.w2 = Example()
        self.w2.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    st = win()
    st.w1()
    sys.exit(app.exec())
