import sys, ctypes,math
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QMainWindow, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QLabel, QLineEdit, QCheckBox, QPlainTextEdit, QFileDialog
from PyQt5.QtGui import QPixmap
import seaborn as sns
import matplotlib.pyplot as pyp
import pandas as pn
from PyQt5.QtCore import pyqtSignal, QObject
from random import randrange
import os
from os import makedirs
import requests
import re
import csv
from PIL import Image, ImageDraw, ImageFont, ImageOps
from astropy.io import fits


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
QPlainTextEdit {
color: rgb(248, 248, 255);border: 2px solid rgb(248, 248, 255);background: rgb(28, 28, 28);
}
'''


def Lafler_clinman(name, max = True):
    with open(name) as f:
        if max:
            ma = 32
        else:
            ma = -32
        ep0 = 0
        m = []
        for i in f:
            m.append(list(map(float, i.split())))
            if m[-1][1] < ma and max:
                ma = m[-1][1]
                ep0 = m[-1][0]
            elif m[-1][1] > ma and not(max):
                ma = m[-1][1]
                ep0 = m[-1][0]
        pmin = 1
        pmax = 1000
        wmin = 1 / pmax
        wmax = 1 / pmin
        step = 0.00001

        def drob(n):
            return n - math.floor(n)

        p = []

        def LK1(a):
            s = 0
            for i in range(len(a)):
                s += (a[i][1] - a[i - 1][1]) ** 2
            return s

        while wmin <= wmax:
            b = []
            for i in range(len(m)):
                b.append([drob((m[i][0] - ep0) * wmin), m[i][1]])
            b = sorted(b, key=lambda x: x[0])
            p.append([LK1(b), 1 / wmin])
            wmin += step

        p = sorted(p, key=lambda x: x[0])
        per_n = p[0][1]
    return round(per_n, 7), ep0

class OtherName:
    def __init__(self, cor):
        self.silka = "https://vizier.u-strasbg.fr/viz-bin/VizieR-4?-mime=html&-source=USNO-A2.0,GSC2.2,IPHAS,USNO-B1.0,GSC2.3,URAT1,2MASS,SDSS,WISE,II/335/galex_ais&-c="+cor+"&-c.rs=4"
        self.other = []
    def getname(self):
        req = requests.get(self.silka)
        a = req.text
        a = a.split()
        for i in range(len(a)):
            if "urat1&amp" in a[i]:
                if 'NOWRAP' in a[i+3]:
                    self.other.append(["URAT1", a[i+3][7:17]])
            if a[i].count("galex_ais")==1 and a[i+7] == "NOWRAP>GALEX" and "J" in a[i+8]:
                self.other.append(["GALEX", a[i+8][:-5]])
            if "===" in a[i] and "AllWISE" not in a[i]:
                b = a[i].split(";")
                b = re.split("===|&|'", b[3])
                if "%2b" in b[1]:
                    b[1] = r"{}+{}".format(*b[1].split("%2b"))
                self.other.append([b[0], b[1]])
        return self.other

class ZTF_Points:
    def __init__(self, coord, fiel_name, mag = True):#на вход координаты и путь куда будут сохраняться файлы / mag - если true то ищет магнитуду дополнительео выводит масив макс зн \мин зн\ фильтр
        self.fiel_name = fiel_name #куда сохраняю файл
        self.ssilka1 = "https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?spatial=box&catalog=ztf_objects_dr12&objstr={}h+{}m+{}s+{}d+{}m+{}s&size=10&outfmt=1".format(*coord.split())
        #запрос к ztf из которого я получаю какие именно данные наблюдений мне нужно запрасить в дальнейшем
        self.ssilka2 = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?ID={}"#запрос данных
        self.mag = mag
    def points(self):#
        rec = requests.get(self.ssilka1)#делаю запрос по координатам
        b = rec.text.split()
        #т.к я делаю запрос по итогу которого мне могут выдать не те звезды то я беру центр своего запроса в градусах
        for i in range(len(b)):
            if "\SKYAREA" ==b[i]:
                ra, dec = map(float, b[i+5][1:-1].split(","))#центр запроса. Нужен чтобы определить бижайшие звезды
                b = b[i+369:]
                break
        name_g = []
        name_r = []

        for i in range(len(b)):
            if i%23==0:
                if ((float(b[i+1])-ra)**2+(float(b[i+2])-dec)**2)**0.5*3600 <1.5:#проверяю чтобы выбранные данные были ближе 1.5 арксек
                    if b[i+8][1] =="g":#данные фильтра g
                        name_g.append([b[i], int(b[i+12])])
                    if b[i+8][1] == "r":#данные фильтра r
                        name_r.append([b[i], int(b[i+12])])
        ret = []#имена файлов которые я создал. В файлах содержатся данные конкретного фильтра
        if self.mag:
            magn = []
        if name_g != []:
            if self.mag:#
                g_mag = [100, -100, "g"]
            ret.append('ztf_g.txt')#записываю что сделал файл с наблюдениями в фильтре g
            name_g = max(name_g, key=lambda x:x[1])[0]#выбираю тот набор в котором больше всего наблюдений
            data = requests.get(self.ssilka2.format(name_g)).text.split()#получаю данные наблюдений
            with open(self.fiel_name+"\ztf_g.txt", "w") as f:
                for i in range(len(data)):
                    if data[i] == "<TR>":
                        f.writelines(re.split("<|>", data[i + 4])[2][:12] + " " + re.split("<|>", data[i + 5])[2][:6] + "\n")#записываю наблюдения в формате дата/наблюдение
                        if self.mag:
                            if float(re.split("<|>", data[i + 5])[2][:6]) < g_mag[0] and len(data[i + 7])<11:#код ошибки наблюдений на i+7
                                g_mag[0]=float(re.split("<|>", data[i + 5])[2][:6])
                            if float(re.split("<|>", data[i + 5])[2][:6]) > g_mag[1] and len(data[i + 7])<11:
                                g_mag[1] = float(re.split("<|>", data[i + 5])[2][:6])
            if self.mag:
                magn.append(g_mag)

        if name_r != []:
            if self.mag:#
                r_mag = [100, -100, "r"]
            ret.append('ztf_r.txt')#записываю что сделал файл с наблюдениями в фильтре r
            name_r = max(name_r, key=lambda x: x[1])[0]#выбираю тот набор в котором больше всего наблюдений
            data = requests.get(self.ssilka2.format(name_r)).text.split()#получаю данные наблюдений
            with open(self.fiel_name + "\ztf_r.txt", "w") as f:
                for i in range(len(data)):
                    if data[i] == "<TR>":
                        f.writelines(re.split("<|>", data[i + 4])[2][:12] + " " + re.split("<|>", data[i + 5])[2][:6] + "\n")#записываю наблюдения в формате дата/наблюдение
                        if self.mag:
                            if float(re.split("<|>", data[i + 5])[2][:6]) < r_mag[0] and len(data[i + 7])<11:
                                r_mag[0]=float(re.split("<|>", data[i + 5])[2][:6])
                            if float(re.split("<|>", data[i + 5])[2][:6]) > r_mag[1] and len(data[i + 7])<11:
                                r_mag[1] = float(re.split("<|>", data[i + 5])[2][:6])
            if self.mag:
                magn.append(r_mag)
        if self.mag:
            return ret ,max(magn, key=lambda x: abs(x[0]- x[1]))
        return ret

class makeGrapf:#создает график из данных файла. формат данных в фале 2 сторки. ось x ось у
    def __init__(self, path, savef, name, phase=False):#массив с путями к файлам\куда сохранять\название сохраняемого файла\фазовый или обычный график
        self.path = path
        self.name = name
        self.savef = savef
        self.phase = phase
    def make(self):
        ymin = 99
        ymax = 0
        with open(self.savef+"\data.csv", "w") as fi:
            fiel = csv.writer(fi)
            fiel.writerow(["x", "y", "data"])
            for i in range(len(self.path)):
                x = []
                y = []
                fil = self.path[i][1]
                with open(self.path[i][0]) as f:
                    for i in f:
                        x.append(float(i.split()[0]))
                        y.append(float(i.split()[1]))
                        fiel.writerow([str(i.split()[0]), str(i.split()[1]), fil])
                mi, ma = min(y), max(y)
                if mi < ymin:
                    ymin = mi
                if ma > ymax:
                    ymax = ma
            data = pn.read_csv(self.savef+"\data.csv")
            color = dict({"r":"#f80000", "g":"#000080", "c" : "#40734f",  "o":"#f5770a"})
            g = sns.scatterplot(data =data, x="x", y="y", hue= "data", palette=color)
        g.figure.set_figwidth(12)
        g.figure.set_figheight(8)
        pyp.ylim(ymax+0.5, ymin-0.5)
        if self.phase:
            pyp.xlim(-0.5, 1)
            pyp.title(self.name, fontsize=23)
            pyp.ylabel("Magnitude", fontsize=18)
            pyp.xlabel("Phase", fontsize=18)
        else:
            pyp.title(self.name, fontsize=23)
            pyp.ylabel("Magnitude", fontsize=18)
            pyp.xlabel("MJD", fontsize=18)
        pyp.savefig(self.savef+"\ "[0]+self.name+".png")
        pyp.close()


class LightCurve:
    def __init__(self, per, path, on, by, epoch, filter, new_fiel, make = False):
        #период\путь к файлу\где должен быть 0 фазы в макс или мин знач\от кого данные\эпоха\какой фильтр\куда сохранять новый файл\ делать график или нет
        self.period = per
        self.path = path
        self.val_on = on
        self.by = by
        self.epoch = epoch
        self.filter = filter
        self.new_fiel = new_fiel
        self.make = make
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
            b = self.new_fiel + "\ "[0] +self.by+self.filter+".txt"
            with open(b, "w") as f:
                for i in range(17, len(a)):
                    if a[i]!= '':
                        f.writelines(a[i].split()[3].replace("00000", "")+ " " + (a[i].split()[4])+ "\n")
            if self.make:
                g = makeGrapf([[b, self.filter]], self.new_fiel, "preview")
                g.make()
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
                            if '-' not in r[1] and len(r[3]) <6:
                                if r[5] == 'c':
                                    f2.writelines(r[0] +' '+ r[1]+'\n')
                                if r[5] == "o":
                                    f1.writelines(r[0] +' '+ r[1]+'\n')
            if self.make:
                g1 = makeGrapf([[o1, "o"],[c1, "c"]], self.new_fiel, "preview")
                g1.make()
        if self.by == "Other":
            c = self.new_fiel + "\ "[0] + self.by + self.filter + ".txt"
            b = c
            with open(b, "w") as f:
                for i in range(17, len(a)):
                    if a[i] != '':
                        f.writelines(a[i].split()[0] + " " + a[i].split()[1] + "\n")
            if self.make:
                g = makeGrapf([[b, self.filter]], self.new_fiel, "preview")
                g.make()
    def  make_LightCurve_with_per(self, fep = True):
        with open(self.path) as f:
            a = f.read().split("\n")
        c = self.new_fiel + "\ "[0] + self.by + self.filter + "P.txt"
        b = c
        if self.val_on == "Минимуме":
            min_ = [0, 0]
            if self.by == "ZTF":
                a = a[17:]
                for i in range(len(a)):
                    if a[i] != '':
                        a[i] = [a[i].split()[3], a[i].split()[4].replace("00000", "")]
                        if float(a[i][1]) > min_[1]:
                            min_ = [float(a[i][0]), float(a[i][1])]
                if fep:
                    correct_epoch = self.make_epoch(min_[0])
                else:
                    correct_epoch = float(self.epoch)

            if self.by == "Other":
                min_ = [0, 0]
                for i in range(len(a)):
                    if a[i]!= "":
                        k = a[i].split()
                        a[i] = [float(k[0]), k[1]]
                        if float(a[i][1]) > float(min_[1]):
                            min_ = a[i]
                if fep:
                    correct_epoch = self.make_epoch(float(min_[0]))
                else:
                    correct_epoch = float(self.epoch)
        else:
            max_ = [30, 30]
            if self.by == "ZTF":
                a = a[17:]
                for i in range(len(a)):
                    if a[i] != '':
                        a[i] = [a[i].split()[3], a[i].split()[4].replace("00000", "")]
                        if float(a[i][1]) < max_[1]:
                            max_ = [float(a[i][0]), float(a[i][1])]
                if fep:
                    correct_epoch = self.make_epoch(max_[0])
                else:
                    correct_epoch = float(self.epoch)

            if self.by == "Other":
                for i in range(len(a)):
                    if a[i] != "":
                        k = a[i].split()
                        a[i] = [float(k[0]), k[1]]
                        if float(a[i][1]) < float(max_[1]):
                            max_ = a[i]
                if fep:
                    correct_epoch = self.make_epoch(float(max_[0]))
                else:
                    correct_epoch = float(self.epoch)
            if self.by == "Atlass":
                for i in range(17, len(a)):
                    r = a[i].split()
                    if a[i] != '' and "-" not in r[1] and float(r[2]) < 1.5 and len(r[3]) < 6:
                        a[i] = [r[0], r[1], r[5]]
                        if float(a[i][1]) < max_[1]:
                            max_ = [float(a[i][0]), float(a[i][1])]
                if fep:
                    correct_epoch = self.make_epoch(max_[0])
                else:
                    correct_epoch = float(self.epoch)

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
        if self.by != "Atlas":
            with open(b, "w") as f:
                for i in range(len(a)):
                    if a[i] != "":
                        rez = (float(a[i][0]) - correct_epoch) / float(self.period)
                        rez_c = math.floor(rez)
                        f.writelines(str(rez - rez_c)[:8] + " " + a[i][1] + '\n')
                        f.writelines(str(rez - rez_c - 1)[:8] + " " + a[i][1] + '\n')

        if self.make:
            g = makeGrapf([[b, self.filter]], self.new_fiel, "preview", phase=True)
            g.make()
        return correct_epoch

def is_foat(a):
    if a.count(".")>1:
        return False
    a =a.split(".")
    if len(a)==1:
        return a[0].isdigit()
    return a[0].isdigit() and a[1].isdigit()

class vari(QWidget):
    def __init__(self):
        super().__init__()
        self.layoutGrid = QGridLayout()
        self.setLayout(self.layoutGrid)
        self.initUI()

    def initUI(self):
        user = ctypes.windll.user32
        self.setGeometry(user.GetSystemMetrics(0)//2-250, user.GetSystemMetrics(1)//2-200, 725, 400)
        self.setStyleSheet('background: rgb(248, 248, 255);')
        self.setMinimumSize(725, 400)

        self.btn_Reg = QPushButton(self)
        self.btn_Reg.setText("REGISTR")
        self.btn_Reg.setGeometry(50, 50, 175, 300)

        self.btn_OBR = QPushButton(self)
        self.btn_OBR.setText("Fiel")
        self.btn_OBR.setGeometry(275, 50, 175, 300)

        self.plate_OBR = QPushButton(self)
        self.plate_OBR.setText("Plates")
        self.plate_OBR.setGeometry(500, 50, 175, 300)

class setting(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.successfully =False

    def initUI(self):
        self.setGeometry(600, 200, 700, 600)
        self.setWindowTitle('Setting')
        self.setStyleSheet('background: rgb(248, 248, 255);')

        self.Fiel_line = QLabel(self)
        self.Fiel_line.setText("Set path form periods program fiel:")
        self.Fiel_line.move(100, 50)

        self.Fiel_line_in = QLineEdit(self)
        self.Fiel_line_in.setGeometry(100, 75, 200, 25)
        self.Fiel_line_in.setMaxLength(50)

        self.Fiel_line_choice = QPushButton(self)
        self.Fiel_line_choice.setGeometry(300, 75, 50, 25)
        self.Fiel_line_choice.setText("Select")
        self.Fiel_line_choice.clicked.connect(self.file_choice)

        self.star_line = QLabel(self)
        self.star_line.setText("Set path form star fiel:")
        self.star_line.move(100, 150)

        self.star_line_in = QLineEdit(self)
        self.star_line_in.setGeometry(100, 175, 200, 25)
        self.star_line_in.setMaxLength(50)

        self.star_line_choice = QPushButton(self)
        self.star_line_choice.setGeometry(300, 175, 50, 25)
        self.star_line_choice.setText("Select")
        self.star_line_choice.clicked.connect(self.star_choice)

        self.min_period_text = QLabel(self)
        self.min_period_text.setGeometry(100, 250, 75, 25)
        self.min_period_text.setText("Min period:")

        self.min_period_in = QLineEdit(self)
        self.min_period_in.setGeometry(175, 250, 100, 25)
        self.min_period_in.setText("1")

        self.max_period_text = QLabel(self)
        self.max_period_text.setGeometry(300, 250, 75, 25)
        self.max_period_text.setText("Max period:")

        self.max_period_in = QLineEdit(self)
        self.max_period_in.setGeometry(375, 250, 100, 25)
        self.max_period_in.setText("1000")

        self.step_period_text = QLabel(self)
        self.step_period_text.setGeometry(100, 350, 75, 25)
        self.step_period_text.setText("Step period:")

        self.step_period_in = QLineEdit(self)
        self.step_period_in.setGeometry(175, 350, 100, 25)
        self.step_period_in.setText("0.00001")

        self.butn = QPushButton(self)
        self.butn.setText("ok")
        self.butn.setGeometry(300, 425, 100, 50)

    def chek_value(self):
        if not(os.path.isdir(self.Fiel_line_in.text())):
            self.Fiel_line_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.star_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.min_period_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.max_period_in.setStyleSheet('background: rgb(248, 248, 255);')
        elif not(os.path.isdir(self.star_line_in.text())):
            self.Fiel_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.star_line_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.min_period_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.max_period_in.setStyleSheet('background: rgb(248, 248, 255);')
        elif not(is_foat(self.max_period_in.text())):
            self.Fiel_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.star_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.min_period_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.max_period_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
        elif not(is_foat(self.min_period_in.text())):
            self.Fiel_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.star_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.min_period_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.max_period_in.setStyleSheet('background: rgb(248, 248, 255);')
        elif float(self.min_period_in.text()) > float(self.max_period_in.text()):
            self.Fiel_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.star_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.min_period_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.max_period_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
        elif float(self.min_period_in.text()) == 0:
            self.Fiel_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.star_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.min_period_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.max_period_in.setStyleSheet('background: rgb(248, 248, 255);')
        else:
            self.successfully = True

    def start(self):
        with open("seting.txt", "w") as f:
            f.writelines(self.star_line_in.text()+"\n")
            f.writelines(self.Fiel_line_in.text()+"\n")
            f.writelines("Min_period " + self.min_period_in.text() + "\n")
            f.writelines("Max_period " + self.max_period_in.text() + "\n")
            f.writelines("Step_period " + self.step_period_in.text())

    def file_choice(self):
        self.Fiel_line_in.setText(QFileDialog().getExistingDirectory(self))
    def star_choice(self):
        self.star_line_in.setText(QFileDialog().getExistingDirectory(self))

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

class previewwin(QWidget):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 1220, 820)
        self.setWindowTitle('Preview')
        self.setStyleSheet('background: rgb(248, 248, 255);')

        self.lab = QLabel(self)
        self.lab.move(10, 10)
        self.pi = QPixmap(self.path)
        self.setGeometry(0, 0, self.pi.width()+20, self.pi.height()+20)
        self.lab.setPixmap(self.pi)


class OBRwin(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        user = ctypes.windll.user32
        self.x = user.GetSystemMetrics(0)
        self.y = user.GetSystemMetrics(1)
        with open("seting.txt") as f:
            self.name_per_fiel = f.read().split("\n")[1]
        self.err_key = 0
        self.make = False

    def initUI(self):
        user = ctypes.windll.user32
        self.setGeometry(0, 0, user.GetSystemMetrics(0), user.GetSystemMetrics(1))
        self.setWindowTitle('Звёздный помошник')
        self.setStyleSheet('background: rgb(248, 248, 255);')

        self.line_Per = QLabel(self)
        self.line_Per.setText("Period (d):")
        self.line_Per.move(100, 50)

        self.line_Per_in = QLineEdit(self)
        self.line_Per_in.setGeometry(300, 50, 200, 25)

        self.line_E = QLabel(self)
        self.line_E.setText("Epoch:")
        self.line_E.move(100, 100)

        self.line_Epoch_in = QLineEdit(self)
        self.line_Epoch_in.setGeometry(300, 100, 200, 25)
        self.line_Epoch_in.setMaxLength(50)

        self.line_F = QLabel(self)
        self.line_F.setText("Fiel path:")
        self.line_F.move(100, 150)

        self.line_F_in = QLineEdit(self)
        self.line_F_in.setGeometry(300, 150, 200, 25)
        self.line_F_in.setMaxLength(80)

        self.line_btn = QPushButton(self)
        self.line_btn.setGeometry(500, 150, 50,25)
        self.line_btn.setText("Select")
        self.line_btn.clicked.connect(self.get_txt)

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

        self.butn4 = QPushButton("Preview", self)
        self.butn4.setGeometry(1700, 200, 100, 50)
        self.butn4.clicked.connect(self.preview)

        self.data_line= QLabel(self)
        self.data_line.setText("Данные от:")
        self.data_line.move(100, 200)

        self.data_box = QComboBox(self)
        self.data_box.setGeometry(300, 200, 100, 25)
        self.data_box.addItem("Atlass")
        self.data_box.addItem("ZTF")
        self.data_box.addItem("Other")

        self.val_Ep = QLabel(self)
        self.val_Ep.setText("Исправленная Epoch:")
        self.val_Ep.move(100, 250)

        self.val_Ep_in = QLineEdit(self)
        self.val_Ep_in.setGeometry(300, 250, 200, 25)

        self.type_line = QLabel(self)
        self.type_line.move(100, 300)
        self.type_line.setText("Ноль в:")

        self.type_box = QComboBox(self)
        self.type_box.move(300, 300)
        self.type_box.resize(100, 25)
        self.type_box.addItem("Максимуме")
        self.type_box.addItem("Минимуме")

        self.filter_box = QComboBox(self)
        self.filter_box.setGeometry(300, 350, 100, 25)
        self.filter_box.addItems(["g", "r", "o", "c"])

        self.filter_line = QLabel(self)
        self.filter_line.setText("Filter")
        self.filter_line.move(100, 350)

        self.beak_btn = QPushButton(self)
        self.beak_btn.setText("Beak")
        self.beak_btn.setGeometry(1700, 150, 100, 50)

        self.make_grath_true = QCheckBox(self)
        self.make_grath_true.move(300, 400)
        self.make_grath_true.clicked.connect(self.make_g)

        self.make_grath = QLabel(self)
        self.make_grath.move(100, 400)
        self.make_grath.setText("Make grath")
    def claer(self):
        self.line_F_in.clear()
        self.line_Epoch_in.clear()
        self.line_Per_in.clear()
        self.val_Ep_in.clear()

    def make_g(self):
        if self.make:
            self.make = False
        else:
            self.make = True

    def get_txt(self):
        self.line_F_in.setText(QFileDialog().getOpenFileName(self, "Open project", "", "Text Files (*.txt *.tbl)")[0])

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
                                   self.filter_box.currentText(), self.name_per_fiel, self.make)
                rezult = otvet.make_LightCurve_with_per()
                self.val_Ep_in.setText(str(rezult)[:10])

            else:
                otvet = LightCurve("",self.line_F_in.text(), "", self.data_box.currentText(), "",self.filter_box.currentText() ,self.name_per_fiel, make=self.make)
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

    def preview(self):
        a = self.make
        self.make = True
        self.count()
        self.make = a
        if self.err_key == 0:
            a = self.name_per_fiel+"/"+"preview.png"
            self.wp = previewwin(a)
            self.wp.show()

class registrWin(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ZTF_f = True
        self.PANSTARRS_F = False
        with open("seting.txt") as f:
            self.path_star = f.readline().split("\n")[0]
        self.key_err = 0

    def initUI(self):
        user = ctypes.windll.user32
        self.setGeometry(0, 0, user.GetSystemMetrics(0), user.GetSystemMetrics(1))
        self.setWindowTitle('Звёздный помошник')
        self.setStyleSheet('background: rgb(248, 248, 255);')

        self.dark_btn = QPushButton(self)
        self.dark_btn.setText("Dark")
        self.dark_btn.setGeometry(1700, 100, 100, 50)
        self.dark_btn.clicked.connect(self.dark)

        self.beak_btn = QPushButton(self)
        self.beak_btn.setText("Beak")
        self.beak_btn.setGeometry(1700, 150, 100, 50)

        self.clear_btn = QPushButton(self)
        self.clear_btn.setGeometry(1700, 50, 100, 50)
        self.clear_btn.setText("Clear")
        self.clear_btn.clicked.connect(self.clear_line)

        self.file_btn = QPushButton(self)
        self.file_btn.setText("Create file")
        self.file_btn.clicked.connect(self.create_file)
        self.file_btn.setGeometry(800, 500, 100, 50)

        self.star_name = QLabel(self)
        self.star_name.setText("Имя звезды")
        self.star_name.move(100, 50)

        self.star_name_in = QLineEdit(self)
        self.star_name_in.setGeometry(300, 50, 200, 25)
        self.star_name_in.setMaxLength(25)

        self.coor_line = QLabel(self)
        self.coor_line.setText("Координаты")
        self.coor_line.move(100, 100)

        self.coor_line_in = QLineEdit(self)
        self.coor_line_in.setGeometry(300, 100, 200, 25)
        self.coor_line_in.setMaxLength(30)

        self.oth_name = QLabel(self)
        self.oth_name.setText("Другие имена")
        self.oth_name.move(100, 150)

        self.oth_name_in = QPlainTextEdit(self)
        self.oth_name_in.setGeometry(300, 150, 200, 225)

        self.type_line = QLabel(self)
        self.type_line.setText("Тип")
        self.type_line.move(100, 400)

        self.type_line_in_n = QLineEdit(self)
        self.type_line_in_n.setGeometry(300, 400, 200, 25)

        self.type_line_in = QComboBox(self)
        self.type_line_in.addItems(["EA","EB","EW", "UG", "UGSU", "UGSS", "RR", "RS", "M", "BY", "RRC", "RRB", "L"])
        self.type_line_in.move(150, 400)

        self.max_mag = QLabel(self)
        self.max_mag.setText("Максимальная магнитуда")
        self.max_mag.move(100, 450)

        self.max_mag_in = QLineEdit(self)
        self.max_mag_in.setGeometry(300, 450, 100, 25)

        self.max_mag_filter = QComboBox(self)
        self.max_mag_filter.addItems(["g", "r", "o", "c", "i", "y", "z"])
        self.max_mag_filter.setGeometry(400, 450, 100, 25)

        self.min_mag = QLabel(self)
        self.min_mag.setText("Минимальная магнитуда")
        self.min_mag.move(100, 500)

        self.min_mag_in = QLineEdit(self)
        self.min_mag_in.setGeometry(300, 500, 100, 25)

        self.min_mag_filter = QComboBox(self)
        self.min_mag_filter.addItems(["g", "r", "o", "c","i", "y", "z"])
        self.min_mag_filter.setGeometry(400, 500, 100, 25)

        self.per_line = QLabel(self)
        self.per_line.setText("Период:")
        self.per_line.move(100, 550)

        self.per_line_in = QLineEdit(self)
        self.per_line_in.setGeometry(300, 550, 200, 25)

        self.Epoch_line = QLabel(self)
        self.Epoch_line.setText("Эпоха (MGD):")
        self.Epoch_line.move(100, 600)

        self.Epoch_line_in = QLineEdit(self)
        self.Epoch_line_in.setGeometry(300, 600, 200, 25)

        self.eclipse_line = QLabel(self)
        self.eclipse_line.move(100, 650)
        self.eclipse_line.setText("% затмения")

        self.eclipse_line_in = QLineEdit(self)
        self.eclipse_line_in.setGeometry(300, 650, 200, 25)

        self.ztf_rem = QLabel(self)
        self.ztf_rem.setText("ZTF Remark")
        self.ztf_rem.move(100, 700)

        self.ztf_rem_ok = QCheckBox(self)
        self.ztf_rem_ok.move(250, 700)
        self.ztf_rem_ok.toggle()
        self.ztf_rem_ok.clicked.connect(self.ZTF)

        self.panstarrs_rem = QLabel(self)
        self.panstarrs_rem.setText("PanSTARRS Remark")
        self.panstarrs_rem.move(310, 700)

        self.panstarrs_rem_ok = QCheckBox(self)
        self.panstarrs_rem_ok.move(485, 700)
        self.panstarrs_rem_ok.clicked.connect(self.PanStarrs)

        self.comm_line = QLabel(self)
        self.comm_line.setText("Revizion comment")
        self.comm_line.move(100, 750)

        self.comm_line_in = QPlainTextEdit(self)
        self.comm_line_in.setGeometry(300, 750, 200, 225)
        self.comm_line_in.setPlainText("GaiaEDR3 position.")

    def dark(self):
        if self.dark_btn.text() == "Dark":
            self.dark_btn.setText("White")
            self.setStyleSheet(setstell1)
            if self.key_err == 1:
                self.star_name_in.setStyleSheet("color: rgb(248, 248, 255);background: rgb(28, 28, 28);border: 2px solid rgb(248, 0, 0)")
                self.coor_line_in.setStyleSheet("color: rgb(248, 248, 255);background: rgb(28, 28, 28)")
            if self.key_err == 2:
                self.star_name_in.setStyleSheet("color: rgb(248, 248, 255);background: rgb(28, 28, 28)")
                self.coor_line_in.setStyleSheet("color: rgb(248, 248, 255);background: rgb(28, 28, 28);border: 2px solid rgb(248, 0, 0)")
        else:
            self.dark_btn.setText("Dark")
            self.setStyleSheet('background: rgb(248, 248, 255);')
            if self.key_err == 1:
                self.star_name_in.setStyleSheet("background: rgb(248, 248, 255);border: 2px solid rgb(248, 0, 0)")
                self.coor_line_in.setStyleSheet("background: rgb(248, 248, 255)")
            if self.key_err == 2:
                self.coor_line_in.setStyleSheet("background: rgb(248, 248, 255);border: 2px solid rgb(248, 0, 0)")
                self.star_name_in.setStyleSheet("background: rgb(248, 248, 255)")

    def create_file(self):
        if self.star_name_in.text() == "" or self.star_name_in.text() == "Обязательное поле":
            self.star_name_in.setText("Обязательное поле")
            if self.key_err == 2:
                self.coor_line_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.key_err =1
            self.star_name_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
        elif self.coor_line_in.text() == "" or self.coor_line_in.text() == "Обязательное поле":
            self.coor_line_in.setText("Обязательное поле")
            if self.key_err == 1:
                self.star_name_in.setStyleSheet('background: rgb(248, 248, 255);')
            self.key_err =2
            self.coor_line_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
        else:
            mp = ["M", "SR"]
            mip = ["EA"]

            stn = self.star_name_in.text()
            p = self.path_star + "\ "[0] +stn

            if self.oth_name_in.toPlainText() == "":
                o = OtherName(self.coor_line_in.text())
                a = o.getname()
                stroka_oth_name = ""
                for i in range(len(a)):
                    stroka_oth_name += a[i][0]+"   "+ a[i][1] + "\n"
                self.oth_name_in.setPlainText(stroka_oth_name)
            try:
                makedirs(p)
            except:
                pass

            if self.min_mag_in.text() == "" or self.max_mag_in.text() == "":
                ztf = ZTF_Points(self.coor_line_in.text(), p, True)
                z,mag = ztf.points()
                self.max_mag_in.setText(str(round(mag[0], 1)))
                self.max_mag_filter.setCurrentText(mag[2])
                self.min_mag_in.setText(str(round(mag[1], 1)))
                self.min_mag_filter.setCurrentText(mag[2])
            else:
                ztf = ZTF_Points(self.coor_line_in.text(), p, False)
                z = ztf.points()

            if self.per_line_in.text() == "" and (self.type_line_in.currentText() in mp or self.type_line_in.currentText() in mip):
                if self.type_line_in.currentText() in mp:
                    per ,ep = map(str, Lafler_clinman(p+"\ "[0]+z[0]))
                else:
                    per, ep = map(str, Lafler_clinman(p + "\ "[0] + z[0], max=False))
                self.per_line_in.setText(per)
                self.Epoch_line_in.setText(ep)
            if z != []:
                m = []
                for i in range(len(z)):
                    if self.type_line_in.currentText() in mp:
                        l = LightCurve(self.per_line_in.text(), p+"\ "[0]+z[i], "Максимуме", "Other" ,self.Epoch_line_in.text(), z[i][4], p)
                        l.make_LightCurve_with_per(False)
                        m.append([p+"\ "[0]+"Other"+z[i][4]+"P.txt", z[i][4]])
                    elif self.type_line_in.currentText() in mip:
                        l = LightCurve(self.per_line_in.text(), p+"\ "[0]+z[i], "Минимуме", "Other" ,self.Epoch_line_in.text(), z[i][4], p)
                        l.make_LightCurve_with_per(False)
                        m.append([p + "\ "[0] + "Other" + z[i][4] + "P.txt", z[i][4]])
                    else:
                        m.append([p+"\ "[0]+z[i],z[i][4]])
                if self.type_line_in.currentText() in mp or self.type_line_in.currentText() in mip:
                    gr =makeGrapf(m, p, self.star_name_in.text(), True)
                    gr.make()
                else:
                    gr = makeGrapf(m, p, self.star_name_in.text())
                    gr.make()


            p1 = p+"\ "[0] + stn + ".txt"
            with open(p1, "w") as f:
                f.writelines("Name: " + self.star_name_in.text() + "\n" +"\n")
                f.writelines("Coordinates: " + self.coor_line_in.text()+ "\n" + "\n")
                f.writelines("Other name: " +"\n"+self.oth_name_in.toPlainText() + '\n')
                f.writelines("Min. mag: " + self.min_mag_in.text() +" "+ self.min_mag_filter.currentText()+"\n")
                f.writelines("Max. mag: " + self.max_mag_in.text() +" "+ self.max_mag_filter.currentText()+"\n"+"\n")
                if self.type_line_in_n.text() != "":
                    f.writelines("Type: " + self.type_line_in_n.text()+"\n")
                else:
                    f.writelines("Type: " + self.type_line_in.currentText()+"\n")
                f.writelines("Period: "+ self.per_line_in.text() + "\n")
                f.writelines("Epoch: " + self.Epoch_line_in.text() + "\n")
                f.writelines("Eclipse: " + self.eclipse_line_in.text() + "%\n" + "\n")
                f.writelines("Remark:"+"\n"+"\n")
                if self.ZTF_f:
                    f.writelines("Masci, F. J.; et al., 2019, The Zwicky Transient Facility: Data Processing, Products, and Archive"+"\n")
                    f.writelines("2019PASP..131a8003M"+"\n"+"\n")
                if self.PANSTARRS_F:
                    f.writelines(
                        "Chambers, K. C.; et al., 2016, The Pan-STARRS1 Surveys." + "\n")
                    f.writelines("2016arxiv161205560C" + "\n" + "\n")
                f.writelines("Revision:"+ "\n"+self.comm_line_in.toPlainText())

    def clear_line(self):
        self.coor_line_in.clear()
        self.max_mag_in.clear()
        self.min_mag_in.clear()
        self.star_name_in.clear()
        self.eclipse_line_in.clear()
        self.oth_name_in.clear()
        self.type_line_in_n.clear()
        self.comm_line_in.setPlainText("GaiaEDR3 position.")
        self.per_line_in.clear()
        self.Epoch_line_in.clear()

    def ZTF(self):
        if self.ZTF_f:
            self.ZTF_f = False
        else:
            self.ZTF_f = True

    def PanStarrs(self):
        if self.PANSTARRS_F:
            self.PANSTARRS_F = False
        else:
            self.PANSTARRS_F = True

class win(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.path = os.getcwd()

    def w1(self):
        self.w1 = setting()
        try:
            with open("seting.txt") as f:
                pass
        except:
            a = self.path+"\seting.txt"
            a = a
            with open(a, "w") as f:
                pass
        with open("seting.txt", "r") as f:
            if f.read() == "":
                self.w1.butn.clicked.connect(self.w1.chek_value)
                self.w1.show()
                self.w1.butn.clicked.connect(self.success)
            else:
                self.w2()

    def w2(self):
        self.w2 = win2()
        self.w2.w1()
    def success(self):
        if self.w1.successfully:
            self.w1.start()
            self.w1.close()
            self.w2()

class Plate_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        with open("seting.txt") as f:
            self.path_save = f.read().split("\n")[1]
        self.prev_file = False
        self.key_error = 0
        self.dark_value = False
        self.show_errwin = ""


    def initUI(self):
        user = ctypes.windll.user32
        self.setGeometry(0, 0, user.GetSystemMetrics(0), user.GetSystemMetrics(1))
        self.setWindowTitle('Звёздный помошник')
        self.setStyleSheet('background: rgb(248, 248, 255);')

        self.beak_btn = QPushButton(self)
        self.beak_btn.setText("Beak")
        self.beak_btn.setGeometry(1700, 150, 100, 50)

        self.dark_btn = QPushButton(self)
        self.dark_btn.setText("Dark")
        self.dark_btn.setGeometry(1700, 100, 100, 50)
        self.dark_btn.clicked.connect(self.dark)

        self.name = QLabel(self)
        self.name.setText("Name")
        self.name.move(100, 50)

        self.name_in = QLineEdit(self)
        self.name_in.setText("Color")
        self.name_in.setGeometry(200, 50, 200, 25)

        self.R = QLabel(self)
        self.R.setText("Red plate")
        self.R.move(100, 100)

        self.R_line = QLineEdit(self)
        self.R_line.setGeometry(200, 100, 200, 25)

        self.R_btn = QPushButton(self)
        self.R_btn.setGeometry(400, 100, 50, 25)
        self.R_btn.setText("Select")
        self.R_btn.clicked.connect(self.get_r)

        self.G = QLabel(self)
        self.G.setText("Green plate")
        self.G.move(100, 150)

        self.G_line = QLineEdit(self)
        self.G_line.setGeometry(200, 150, 200, 25)

        self.G_btn = QPushButton(self)
        self.G_btn.setGeometry(400, 150, 50, 25)
        self.G_btn.setText("Select")
        self.G_btn.clicked.connect(self.get_g)

        self.B = QLabel(self)
        self.B.setText("Blue plate")
        self.B.move(100, 200)

        self.B_line = QLineEdit(self)
        self.B_line.setGeometry(200,200, 200, 25)

        self.B_btn = QPushButton(self)
        self.B_btn.setGeometry(400, 200, 50, 25)
        self.B_btn.clicked.connect(self.get_b)
        self.B_btn.setText("Select")

        self.color_combinations = QLabel(self)
        self.color_combinations.setText("Тип комбинации")
        self.color_combinations.move(100, 250)

        self.color_combinations_value = QComboBox(self)
        self.color_combinations_value.addItems(["BRIR", "BR B+R"])
        self.color_combinations_value.setGeometry(200, 250, 200, 25)

        self.color_size = QLabel(self)
        self.color_size.setText("FOV")
        self.color_size.move(100, 300)

        self.color_size_value = QComboBox(self)
        self.color_size_value.addItems(["10'x10'", "5'x5'"])
        self.color_size_value.setGeometry(200, 300, 200, 25)

        self.color_btn = QPushButton(self)
        self.color_btn.setGeometry(800, 500, 100, 50)
        self.color_btn.setText("Color")
        self.color_btn.clicked.connect(self.color)

        self.clear_btn = QPushButton(self)
        self.clear_btn.setGeometry(1700, 50, 100, 50)
        self.clear_btn.setText("Clear")
        self.clear_btn.clicked.connect(self.clear)

        self.butn4 = QPushButton("Preview", self)
        self.butn4.setGeometry(1700, 200, 100, 50)
        self.butn4.clicked.connect(self.preview)
    def dark(self):
        if self.dark_btn.text() == "Dark":
            self.dark_value = True
            self.setStyleSheet(setstell1)
            self.dark_btn.setText("White")
            if self.key_error == 1:
                self.R_line.setStyleSheet("background: rgb(28, 28, 28);border: 2px solid rgb(248, 0, 0)")
                self.G_line.setStyleSheet(setstell1)
                self.B_line.setStyleSheet(setstell1)
            elif self.key_error == 2:
                self.R_line.setStyleSheet(setstell1)
                self.G_line.setStyleSheet("background: rgb(28, 28, 28);border: 2px solid rgb(248, 0, 0)")
                self.B_line.setStyleSheet(setstell1)
            elif self.key_error == 3:
                self.R_line.setStyleSheet(setstell1)
                self.G_line.setStyleSheet(setstell1)
                self.B_line.setStyleSheet("background: rgb(28, 28, 28);border: 2px solid rgb(248, 0, 0)")
        else:
            self.dark_value = False
            self.dark_btn.setText("Dark")
            self.setStyleSheet('background: rgb(248, 248, 255);')
            if self.key_error == 1:
                self.R_line.setStyleSheet("background: rgb(248, 248, 255);border: 2px solid rgb(248, 0, 0)")
                self.G_line.setStyleSheet('background: rgb(248, 248, 255);')
                self.B_line.setStyleSheet('background: rgb(248, 248, 255);')
            elif self.key_error == 2:
                self.R_line.setStyleSheet("background: rgb(248, 248, 255);")
                self.G_line.setStyleSheet('background: rgb(248, 248, 255);border: 2px solid rgb(248, 0, 0)')
                self.B_line.setStyleSheet('background: rgb(248, 248, 255);')
            elif self.key_error == 2:
                self.R_line.setStyleSheet("background: rgb(248, 248, 255);")
                self.G_line.setStyleSheet('background: rgb(248, 248, 255);')
                self.B_line.setStyleSheet('background: rgb(248, 248, 255);border: 2px solid rgb(248, 0, 0)')

    def get_r(self):
        self.R_line.setText(QFileDialog().getOpenFileName(self, "Open project", "", "Image Files (*.fits)")[0])

    def get_b(self):
        self.B_line.setText(QFileDialog().getOpenFileName(self, "Open project", "", "Image Files (*.fits)")[0])

    def get_g(self):
        self.G_line.setText(QFileDialog().getOpenFileName(self, "Open project", "", "Image Files (*.fits)")[0])

    def preview(self):
        self.prev_file =True
        self.color()
        self.pr = previewwin(self.prev_file)
        self.pr.show()
        self.prev_file = False

    def color(self):
        if self.R_line.text() == "" or self.R_line.text() == "Выберете файл":
            self.R_line.setText("Выберете файл")
            self.R_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.key_error = 1
        elif self.G_line.text() == "" or self.G_line.text() == "Выберете файл":
            self.G_line.setText("Выберете файл")
            self.G_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            if self.dark_value:
                self.R_line.setStyleSheet(setstell1)
            else:
                self.R_line.setStyleSheet('background: rgb(248, 248, 255);')
            self.key_error = 2
        elif self.B_line.text() == "" or self.B_line.text() == "Выберете файл":
            if self.dark_value:
                self.R_line.setStyleSheet(setstell1)
                self.G_line.setStyleSheet(setstell1)
            else:
                self.R_line.setStyleSheet('background: rgb(248, 248, 255);')
                self.G_line.setStyleSheet('background: rgb(248, 248, 255);')
            self.B_line.setText("Выберете файл")
            self.B_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.key_error = 3

        else:
            if self.dark_value:
                self.R_line.setStyleSheet(setstell1)
                self.G_line.setStyleSheet(setstell1)
                self.B_line.setStyleSheet(setstell1)
            else:
                self.R_line.setStyleSheet('background: rgb(248, 248, 255);')
                self.B_line.setStyleSheet('background: rgb(248, 248, 255);')
                self.G_line.setStyleSheet('background: rgb(248, 248, 255);')
            save_as = self.name_in.text()
            data = []
            data.append(self.R_line.text())
            data.append(self.G_line.text())
            data.append(self.B_line.text())
            color = Image.new("RGB", (1240, 1240), 'white')

            for i in range(len(data)):
                image_data = fits.getdata(data[i])
                pyp.figure(figsize=(20, 20))
                pyp.imshow(image_data, cmap='gray')
                pyp.colorbar()
                name = data[i] + '.png'
                pyp.savefig(name)
                pyp.close()
                image = Image.open(name)
                image = image.crop((250, 390, 1490, 1630))
                pixels = image.load()
                color_p = color.load()
                for y in range(image.size[0]):
                    for x in range(image.size[1]):
                        zn = color_p[y, x]
                        if i == 0:
                            zn = (pixels[y, x][i], 1, 1)
                        elif i == 1:
                            zn = (zn[0], pixels[y, x][i], 1)
                        else:
                            zn = (zn[0], zn[1], pixels[y, x][i])
                        color_p[y, x] = zn
            colorsize = self.color_size_value.currentText()
            if colorsize == "10'x10'":
                color = color.crop((200, 200, 1040, 1040))
            else:
                color = color.crop((400, 400, 840, 840))
            color = color.resize((800, 800))
            color = ImageOps.flip(color)
            dr = ImageDraw.Draw(color)
            dr.line(((370, 400), (390, 400)), fill=(255, 255, 255))
            dr.line(((410, 400), (430, 400)), fill=(255, 255, 255))
            font = ImageFont.truetype("arial.ttf", 40)
            dr.text((400, 50), save_as, fill="#FFFFFF", font=font, anchor="ms")
            font = ImageFont.truetype("arial.ttf", 30)
            dr.text((100, 775), "Chart: " + self.color_combinations_value.currentText(), fill="#FFFFFF", font=font, anchor="ms")
            dr.text((700, 775), "FOV: " + self.color_size_value.currentText(), fill="#FFFFFF", font=font, anchor="ms")
            color.save(self.path_save+"/"+save_as.strip()+" " +self.color_size_value.currentText()+ ".png")
            if self.prev_file:
                self.prev_file = self.path_save+"/"+save_as.strip()+" " +self.color_size_value.currentText()+ ".png"

    def clear(self):
        self.R_line.clear()
        self.G_line.clear()
        self.B_line.clear()
        self.name_in.setText("Color")

class win2(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.wi2 = ""
        self.wi3 = ""
        self.wi4 = ""

    def w1(self):
        self.wi1 = vari()
        self.wi1.show()
        self.wi1.btn_OBR.clicked.connect(self.w2)
        self.wi1.btn_Reg.clicked.connect(self.w3)
        self.wi1.plate_OBR.clicked.connect(self.w4)
    def w2(self):
        self.wi1.close()
        self.wi2 = OBRwin()
        self.wi2.show()
        self.wi2.beak_btn.clicked.connect(self.beak)
    def w3(self):
        self.wi1.close()
        self.wi3 = registrWin()
        self.wi3.show()
        self.wi3.beak_btn.clicked.connect(self.beak)
    def w4(self):
        self.wi1.close()
        self.wi4 = Plate_Window()
        self.wi4.show()
        self.wi4.beak_btn.clicked.connect(self.beak)

    def beak(self):
        if self.wi2 != '':
            self.wi2.close()
            self.wi2 = ''
            self.w1()
        if self.wi3 != '':
            self.wi3.close()
            self.wi3 = ""
            self.w1()
        if self.wi4 != "":
            self.wi4.close()
            self.wi4 = ""
            self.w1()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    st = win()
    st.w1()
    sys.exit(app.exec())