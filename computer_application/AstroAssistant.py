import sys, ctypes,math
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QMainWindow, QGridLayout, QSizePolicy, \
    QVBoxLayout, QScrollArea
from PyQt5.QtWidgets import QLabel, QLineEdit, QCheckBox, QPlainTextEdit, QFileDialog
from PyQt5.QtGui import QPixmap, QFont
import seaborn as sns
import matplotlib.pyplot as pyp
from PyQt5.uic import loadUi
from pandas import DataFrame
import os
from os import makedirs
import requests
import re
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat
from astropy.io import fits

darkstele= '''
QWidget {
    background-color:rgb(28, 28, 28);
}

QPushButton {
	border: 2px solid rgb(248, 248, 255);
	background-color: rgb(11, 20, 197);
	color: rgb(248, 248, 255);
}

QLabel {
	color: rgb(248, 248, 255)
}

QLineEdit {
	color: rgb(248, 248, 255);
	background: rgb(28, 28, 28);
}

QLineEdit:hover {
	background-color: rgb(64, 72, 221);
}

QGroupBox{
	color: rgb(248, 248, 255);
	background: rgb(28, 28, 28);
}

QComboBox {
	color: rgb(248, 248, 255);
	border: 2px solid rgb(248, 248, 255);
	background: rgb(28, 28, 28);
}

QComboBox:hover {
	background-color: rgb(11, 20, 197);
}

QComboBox QAbstractItemView {
	color: rgb(248, 248, 255);
	border: 2px solid rgb(248, 248, 255);
	background: rgb(28, 28, 28);
	selection-background-color: rgb(11, 20, 197);
	selection-color: rgb(170, 85, 255)
}

QComboBox::drop-down:hover {
    background-color: rgb(131, 0, 81);
}

QPushButton:hover{
	background-color: rgb(170, 85, 255);
	color: rgb(0, 0,0);
}

QPushButton:pressed {
	background-color: rgb(131, 0, 81);
	color: rgb(248, 248, 255);
}

QSlider::groove:horizontal {
	border: 0px;
}
 
QSlider::sub-page:horizontal {
	background-color: rgb(170, 85, 255);
	margin-top:8px;
	margin-bottom:8px;
	border-radius: 2px;
}
 
QSlider::add-page:horizontal {
	background:  rgb(131, 0, 81);
	border: 0px solid #777;
	border-radius: 2px;
	margin-top:8px;
	margin-bottom:8px;
}
 
QSlider::handle:horizontal {
	background: rgb(28, 28, 28);
	border: 2px solid rgb(248, 248, 255);
	width: 12px;
	border-radius: 4px;
	margin-top:2px;
	margin-bottom:2px;
}
 
QSlider::handle:horizontal:hover {
	background-color: rgb(11, 20, 197)
}

QPlainTextEdit{
	background-color: rgb(28, 28, 28);
	border: 2px solid rgb(248, 248, 255);
	color: rgb(248, 248, 255);
}

QPlainTextEdit:hover{
	background-color: rgb(64, 72, 221);
}
'''

standartstele='''
QWidget {
	background-color: rgb(243, 245, 255);
}

QPushButton {
	border: 2px solid rgb(0, 0, 0);
	background-color: rgb(124, 159, 255);
	color: rgb(0, 0, 0);
}

QLabel {
	color: rgb(0, 0, 0)
}

QLineEdit {
	background-color: rgb(243, 245, 255);
	border: 2px solid rgb(0, 0, 0);
}

QLineEdit:hover {
	background-color: rgb(217, 222, 255);
}

QGroupBox{
	color: rgb(0, 0, 0);
	background-color: rgb(243, 245, 255);
}

QComboBox {
	border: 2px solid rgb(0, 0, 0);
	background-color: rgb(243, 245, 255);
}

QComboBox:hover {
	background-color: rgb(124, 159, 255);
}

QComboBox QAbstractItemView {
	border: 2px solid rgb(0, 0, 0);
	background-color: rgb(243, 245, 255);
	selection-background-color: rgb(217, 222, 255);
	selection-color: rgb(0, 0, 0)
}

QComboBox::drop-down:hover {
    background-color: rgb(190, 137, 255);
}

QPushButton:hover{
	background-color: rgb(190, 137, 255);
	color: rgb(0, 0,0);
}

QPushButton:pressed {
	background-color:rgb(189, 23, 87);
}

QSlider::groove:horizontal {
	border: 0px;
}
 
QSlider::sub-page:horizontal {
	background-color: rgb(11, 20, 197);
	margin-top:8px;
	margin-bottom:8px;
	border-radius: 2px;
}
 
QSlider::add-page:horizontal {
	background:  rgb(131, 0, 81);
	border: 0px solid #777;
	border-radius: 2px;
	margin-top:8px;
	margin-bottom:8px;
}
 
QSlider::handle:horizontal {
	background: rgb(124, 159, 255);
	border: 2px solid rgb(0, 0, 0);
	width: 12px;
	border-radius: 4px;
	margin-top:2px;
	margin-bottom:2px;
}
 
QSlider::handle:horizontal:hover {
	background-color: rgb(190, 137, 255)
}

QPlainTextEdit{
	background-color: rgb(243, 245, 255);
	border: 2px solid rgb(0, 0, 0);
}

QPlainTextEdit:hover{
	background-color: rgb(217, 222, 255);
}
'''

def refiend_path(path):
    try:
        a = sys._MEIPASS
    except Exception:
        a = os.path.abspath("..")
    return os.path.join(a, path)

def eclipse_percent(path):
    data = []
    s = {}
    with open(path) as f:
        for i in f:
            a = list(map(float, i.split()))
            data.append(a)
            if round(a[1], 2) in s:
                s[round(a[1], 2)] +=1
            else:
                s[round(a[1], 2)] = 1
    ma = [0, 0]
    for i in s:
        if s[i]>ma[0]:
            ma[0] = s[i]
            ma[1] = i
    data = sorted(filter(lambda x :-0.5<=x[0]<=0.5,data), key=lambda x:x[0])
    znach = []
    pred = 0
    value_mi = False
    for i in range(len(data)):
        if data[i][1] - ma[1] > 0.15:
            if not(value_mi):
                pred = data[i][0]
                value_mi = True
        else:
            if value_mi:
                value_mi = False
                znach.append(data[i][0] - pred)
    eclipse = max(znach)*100
    if eclipse%1>0.2:
        return math.ceil(eclipse)
    else:
        return math.floor(eclipse)

def is_coord(value):
    match = re.fullmatch(r"\d{1,2}\s\d{1,2}\s\d{1,2}\.\d{1,3}\s[+-]\d{1,2}\s\d{1,2}\s\d{1,2}\.\d{1,3}", value)
    return True if match else False

def fiend_err(wids, style, min_err_key):
    k = min_err_key
    for i in range(len(wids)):
        if wids[i].text() != "":
            if not(is_float(wids[i].text())):
                wids[i].setStyleSheet(style)
                return k
        k+=1
    return 0

def normal_wid(wids, style):
    for i in range(len(wids)):
        wids[i].setStyleSheet(style)

def LK1(a):
    s = 0
    for i in range(len(a)):
        s += (a[i][1] - a[i - 1][1]) ** 2
    return s

def drob(n):
    return n - math.floor(n)

def Lafler_clinman(name, maxi = True):
    with open(name) as f:
        if maxi:
            ma = 32
        else:
            ma = -32
        ep0 = 0
        m = []
        for i in f:
            m.append(list(map(float, i.split())))
            if m[-1][1] < ma and maxi:
                ma = m[-1][1]
                ep0 = m[-1][0]
            elif m[-1][1] > ma and not(maxi):
                ma = m[-1][1]
                ep0 = m[-1][0]
        with open("setting.txt") as f:
            file = f.read().split("\n")
            pmin = float(file[2].split()[1])
            pmax = float(file[3].split()[1])
            step = float(file[4].split()[1])
        wmin = 1 / pmax
        wmax = 1 / pmin
        p = []

        while wmin <= wmax:
            b = []
            for i in range(len(m)):
                b.append([drob((m[i][0] - ep0) * wmin), m[i][1]])
            b = sorted(b, key=lambda x: x[0])
            p.append([LK1(b), 1 / wmin])
            wmin += step

        p = sorted(p, key=lambda x: x[0])
        per_n = p[0][1]
    return round(per_n, 7), round(ep0, 3)

class OtherName:
    def __init__(self, cor):
        self.silka = "https://vizier.u-strasbg.fr/viz-bin/VizieR-4?-mime=html&-source=USNO-A2.0,GSC2.2,IPHAS,USNO-B1.0,GSC2.3,URAT1,2MASS,SDSS,WISE,II/335/galex_ais&-c="+cor+"&-c.rs=4"
        self.other = []
    def getname(self):
        req = requests.get(self.silka)
        a = req.text
        a = a.split()
        s = {}
        for i in range(len(a)):
            if "urat1&amp" in a[i]:
                if 'NOWRAP' in a[i+3]:
                    if "URAT1" not in s:
                        self.other.append(["URAT1", a[i+3][7:17]])
                        s["URAT1"] = ""
            if a[i].count("galex_ais")==1 and a[i+7] == "NOWRAP>GALEX" and "J" in a[i+8]:
                if "GALEX" not in s:
                    self.other.append(["GALEX", a[i+8][:-5]])
                    s["GALEX"] = ""
            if "===" in a[i] and "AllWISE" not in a[i]:
                b = a[i].split(";")
                b = re.split("===|&|'", b[3])
                if "%2b" in b[1]:
                    b[1] = r"{}+{}".format(*b[1].split("%2b"))
                if b[0] == "2MASS":
                    b[1] = "J"+b[1]
                if b[0] not in s:
                    self.other.append([b[0], b[1]])
                    s[b[0]] = ""
        return self.other

class ZTF_Points:
    def __init__(self, coord, fiel_name, mag = True):#на вход координаты и путь куда будут сохраняться файлы / mag - если true то ищет магнитуду дополнительео выводит масив макс зн \мин зн\ фильтр
        self.fiel_name = fiel_name #куда сохраняю файл
        self.ssilka1 = "https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?spatial=box&catalog=ztf_objects_dr15&objstr={}h+{}m+{}s+{}d+{}m+{}s&size=10&outfmt=1".format(*coord.split())
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
        print(name_r, name_g)
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
            name_g = max(name_g, key=lambda x:x[1])[0]#выбираю тот набор в котором больше всего наблюдений
            data = requests.get(self.ssilka2.format(name_g)).text.split()#получаю данные наблюдений
            if "<TR>" in data:
                kol = 0
                with open(self.fiel_name+"\ztf_g.txt", "w") as f:
                    for i in range(len(data)):
                        if data[i] == "<TR>":
                            kol+=1
                            f.writelines(re.split("<|>", data[i + 4])[2][:12] + " " + re.split("<|>", data[i + 5])[2][:6] + "\n")#записываю наблюдения в формате дата/наблюдение
                            if self.mag:
                                if float(re.split("<|>", data[i + 5])[2][:6]) < g_mag[0] and len(data[i + 7])<11:#код ошибки наблюдений на i+7
                                    g_mag[0]=float(re.split("<|>", data[i + 5])[2][:6])
                                if float(re.split("<|>", data[i + 5])[2][:6]) > g_mag[1] and len(data[i + 7])<11:
                                    g_mag[1] = float(re.split("<|>", data[i + 5])[2][:6])
                    ret.append(['ztf_g.txt', kol])  # записываю что сделал файл с наблюдениями в фильтре g
                if self.mag:
                    magn.append(g_mag)

        if name_r != []:
            if self.mag:
                r_mag = [100, -100, "r"]
            name_r = max(name_r, key=lambda x: x[1])[0]#выбираю тот набор в котором больше всего наблюдений
            data = requests.get(self.ssilka2.format(name_r)).text.split()#получаю данные наблюдений
            if "<TR>" in data:
                kol = 0
                with open(self.fiel_name + "\ztf_r.txt", "w") as f:
                    for i in range(len(data)):
                        if data[i] == "<TR>":
                            kol+=1
                            f.writelines(re.split("<|>", data[i + 4])[2][:12] + " " + re.split("<|>", data[i + 5])[2][:6] + "\n")#записываю наблюдения в формате дата/наблюдение
                            if self.mag:
                                if float(re.split("<|>", data[i + 5])[2][:6]) < r_mag[0] and len(data[i + 7])<11:
                                    r_mag[0]=float(re.split("<|>", data[i + 5])[2][:6])
                                if float(re.split("<|>", data[i + 5])[2][:6]) > r_mag[1] and len(data[i + 7])<11:
                                    r_mag[1] = float(re.split("<|>", data[i + 5])[2][:6])
                    ret.append(['ztf_r.txt', kol])  # записываю что сделал файл с наблюдениями в фильтре r
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
        x = []
        y = []
        value = []
        for i in range(len(self.path)):
            fil = self.path[i][2]+" "+self.path[i][1]
            with open(self.path[i][0]) as f:
                for i in f:
                    x.append(float(i.split()[0]))
                    y.append(float(i.split()[1]))
                    value.append(fil)
                mi, ma = min(y), max(y)
                if mi < ymin:
                    ymin = mi
                if ma > ymax:
                    ymax = ma
        data = DataFrame({"x":x, "y":y, "data":value})
        color = {"ZTF r":"#f80000", "ZTF g":"#000080", "Atlas c" : "#40734f",  "Atlas o":"#f5770a", "ZTF i":"#ff4d00", "Other r": "#f80000", "Other g":"#000080",
                 "Other c" : "#40734f",  "Other o":"#f5770a", "Other i":"#ff4d00"}
        g = sns.scatterplot(data =data, x="x", y="y", hue= "data", palette=color)
        g.figure.set_figwidth(12)
        g.figure.set_figheight(8)
        pyp.ylim(ymax+0.5, ymin-0.5)
        if self.phase:
            pyp.xlim(-0.5, 1)
            pyp.title(self.name, fontsize=23)
            pyp.ylabel("Magnitude", fontsize=18)
            pyp.xlabel("Phase", fontsize=18)
            pyp.savefig(self.savef + "\ "[0] + self.name + "Phase.png")
        else:
            pyp.title(self.name, fontsize=23)
            pyp.ylabel("Magnitude", fontsize=18)
            pyp.xlabel("MJD", fontsize=18)
            pyp.savefig(self.savef + "\ "[0] + self.name + "LC.png")
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
                g = makeGrapf([[b, self.filter, self.by]], self.new_fiel, "preview")
                g.make()

        if self.by == "Atlas":
            o = self.new_fiel+'\ '[0]+self.by+'o.txt'
            o1 = o
            c = self.new_fiel+'\ '[0] +self.by+'c.txt'
            c1 = c
            with open(o1,'w') as f1:
                with open(c1,'w') as f2:
                    for i in range(1, len(a)):
                        if a[i] != '':
                            r = a[i].split()
                            if '-' not in r[1] and len(r[3]) <6 and float(r[2])<1.5:
                                if r[5] == 'c':
                                    f2.writelines(r[0] +' '+ r[1]+'\n')
                                if r[5] == "o":
                                    f1.writelines(r[0] +' '+ r[1]+'\n')
            if self.make:
                g1 = makeGrapf([[o1, "o", "Atlas"],[c1, "c", "Atlas"]], self.new_fiel, "preview")
                g1.make()

        if self.by == "Other":
            c = self.new_fiel + "\ "[0] + self.by + self.filter + ".txt"
            b = c
            with open(b, "w") as f:
                for i in range(17, len(a)):
                    if a[i] != '':
                        f.writelines(a[i].split()[0] + " " + a[i].split()[1] + "\n")
            if self.make:
                g = makeGrapf([[b, self.filter, self.by]], self.new_fiel, "preview")
                g.make()

    def make_LightCurve_with_per(self, fep = True):
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

            if self.by == "Atlas":
                for i in range(17, len(a)):
                    r = a[i].split()
                    if a[i] != '' and "-" not in r[1] and float(r[2]) < 1.5 and len(r[3]) < 6:
                        a[i] = [r[0], r[1], r[5]]
                        if float(a[i][1]) > min_[1]:
                            min_ = [float(a[i][0]), float(a[i][1])]
                if fep:
                    correct_epoch = self.make_epoch(min_[0])
                else:
                    correct_epoch = float(self.epoch)
                ft1= self.new_fiel + "\ "[0] + self.by + "oP.txt"
                ft2 = self.new_fiel + "\ "[0] + self.by + "cP.txt"
                f1 = ft1
                f2 = ft2
                with open(f1, "w") as of1:
                    with open(f2, "w") as of2:
                        for i in range(1, len(a)):
                            if len(a[i]) == 3:
                                rez = (float(a[i][0]) - correct_epoch) / float(self.period)
                                rez_c = round(rez) - 1
                                if a[i][2] == "c":
                                    of2.writelines(str(rez - rez_c)[:8] + " " + a[i][1] + '\n')
                                    of2.writelines(str(rez - rez_c-1)[:8] + " " + a[i][1] + '\n')
                                else:
                                    of1.writelines(str(rez - rez_c)[:8] + " " + a[i][1] + '\n')
                                    of1.writelines(str(rez - rez_c - 1)[:8] + " " + a[i][1] + '\n')

                if self.make:
                    g = makeGrapf([[f1, "o", "Atlas"], [f2, "c", "Atlas"]], self.new_fiel, "preview", phase= True)
                    g.make()
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

            if self.by == "Atlas":
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
                with open(f1, "w") as of1:
                    with open(f2, "w") as of2:
                        for i in range(1, len(a)):
                            if len(a[i]) == 3:
                                rez = (float(a[i][0]) - correct_epoch) / float(self.period)
                                rez_c = round(rez) - 1
                                if a[i][2] == "c":
                                    of2.writelines(str(rez - rez_c)[:8] + " " + a[i][1] + '\n')
                                    of2.writelines(str(rez - rez_c-1)[:8] + " " + a[i][1] + '\n')
                                else:
                                    of1.writelines(str(rez - rez_c)[:8] + " " + a[i][1] + '\n')
                                    of1.writelines(str(rez - rez_c - 1)[:8] + " " + a[i][1] + '\n')

                if self.make:
                    g = makeGrapf([[f1, "o", "Atlas"], [f2, "c", "Atlas"]], self.new_fiel, "preview", phase= True)
                    g.make()

        if self.by != "Atlas":
            with open(b, "w") as f:
                for i in range(len(a)):
                    if a[i] != "":
                        rez = (float(a[i][0]) - correct_epoch) / float(self.period)
                        rez_c = math.floor(rez)
                        f.writelines(str(rez - rez_c)[:8] + " " + a[i][1] + '\n')
                        f.writelines(str(rez - rez_c - 1)[:8] + " " + a[i][1] + '\n')

            if self.make:
                g = makeGrapf([[b, self.filter, self.by]], self.new_fiel, "preview", phase=True)
                g.make()
        return correct_epoch

def is_float(value):
    match1 = re.fullmatch(r"\d{1,}\.\d{0,}", value)
    match2 = re.fullmatch(r"\d{1,}", value)
    return (True if match1 else False) or (True if match2 else False)

class vari(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        user = ctypes.windll.user32
        self.setGeometry(user.GetSystemMetrics(0)//2-250, user.GetSystemMetrics(1)//2-200, 725, 400)
        self.setStyleSheet(standartstele)
        self.ui = loadUi(refiend_path("UIvari.ui"), self)
        self.setWindowTitle("Выбор")

class about_program(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet(standartstele)
        self.setFixedSize(700, 600)
        user = ctypes.windll.user32
        self.move(user.GetSystemMetrics(0) // 2 - 350, user.GetSystemMetrics(1) // 2 - 300)
        self.setWindowTitle("О программе")
        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QVBoxLayout()

        with open(refiend_path("about.txt"), encoding="utf-8") as f:
            for text in f:
                object = QLabel(text.strip())
                if "?" in text:
                    object.setStyleSheet("color: #005de0")
                if "https" in text:
                    object = QLabel(self)
                    object.setText('<a href="https://www.aavso.org/vsx/index.php?view=about.vartypes">Типы переменных звезд</a>')
                    object.setOpenExternalLinks(True)
                font = QFont()
                font.setPixelSize(18)
                object.setFont(font)
                object.setWordWrap(True)
                self.vbox.addWidget(object)

        self.widget.setLayout(self.vbox)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.setCentralWidget(self.scroll)
        self.show()


class setting(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.successfully =False
        self.err_win = ""
        self.information = ""

    def initUI(self):
        self.setFixedSize(700, 600)
        user = ctypes.windll.user32
        self.move(user.GetSystemMetrics(0) // 2 - 350, user.GetSystemMetrics(1) // 2 - 300)
        self.ui = loadUi(refiend_path("UIsettings.ui"), self)
        self.ui.setStyleSheet(standartstele)
        self.setWindowTitle('Настройки')

        self.ui.Fiel_line_choice.clicked.connect(self.file_choice)

        self.ui.star_line_choice.clicked.connect(self.star_choice)

        self.ui.inf_btn.clicked.connect(self.inform_show)

    def inform_show(self):
        self.information = about_program()

    def chek_value(self):
        if not(os.path.isdir(self.ui.Fiel_line_in.text())):
            self.ui.Fiel_line_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.ui.star_line_in.setStyleSheet(standartstele)
            self.ui.min_period_in.setStyleSheet(standartstele)
            self.ui.max_period_in.setStyleSheet(standartstele)
            self.err_win = errWind("Папка не найдена!")
            self.err_win.show()
        elif not(os.path.isdir(self.ui.star_line_in.text())):
            self.ui.Fiel_line_in.setStyleSheet(standartstele)
            self.ui.star_line_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.ui.min_period_in.setStyleSheet(standartstele)
            self.ui.max_period_in.setStyleSheet(standartstele)
            self.err_win = errWind("Папка не найдена!")
            self.err_win.show()
        elif not(is_float(self.ui.max_period_in.text())):
            self.ui.Fiel_line_in.setStyleSheet(standartstele)
            self.ui.star_line_in.setStyleSheet(standartstele)
            self.ui.min_period_in.setStyleSheet(standartstele)
            self.ui.max_period_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.err_win = errWind("Укажите число!")
            self.err_win.show()
        elif not(is_float(self.ui.min_period_in.text())):
            self.ui.Fiel_line_in.setStyleSheet(standartstele)
            self.ui.star_line_in.setStyleSheet(standartstele)
            self.ui.min_period_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.ui.max_period_in.setStyleSheet(standartstele)
            self.err_win = errWind("Укажите число!")
            self.err_win.show()
        elif float(self.ui.min_period_in.text()) > float(self.ui.max_period_in.text()):
            self.ui.Fiel_line_in.setStyleSheet(standartstele)
            self.ui.star_line_in.setStyleSheet(standartstele)
            self.ui.min_period_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.ui.max_period_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.err_win = errWind("Минимальный период должен быть меньше максимального!")
            self.err_win.show()
        elif float(self.ui.min_period_in.text()) == 0:
            self.ui.Fiel_line_in.setStyleSheet(standartstele)
            self.ui.star_line_in.setStyleSheet(standartstele)
            self.ui.min_period_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.ui.max_period_in.setStyleSheet(standartstele)
            self.err_win = errWind("Минимальный период не может равняться 0!")
            self.err_win.show()
        else:
            if self.err_win != "":
                self.err_win.close()
                self.err_win = ""
            self.successfully = True

    def closeEvent(self, event):
        if self.err_win != "":
            self.err_win.close()
            self.err_win = ""
        if self.information != "":
            self.information.close()

    def start(self):
        with open("setting.txt", "w") as f:
            f.writelines(self.ui.star_line_in.text()+"\n")
            f.writelines(self.ui.Fiel_line_in.text()+"\n")
            f.writelines("Min_period " + self.ui.min_period_in.text() + "\n")
            f.writelines("Max_period " + self.ui.max_period_in.text() + "\n")
            f.writelines("Step_period " + self.ui.step_period_in.text())

    def file_choice(self):
        self.ui.Fiel_line_in.setText(QFileDialog().getExistingDirectory(self))

    def star_choice(self):
        self.ui.star_line_in.setText(QFileDialog().getExistingDirectory(self))

    def fill_inf(self):
        with open("setting.txt") as f:
            file = f.read().split("\n")
            self.ui.star_line_in.setText(file[0])
            self.ui.Fiel_line_in.setText(file[1])
            self.ui.min_period_in.setText(file[2].split()[1])
            self.ui.max_period_in.setText(file[3].split()[1])
            self.ui.step_period_in.setText(file[4].split()[1])

class errWind(QWidget):
    def __init__(self, text_err):
        super().__init__()
        self.text_err = text_err
        self.initUI()

    def initUI(self):
        self.setFixedSize(400, 200)
        user = ctypes.windll.user32
        self.move(user.GetSystemMetrics(0) // 2 - 200, user.GetSystemMetrics(1) // 2 - 100)
        self.setStyleSheet(standartstele)
        self.ui = loadUi(refiend_path("UIerr.ui"), self)
        self.setWindowTitle("ERR")

        self.ui.err_show.setText(self.text_err)
        self.ui.err_show.setAlignment(Qt.AlignCenter)

        self.ui.btn.clicked.connect(self.ok)

    def ok(self):
        self.close()

class previewwin(QWidget):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Preview')
        self.setStyleSheet(standartstele)

        self.lab = QLabel(self)
        self.lab.move(10, 10)
        self.pi = QPixmap(self.path)
        self.setFixedSize(self.pi.width()+20, self.pi.height()+20)
        self.lab.setPixmap(self.pi)


class OBRwin(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        user = ctypes.windll.user32
        self.x = user.GetSystemMetrics(0)
        self.y = user.GetSystemMetrics(1)
        with open("setting.txt") as f:
            self.name_per_fiel = f.read().split("\n")[1]
        self.err_key = 0
        self.make = False
        self.settig = ""
        self.show_errwin = ""
        self.dark_value = False
        self.information = ""

    def initUI(self):
        user = ctypes.windll.user32
        self.setGeometry(0, 0, user.GetSystemMetrics(0), user.GetSystemMetrics(1))
        loadUi(refiend_path("UIobrwin.ui"), self)
        self.setStyleSheet(standartstele)
        self.setWindowTitle('Star Assistant')

        self.line_btn.clicked.connect(self.get_txt)

        self.butn1.clicked.connect(self.count)

        self.butn2.clicked.connect(self.claer)

        self.butn3.clicked.connect(self.dark)

        self.butn4.clicked.connect(self.preview)

        self.make_grath_true.clicked.connect(self.make_g)

        self.settings_btn.clicked.connect(self.show_settings)

        self.inf_btn.clicked.connect(self.inform_show)

    def inform_show(self):
        self.information = about_program()

    def closeEvent(self, event):
        if self.settig != "":
            self.settig.close()
            self.settig = ""
        if self.show_errwin != "":
            self.show_errwin.close()
        if self.information != "":
            self.information.close()

    def resizeEvent(self, event):
        self.settings_btn.move(self.width() - 200, self.settings_btn.y())
        self.butn3.move(self.width()- 200, self.butn3.y())
        self.butn4.move(self.width() - 200, self.butn4.y())
        self.beak_btn.move(self.width()- 200, self.beak_btn.y())
        self.butn2.move(self.width() - 200, self.butn2.y())
        self.butn1.move(self.width()//2 - 50, self.butn1.y())
        self.inf_btn.move(self.width() - 200, self.inf_btn.y())

    def show_settings(self):
        self.settig = setting()
        self.settig.fill_inf()
        self.settig.show()
        self.settig.ui.butn.clicked.connect(self.settig.chek_value)
        self.settig.ui.butn.clicked.connect(self.success)

    def success(self):
        if self.settig.successfully:
            self.settig.start()
            with open("setting.txt") as f:
                self.name_per_fiel = f.read().split("\n")[1]
            self.settig.close()

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
        if self.dark_value:
            self.line_F_in.setStyleSheet(darkstele)
            self.line_Per_in.setStyleSheet(darkstele)
            self.line_Epoch_in.setStyleSheet(darkstele)
        else:
            self.line_F_in.setStyleSheet(standartstele)
            self.line_Per_in.setStyleSheet(standartstele)
            self.line_Epoch_in.setStyleSheet(standartstele)

        if self.line_F_in.text() == "" or self.line_F_in.text() == "Обязательное поле":
            self.line_F_in.setText("Обязательное поле")
            self.line_F_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.err_key =1
            self.show_errwin = errWind("Не указан путь к файлу!")
            self.show_errwin.show()
        else:
            if self.line_Epoch_in.text() == "" and self.line_Per_in.text() != "" or self.line_Epoch_in.text() == "Обязательное поле" and self.line_Per_in.text() != "":
                self.line_Epoch_in.setText("Обязательное поле")
                self.line_Epoch_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
                self.err_key = 2
                self.show_errwin = errWind("Вы указали период! Укажите эпоху!")
                self.show_errwin.show()
            elif self.line_Epoch_in.text() != "" and self.line_Per_in.text() == "" or self.line_Epoch_in.text() != "" and self.line_Per_in.text() == "Обязательное поле":
                self.line_Per_in.setText("Обязательное поле")
                self.err_key = 3
                self.line_Per_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
                self.show_errwin = errWind("Вы указали эпоху! Укажите период!")
                self.show_errwin.show()
            elif not(is_float(self.line_Per_in.text())) and self.line_Per_in.text() != "":
                self.line_Per_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
                self.err_key = 4
                self.show_errwin = errWind("Период должен быть числом!")
                self.show_errwin.show()
            elif not(is_float(self.line_Epoch_in.text())) and self.line_Epoch_in.text() != "":
                self.line_Epoch_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
                self.err_key = 5
                self.show_errwin = errWind("Эпоха должна быть числом!")
                self.show_errwin.show()
            else:
                self.err_key = 0
                if self.line_Epoch_in.text() != "":
                    if float(self.line_Per_in.text()) == 0:
                        self.line_Per_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
                        self.err_key = 7
                        self.show_errwin = errWind("Период не может равняться 0!")
                        self.show_errwin.show()
                    elif float(self.line_Epoch_in.text()) == 0:
                        self.line_Epoch_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
                        self.err_key = 8
                        self.show_errwin = errWind("Эпоха не может равняться 0!")
                        self.show_errwin.show()
                    else:
                        self.err_key = 0

            if self.err_key == 0:
                if self.line_Epoch_in.text() != "" and self.line_Per_in.text() != "":
                    otvet = LightCurve(self.line_Per_in.text(), self.line_F_in.text(), self.type_box.currentText(),
                                           self.data_box.currentText(), self.line_Epoch_in.text(),
                                           self.filter_box.currentText(), self.name_per_fiel, self.make)
                    try:
                        rezult = otvet.make_LightCurve_with_per()
                        self.val_Ep_in.setText(str(rezult)[:10])
                        self.err_key = 0
                    except:
                        self.show_errwin = errWind("Не удалось обработать файл! Проверьте введенные данные!")
                        self.show_errwin.show()
                        self.err_key = 6
                else:
                    try:
                        otvet = LightCurve("",self.line_F_in.text(), "", self.data_box.currentText(), "",self.filter_box.currentText() ,self.name_per_fiel, make=self.make)
                        otvet.make_LightCurve_not_per()
                        self.err_key = 0
                    except:
                        self.show_errwin = errWind("Не удалось обработать файл! Проверьте введенные данные!")
                        self.show_errwin.show()
                        self.err_key = 6

    def dark(self):
        if self.butn3.text() == "Темная тема":
            self.dark_value = True
            self.butn3.setText("Светлая тема")
            self.setStyleSheet(darkstele)
            self.line_Per_in.setStyleSheet(darkstele)
            self.line_F_in.setStyleSheet(darkstele)
            self.line_Epoch_in.setStyleSheet(darkstele)
            if self.err_key == 1:
                self.line_F_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.err_key ==2 or self.err_key == 5 or self.err_key == 8:
                self.line_Epoch_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.err_key == 3 or self.err_key == 4 or self.err_key == 7:
                self.line_Per_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
        else:
            self.dark_value = False
            self.butn3.setText("Темная тема")
            self.setStyleSheet(standartstele)
            self.line_Per_in.setStyleSheet(standartstele)
            self.line_F_in.setStyleSheet(standartstele)
            self.line_Epoch_in.setStyleSheet(standartstele)
            if self.err_key == 1:
                self.line_F_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.err_key ==2 or self.err_key == 5 or self.err_key == 8:
                self.line_Epoch_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.err_key == 3 or self.err_key == 4 or self.err_key == 7:
                self.line_Per_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")

    def preview(self):
        a = self.make
        self.make = True
        self.count()
        self.make = a
        if self.err_key == 0:
            if self.line_Per_in.text() != "":
                a = self.name_per_fiel+"/"+"previewPhase.png"
            else:
                a = self.name_per_fiel + "/" + "previewLC.png"
            self.wp = previewwin(a)
            self.wp.show()

class registrWin(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ZTF_f = True
        self.PANSTARRS_F = False
        with open("setting.txt") as f:
            self.path_star = f.readline().split("\n")[0]
        self.key_err = 0
        self.settig = ""
        self.show_errwin = ""
        self.information = ""
        self.dark_value = False

    def initUI(self):
        user = ctypes.windll.user32
        self.setGeometry(0, 0, user.GetSystemMetrics(0), user.GetSystemMetrics(1))
        self.setWindowTitle('Star Assistant')
        self.setStyleSheet(standartstele)
        loadUi(refiend_path("UIregister.ui"), self)

        self.dark_btn.clicked.connect(self.dark)

        self.clear_btn.clicked.connect(self.clear_line)

        self.file_btn.clicked.connect(self.create_file)

        self.type_line_in.addItems(sorted(['ACEP', 'ACV', 'ACYG', 'AHB1', 'AM', 'BCEP', 'BCEPS', 'BE', 'BLAP', 'BXCIR', 'BY',
                                           'CBSS', 'CBSS/V', 'CEP', 'CTTS', 'CTTS/ROT', 'CW', 'CWA', 'CWB', 'CWB(B)', 'CWBS', 'DCEP',
                                           'DCEP(B)', 'DCEPS', 'DCEPS(B)', 'DPV', 'DQ', 'DQ/AE', 'DSCT', 'DSCTC', 'DWLYN', 'DYPer',
                                           'E', 'EA', 'EB', 'ELL', 'EP', 'EW', 'EXOR', 'FF', 'FKCOM', 'FSCMa', 'FUOR', 'GCAS', 'GDOR',
                                           'HADS', 'HADS(B)', 'HB', 'HMXB', 'I', 'IA', 'IB', 'IBWD', 'IMXB', 'IN', 'INA', 'INAT', 'INB',
                                           'INS', 'INSA', 'INSB', 'INST', 'INT', 'IS', 'ISA', 'ISB', 'L', 'LB', 'LC', 'LERI', 'LMXB', 'M',
                                           'N', 'NA', 'NB', 'NC', 'NL', 'NL/VY', 'NR', 'PPN', 'PSR', 'PVTEL', 'PVTELI', 'PVTELII', 'PVTELIII',
                                           'R', 'RCB', 'ROT', 'RR', 'RRAB', 'RRC', 'RRD', 'RS', 'RV', 'RVA', 'RVB', 'SDOR', 'SN', 'SN I', 'SN II',
                                           'SN II-L', 'SN II-P', 'SN IIa', 'SN IIb', 'SN IId', 'SN IIn', 'SN Ia', 'SN Ia-CSM', 'SN Iax', 'SN Ib', 'SN Ic',
                                           'SN Ic-BL', 'SN-pec', 'SPB', 'SPBe', 'SR', 'SRA', 'SRB', 'SRC', 'SRD', 'SRS', 'SXARI', 'SXARI/E', 'SXPHE', 'SXPHE(B)',
                                           'TTS', 'TTS/ROT', 'UG', 'UGER', 'UGSS', 'UGSU', 'UGWZ', 'UGZ', 'UGZ/IW', 'UV', 'UVN',
                                           'UXOR', 'V1093HER', 'V361HYA', 'V838MON', 'WDP', 'WR', 'WTTS', 'WTTS/ROT', 'X', 'ZAND',
                                           'ZZ', 'ZZ/GWLIB', 'ZZA', 'ZZA/O', 'ZZB', 'ZZLep', 'ZZO', 'cPNB[e]', 'roAm', 'roAp']))

        self.ztf_rem_ok.toggle()
        self.ztf_rem_ok.clicked.connect(self.ZTF)

        self.panstarrs_rem_ok.clicked.connect(self.PanStarrs)

        self.comm_line_in.setPlainText("Gaia DR3 position.")

        self.settings_btn.clicked.connect(self.show_settings)

        self.inf_btn.clicked.connect(self.inform_show)

    def inform_show(self):
        self.information = about_program()

    def closeEvent(self, event):
        if self.settig != "":
            self.settig.close()
        if self.show_errwin != "":
            self.show_errwin.close()
        if self.information != "":
            self.information.close()

    def resizeEvent(self, event):
        self.settings_btn.move(self.width() - 200, self.settings_btn.y())
        self.clear_btn.move(self.width()- 200, self.clear_btn.y())
        self.beak_btn.move(self.width()- 200, self.beak_btn.y())
        self.dark_btn.move(self.width() - 200, self.dark_btn.y())
        self.file_btn.move(self.width()//2 - 100, self.file_btn.y())
        self.inf_btn.move(self.width() - 200, self.inf_btn.y())

    def show_settings(self):
        self.settig = setting()
        self.settig.fill_inf()
        self.settig.show()
        self.settig.ui.butn.clicked.connect(self.settig.chek_value)
        self.settig.ui.butn.clicked.connect(self.success)

    def success(self):
        if self.settig.successfully:
            self.settig.start()
            with open("setting.txt") as f:
                self.path_star = f.readline().split("\n")[0]
            self.settig.close()

    def dark(self):
        wid = [self.max_mag_in, self.min_mag_in, self.per_line_in, self.Epoch_line_in, self.eclipse_line_in]
        if self.dark_btn.text() == "Темная тема":
            self.dark_value = True
            self.dark_btn.setText("Светлая тема")
            self.setStyleSheet(darkstele)
            self.star_name_in.setStyleSheet(darkstele)
            self.coor_line_in.setStyleSheet(darkstele)
            normal_wid(wid, darkstele)
            if self.key_err == 1:
                self.star_name_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            if self.key_err == 2 or self.key_err == 3:
                self.coor_line_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            if self.key_err >= 4:
                wid[self.key_err-4].setStyleSheet("border: 2px solid rgb(248, 0, 0)")
        else:
            self.dark_value = False
            self.dark_btn.setText("Темная тема")
            self.setStyleSheet(standartstele)
            self.coor_line_in.setStyleSheet(standartstele)
            self.star_name_in.setStyleSheet(standartstele)
            normal_wid(wid, standartstele)
            if self.key_err == 1:
                self.star_name_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            if self.key_err == 2 or self.key_err == 3:
                self.coor_line_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            if self.key_err >= 4:
                wid[self.key_err-4].setStyleSheet("border: 2px solid rgb(248, 0, 0)")

    def create_file(self):
        wid = [self.max_mag_in, self.min_mag_in, self.per_line_in, self.Epoch_line_in, self.eclipse_line_in]
        if self.star_name_in.text() == "" or self.star_name_in.text() == "Обязательное поле":
            self.star_name_in.setText("Обязательное поле")
            if self.dark_value:
                normal_wid(wid, darkstele)
                self.coor_line_in.setStyleSheet(darkstele)
            else:
                normal_wid(wid, standartstele)
                self.coor_line_in.setStyleSheet(standartstele)
            self.key_err =1
            self.star_name_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.show_errwin = errWind("Укажите имя звезды!")
            self.show_errwin.show()
        elif self.coor_line_in.text() == "" or self.coor_line_in.text() == "Обязательное поле":
            self.coor_line_in.setText("Обязательное поле")
            if self.dark_value:
                normal_wid(wid, darkstele)
                self.star_name_in.setStyleSheet(darkstele)
            else:
                normal_wid(wid, standartstele)
                self.star_name_in.setStyleSheet(standartstele)
            self.key_err =2
            self.coor_line_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.show_errwin = errWind("Укажите координаты звезды!")
            self.show_errwin.show()
        elif not(is_coord(self.coor_line_in.text())):
            self.key_err = 3
            if self.dark_value:
                normal_wid(wid, darkstele)
                self.star_name_in.setStyleSheet(darkstele)
            else:
                normal_wid(wid, standartstele)
            self.coor_line_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.show_errwin = errWind("Не правельный формат координат!\nФормат хх хх хх.ххх ±хх хх хх.ххх\nПример 23 56 32.019 +00 18 25.14")
            self.show_errwin.show()
        else:
            self.key_err = 0
            style = "border: 2px solid rgb(248, 0, 0)"
            if self.dark_value:
                self.coor_line_in.setStyleSheet(darkstele)
                self.star_name_in.setStyleSheet(darkstele)
                not_err_style = darkstele
            else:
                self.coor_line_in.setStyleSheet(standartstele)
                self.star_name_in.setStyleSheet(standartstele)
                not_err_style = standartstele
            self.key_err = fiend_err(wid, style, 4)
            normal_wid(wid[:self.key_err - 4] +wid[self.key_err- 3:], not_err_style)
            err_text = {4: "Максимальная магнитуда должена быть числом!", 5: "Минимальная магнитуда должена быть числом!",
                        6: "Период должен быть числом!",7 :"Эпоха должена быть числом!", 8: "Процент затмения должен быть числом!"}
            if self.key_err in err_text:
                self.show_errwin = errWind(err_text[self.key_err])
                self.show_errwin.show()

        if self.key_err == 0:
            mp = {'ACV', 'BY', 'CTTS/ROT', 'ELL', 'FKCOM', 'HB', 'LERI', 'PSR', 'R', 'ROT', 'RS', 'SXARI', 'SXARI/E', 'TTS/ROT', 'WTTS/ROT','ACEP',
                  'ACYG', 'AHB1', 'BCEP', 'BCEPS', 'BLAP', 'BXCIR', 'CEP', 'CW', 'CWA', 'CWB', 'DCEP', 'DCEP(B)', 'DCEPS', 'DCEPS(B)',
                  'DSCT', 'GDOR', 'HADS', 'HADS(B)', 'L', 'M', 'PPN', 'roAm', 'roAp',
                  'RR', 'RRAB', 'RRC', 'RRD', 'RV', 'RVA', 'RVB', 'SPB', 'SR', 'SRA', 'SRB', 'SRC', 'SRD', 'SRS', 'SXPHE', 'SXPHE(B)', 'V361HYA',
                  'V1093HER', 'ZZ', 'ZZ/GWLIB', 'DPV', 'DYPer', 'RCB', 'UVN', 'ZZA/O'}
            mip = {'E', 'EA', 'EB', 'EP', 'EW'}

            stn = self.star_name_in.text()
            p = self.path_star + "\ "[0] +stn

            try:
                if self.oth_name_in.toPlainText() == "":
                    o = OtherName(self.coor_line_in.text())
                    a = o.getname()
                    stroka_oth_name = ""
                    for i in range(len(a)):
                        stroka_oth_name += a[i][0]+"   "+ a[i][1] + "\n"
                    self.oth_name_in.setPlainText(stroka_oth_name)
            except:
                self.show_errwin = errWind("Не удалось получить обозначения в каталогах!")
                self.show_errwin.show()
                return -1

            try:
                makedirs(p)
            except:
                pass
            try:
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
            except:
                self.show_errwin = errWind("Не удалось получить данные наблюдений!")
                self.show_errwin.show()
                return -1

            current_type = self.type_line_in.currentText()
            subtype = ""
            special_type = self.type_line_in_n.text()
            if special_type != "":
                if "+" in special_type or '\ '[0] in special_type:
                    if '\ '[0] in special_type:
                        delitel = '\ '[0]
                    else:
                        delitel = "+"
                    razd = special_type.split(delitel)
                    current_type = razd[0]
                    subtype = razd[1]
                else:
                    current_type = special_type

            if (self.per_line_in.text() == "" or self.Epoch_line_in.text() == "") and (self.type_line_in.currentText() in mp or self.type_line_in.currentText() in mip) or self.per_line_in.text() != "" or subtype == "E":
                if self.type_line_in.currentText() in mp or self.per_line_in.text() != "":
                    per, ep = map(str, Lafler_clinman(p+"\ "[0]+max(z, key=lambda x: x[1])[0]))
                else:
                    per, ep = map(str, Lafler_clinman(p + "\ "[0] + max(z, key=lambda x: x[1])[0], max=False))
                if self.per_line_in.text() == "":
                    self.per_line_in.setText(per)
                if self.Epoch_line_in.text() == "":
                    self.Epoch_line_in.setText(ep)

            if z != []:
                current_path = []
                special_path = []
                for i in range(len(z)):
                    if current_type not in mip and self.per_line_in.text() != '' and subtype != "E":
                        l = LightCurve(self.per_line_in.text(), p+"\ "[0]+z[i][0], "Максимуме", "Other" ,self.Epoch_line_in.text(), z[i][0][4], p)
                        l.make_LightCurve_with_per(False)
                        current_path.append([p+"\ "[0]+"Other"+z[i][0][4]+"P.txt", z[i][0][4], "ZTF"])
                    elif current_type in mip:
                        l = LightCurve(self.per_line_in.text(), p+"\ "[0]+z[i][0], "Минимуме", "Other" ,self.Epoch_line_in.text(), z[i][0][4], p)
                        l.make_LightCurve_with_per(False)
                        current_path.append([p + "\ "[0] + "Other" + z[i][0][4] + "P.txt", z[i][0][4], "ZTF"])
                    else:
                        current_path.append([p+"\ "[0]+z[i][0], z[i][0][4], "ZTF"])

                    if subtype == "E":
                        l = LightCurve(self.per_line_in.text(), p + "\ "[0] + z[i][0], "Минимуме", "Other",
                                       self.Epoch_line_in.text(), z[i][0][4], p)
                        l.make_LightCurve_with_per(False)
                        special_path.append([p + "\ "[0] + "Other" + z[i][0][4] + "P.txt", z[i][0][4], "ZTF"])

                if self.per_line_in.text() != "" and subtype != "E":
                    gr =makeGrapf(current_path, p, self.star_name_in.text(), True)
                    gr.make()
                else:
                    gr = makeGrapf(current_path, p, self.star_name_in.text())
                    gr.make()

                if subtype == "E":
                    gr = makeGrapf(special_path, p, self.star_name_in.text(), True)
                    gr.make()

                if self.eclipse_line_in.text() == "" and (self.type_line_in.currentText() in mip):
                    eclips_value = eclipse_percent(current_path[0][0])
                    self.eclipse_line_in.setText(str(eclips_value))

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
                if self.Epoch_line_in.text() != "":
                    f.writelines("Epoch: " + str(float(self.Epoch_line_in.text()) + 2400000.5) + "\n")
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
        self.comm_line_in.setPlainText("Gaia DR3 position.")
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

    def w1(self):
        self.w1 = setting()
        try:
            with open("setting.txt") as f:
                pass
        except:
            a = "setting.txt"
            a = a
            with open(a, "w") as f:
                pass
        with open("setting.txt", "r") as f:
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
        with open("setting.txt") as f:
            self.path_save = f.read().split("\n")[1]
        self.prev_file = False
        self.key_error = 0
        self.dark_value = False
        self.show_errwin = ""
        self.settig = ""
        self.information = ""

    def initUI(self):
        user = ctypes.windll.user32
        self.setGeometry(0, 0, user.GetSystemMetrics(0), user.GetSystemMetrics(1))
        loadUi(refiend_path("UIplates.ui"), self)
        self.setWindowTitle('Star Assistant')
        self.setStyleSheet(standartstele)
        self.setMinimumSize(1200, 700)

        self.dark_btn.clicked.connect(self.dark)

        self.R_btn.clicked.connect(self.get_r)

        self.G_btn.clicked.connect(self.get_g)

        self.B_btn.clicked.connect(self.get_b)

        self.color_btn.clicked.connect(self.color)

        self.clear_btn.clicked.connect(self.clear)

        self.butn4.clicked.connect(self.preview)

        self.settings_btn.clicked.connect(self.show_settings)

        self.inf_btn.clicked.connect(self.inform_show)

    def inform_show(self):
        self.information = about_program()

    def closeEvent(self, event):
        if self.settig != "":
            self.settig.close()
        if self.show_errwin != "":
            self.show_errwin.close()
        if self.information != "":
            self.information.close()

    def resizeEvent(self, event):
        self.settings_btn.move(self.width() - 200, self.settings_btn.y())
        self.butn4.move(self.width()- 200, self.butn4.y())
        self.clear_btn.move(self.width()- 200, self.clear_btn.y())
        self.beak_btn.move(self.width()- 200, self.beak_btn.y())
        self.dark_btn.move(self.width() - 200, self.dark_btn.y())
        self.color_btn.move(self.width() // 2 - 50, self.color_btn.y())
        self.inf_btn.move(self.width() - 200, self.inf_btn.y())

    def show_settings(self):
        self.settig = setting()
        self.settig.fill_inf()
        self.settig.show()
        self.settig.ui.butn.clicked.connect(self.settig.chek_value)
        self.settig.ui.butn.clicked.connect(self.success)

    def success(self):
        if self.settig.successfully:
            self.settig.start()
            with open("setting.txt") as f:
                self.path_save = f.read().split("\n")[1]
            self.settig.close()

    def dark(self):
        if self.dark_btn.text() == "Темная тема":
            self.dark_value = True
            self.setStyleSheet(darkstele)
            self.dark_btn.setText("Светлая тема")
            self.R_line.setStyleSheet(darkstele)
            self.G_line.setStyleSheet(darkstele)
            self.B_line.setStyleSheet(darkstele)
            self.name_in.setStyleSheet(darkstele)
            if self.key_error == 1:
                self.R_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.key_error == 2:
                self.G_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.key_error == 3:
                self.B_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.key_error == 4:
                self.name_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
        else:
            self.dark_value = False
            self.dark_btn.setText("Темная тема")
            self.setStyleSheet(standartstele)
            self.R_line.setStyleSheet(standartstele)
            self.G_line.setStyleSheet(standartstele)
            self.B_line.setStyleSheet(standartstele)
            self.name_in.setStyleSheet(standartstele)
            if self.key_error == 1:
                self.R_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.key_error == 2:
                self.G_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.key_error == 3:
                self.B_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            elif self.key_error == 4:
                self.name_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")

    def get_r(self):
        self.R_line.setText(QFileDialog().getOpenFileName(self, "Open project", "", "Image Files (*.fits)")[0])

    def get_b(self):
        self.B_line.setText(QFileDialog().getOpenFileName(self, "Open project", "", "Image Files (*.fits)")[0])

    def get_g(self):
        self.G_line.setText(QFileDialog().getOpenFileName(self, "Open project", "", "Image Files (*.fits)")[0])

    def preview(self):
        self.prev_file =True
        self.color()
        if self.key_error == 0:
            self.pr = previewwin(self.prev_file)
            self.pr.show()
        self.prev_file = False

    def color(self):
        if self.dark_value:
            self.R_line.setStyleSheet(darkstele)
            self.G_line.setStyleSheet(darkstele)
            self.B_line.setStyleSheet(darkstele)
            self.name_in.setStyleSheet(darkstele)
        else:
            self.R_line.setStyleSheet(standartstele)
            self.G_line.setStyleSheet(standartstele)
            self.B_line.setStyleSheet(standartstele)
            self.name_in.setStyleSheet(standartstele)

        if self.name_in.text() == "":
            self.name_in.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.key_error = 4
            self.show_errwin = errWind("Введите имя звезды!")
            self.show_errwin.show()
        elif (self.R_line.text() == "" or self.R_line.text() == "Выберете файл") and self.color_combinations_value.currentText() == "BRIR":
            self.R_line.setText("Выберете файл")
            self.R_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.key_error = 1
            self.show_errwin = errWind("Не выбран файл!")
            self.show_errwin.show()
        elif self.G_line.text() == "" or self.G_line.text() == "Выберете файл":
            self.G_line.setText("Выберете файл")
            self.G_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.show_errwin = errWind("Не выбран файл!")
            self.show_errwin.show()
            self.key_error = 2
        elif self.B_line.text() == "" or self.B_line.text() == "Выберете файл":
            self.show_errwin = errWind("Не выбран файл!")
            self.show_errwin.show()
            self.B_line.setText("Выберете файл")
            self.B_line.setStyleSheet("border: 2px solid rgb(248, 0, 0)")
            self.key_error = 3
        else:
            self.key_error = 0
            save_as = self.name_in.text()
            data = []
            type_comb = self.color_combinations_value.currentText()
            data.append(self.G_line.text())
            data.append(self.B_line.text())
            if type_comb == "BRIR":
                data.append(self.R_line.text())
            color = Image.new("RGB", (1240, 1240), 'white')
            data_png = []

            for i in range(len(data)):
                image_data = fits.getdata(data[i])
                pyp.figure(figsize=(20, 20))
                pyp.imshow(image_data, cmap='gray')
                pyp.colorbar()
                if i == 0:
                    name = self.path_save + '/GRIN.png'
                elif i == 1:
                    name = self.path_save + '/BLUE.png'
                else:
                    name = self.path_save + '/RED.png'
                data_png.append(name)
                pyp.savefig(name)
                pyp.close()

            if type_comb != "BRIR":
                data_rot = [0, self.rot_image(data_png[0], data_png[1]), 0]
                image_g = Image.open(data_png[0])
                image_b = Image.open(data_png[1]).rotate(data_rot[1])
                image_br = Image.blend(image_b, image_g, alpha=0.5)
                image_br.save(self.path_save + "/BandR.png")
                data_png.append(self.path_save + "/BandR.png")
            else:
                data_rot = [self.rot_image(data_png[2], data_png[0]), self.rot_image(data_png[2], data_png[1]), 0]

            delta_color = []
            for name in data_png:
                image = Image.open(name)
                stat = ImageStat.Stat(image).mean
                delta_color.append(stat[0])

            max_color = max(delta_color)
            for i in range(len(delta_color)):
                delta_color[i] = round(max_color - delta_color[i])

            for i in range(len(data_png)):
                image = Image.open(data_png[i])
                image = image.crop((250, 390, 1490, 1630))
                image = image.rotate(data_rot[i])
                pixels = image.load()
                color_p = color.load()
                for y in range(image.size[0]):
                    for x in range(image.size[1]):
                        zn = color_p[y, x]
                        if i == 0:
                            zn = (1, pixels[y, x][i] + delta_color[i], 1)
                        elif i == 1:
                            zn = (1, zn[1], pixels[y, x][i] + delta_color[i])
                        else:
                            zn = (pixels[y, x][i] + delta_color[i], zn[1], zn[2])
                        color_p[y, x] = zn
            colorsize = self.color_size_value.currentText()
            if colorsize == "10'x10'":
                color = color.crop((200, 200, 1040, 1040))
            else:
                color = color.crop((400, 400, 840, 840))
            color = ImageOps.flip(color.resize((800, 800)))
            dr = ImageDraw.Draw(color)
            dr.line(((370, 400), (390, 400)), fill=(255, 255, 255))
            dr.line(((410, 400), (430, 400)), fill=(255, 255, 255))
            font = ImageFont.truetype("arial.ttf", 40)
            dr.text((400, 50), save_as, fill="#FFFFFF", font=font, anchor="ms")
            font = ImageFont.truetype("arial.ttf", 30)
            if type_comb == "BRIR":
                dr.text((100, 775), "Chart: " + self.color_combinations_value.currentText(), fill="#FFFFFF", font=font,
                        anchor="ms")
            else:
                dr.text((150, 775), "Chart: " + self.color_combinations_value.currentText(), fill="#FFFFFF", font=font,
                        anchor="ms")
            dr.text((700, 775), "FOV: " + self.color_size_value.currentText(), fill="#FFFFFF", font=font, anchor="ms")
            color.save(self.path_save + "/" + save_as.strip() + " chart.png")
            if self.prev_file:
                self.prev_file = self.path_save + "/" + save_as.strip() + " chart.png"
            self.start = False

    def clear(self):
        self.R_line.clear()
        self.G_line.clear()
        self.B_line.clear()
        self.name_in.setText("Color")

    def rot_image(self, basic_img, rot_img):
        image_main = Image.open(basic_img).crop((250, 390, 1490, 1630))
        image_rot = Image.open(rot_img).crop((250, 390, 1490, 1630))
        ma = 0
        angle = 0
        for i in range(-50, 50, 2):
            if i < 0:
                rt = (3600 + i) / 10
            else:
                rt = i / 10
            rot = image_rot.rotate(rt).crop((200, 200, 600, 600)).load()
            main = image_main.crop((200, 200, 600, 600)).load()
            s = 0
            for v in range(400):
                for w in range(400):
                    if rot[v, w][0] > 100 or main[v, w][0] > 100:
                        if rot[v, w][0] > 100 and main[v, w][0] < 100 or rot[v, w][0] < 100 and main[v, w][0] > 100:
                            s += 1
                        else:
                            s += 4
            if s > ma:
                ma = s
                angle = rt
        return angle

class win2(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.wi2 = ""
        self.wi3 = ""
        self.wi4 = ""

    def w1(self):
        self.wi1 = vari()
        self.wi1.show()
        self.wi1.ui.btn_OBR.clicked.connect(self.w2)
        self.wi1.ui.btn_Reg.clicked.connect(self.w3)
        self.wi1.ui.plate_OBR.clicked.connect(self.w4)
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