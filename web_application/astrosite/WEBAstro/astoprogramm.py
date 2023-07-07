import math
import re
import seaborn as sns
import requests
from pandas import DataFrame
import matplotlib.pyplot as pyp



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

def LK1(a):
    s = 0
    for i in range(len(a)):
        s += (a[i][1] - a[i - 1][1]) ** 8
    return s

def drob(n):
    return n - math.floor(n)

def Lafler_clinman(data, max = True):
    if max:
        ma = 32
    else:
        ma = -32
    ep0 = 0
    for i in range(len(data)):
            if data[i][1] < ma and max:
                ma = data[i][1]
                ep0 = data[i][0]
            elif data[i][1] > ma and not(max):
                ma = data[i][1]
                ep0 = data[i][0]
    pmin = 0.5
    pmax = 1000
    wmin = 1 / pmax
    wmax = 1 / pmin
    p = []
    while wmin <= wmax:
        if 1/wmin > 400:
            step = 0.000005
        elif 1/wmin >100:
            step= 0.00001
        elif 1/wmin >10:
            step = 0.000025
        elif 1/wmin > 2:
            step=0.00005
        elif 1/wmin > 0.75:
            step=0.00015
        else:
            step = 0.0003

        b = []
        for i in range(len(data)):
            b.append([drob((data[i][0] - ep0) * wmin), data[i][1]])
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
                        self.other.append("URAT1 "+ a[i+3][7:17])
                        s["URAT1"] = ""
            if a[i].count("galex_ais")==1 and a[i+7] == "NOWRAP>GALEX" and "J" in a[i+8]:
                if "GALEX" not in s:
                    self.other.append("GALEX "+ a[i+8][:-5])
                    s["GALEX"] = ""
            if "===" in a[i] and "AllWISE" not in a[i]:
                b = a[i].split(";")
                b = re.split("===|&|'", b[3])
                if "%2b" in b[1]:
                    b[1] = r"{}+{}".format(*b[1].split("%2b"))
                if b[0] == "2MASS":
                    b[1] = "J"+b[1]
                if b[0] not in s:
                    self.other.append(b[0]+" "+ b[1])
                    s[b[0]] = ""
        return self.other


class ZTF_Points:
    def __init__(self, coord):#на вход координаты и путь куда будут сохраняться файлы / mag - если true то ищет магнитуду дополнительео выводит масив макс зн \мин зн\ фильтр
        self.ssilka1 = "https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?spatial=box&catalog=ztf_objects_dr15&objstr={}h+{}m+{}s+{}d+{}m+{}s&size=10&outfmt=1".format(*coord.split())
        #запрос к ztf из которого я получаю какие именно данные наблюдений мне нужно запрасить в дальнейшем
        self.ssilka2 = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?ID={}"#запрос данных
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
        res_g = []
        res_r = []
        for i in range(len(b)):
            if i%23==0:
                if ((float(b[i+1])-ra)**2+(float(b[i+2])-dec)**2)**0.5*3600 <1.5:#проверяю чтобы выбранные данные были ближе 1.5 арксек
                    if b[i+8][1] =="g":#данные фильтра g
                        name_g.append([b[i], int(b[i+12])])
                    if b[i+8][1] == "r":#данные фильтра r
                        name_r.append([b[i], int(b[i+12])])
        ret = {}
        magn = []
        if name_g != []:
            g_mag = [100, -100, "g"]
            name_g = max(name_g, key=lambda x:x[1])[0]#выбираю тот набор в котором больше всего наблюдений
            data = requests.get(self.ssilka2.format(name_g)).text.split()#получаю данные наблюдений
            if "<TR>" in data:
                kol = 0
                for i in range(len(data)):
                    if data[i] == "<TR>":
                        kol+=1
                        res_g.append([float(re.split("<|>", data[i + 4])[2][:12]) , float(re.split("<|>", data[i + 5])[2][:6])])
                        if float(re.split("<|>", data[i + 5])[2][:6]) < g_mag[0] and len(data[i + 7])<11:#код ошибки наблюдений на i+7
                            g_mag[0]=float(re.split("<|>", data[i + 5])[2][:6])
                        if float(re.split("<|>", data[i + 5])[2][:6]) > g_mag[1] and len(data[i + 7])<11:
                            g_mag[1] = float(re.split("<|>", data[i + 5])[2][:6])
                magn.append(g_mag)
                if kol != 0:
                    ret["ZTF g"] = res_g

        if name_r != []:
            r_mag = [100, -100, "r"]
            name_r = max(name_r, key=lambda x: x[1])[0]#выбираю тот набор в котором больше всего наблюдений
            data = requests.get(self.ssilka2.format(name_r)).text.split()#получаю данные наблюдений
            if "<TR>" in data:
                kol = 0
                for i in range(len(data)):
                    if data[i] == "<TR>":
                        kol += 1
                        res_r.append([float(re.split("<|>", data[i + 4])[2][:12]) ,  float(re.split("<|>", data[i + 5])[2][:6])])
                        if float(re.split("<|>", data[i + 5])[2][:6]) < r_mag[0] and len(data[i + 7]) < 11:
                            r_mag[0] = float(re.split("<|>", data[i + 5])[2][:6])
                        if float(re.split("<|>", data[i + 5])[2][:6]) > r_mag[1] and len(data[i + 7]) < 11:
                            r_mag[1] = float(re.split("<|>", data[i + 5])[2][:6])
                magn.append(r_mag)
                if kol != 0:
                    ret["ZTF r"] = res_r
        ret["magn"] = max(magn, key=lambda x: abs(x[0]- x[1]))
        return ret

class makeGrapf:#создает график из данных файла. формат данных в фале 2 сторки. ось x ось у
    def __init__(self,name, data, phase=False):#массив с путями к файлам\куда сохранять\название сохраняемого файла\фазовый или обычный график
        self.name = name
        self.data = data
        self.phase = phase
    def make(self):
        ymin = 99
        ymax = 0
        x = []
        y = []
        value = []
        for y in range(len(self.data)):
            for i in range(len(self.data[y][0])):
                x.append(self.data[y][0][i][0])
                y.append(self.data[y][0][i][1])
                value.append(self.data[y][1])
        mi, ma = min(y), max(y)
        if mi < ymin:
            ymin = mi
        if ma > ymax:
            ymax = ma

        data = DataFrame({"x":x, "y":y, "data":value})
        color = {"ZTF r":"#f80000", "ZTF g":"#000080"}
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
        return pyp


def make_LightCurve_with_per(data, epoch, period):
    res = []
    for i in range(len(data)):
        rez = (float(data[i][0]) - epoch) / float(period)
        rez_c = math.floor(rez)
        res.append([round((rez - rez_c), 6) , data[i][1]])
        res.append([round((rez - rez_c)-1, 6) , data[i][1]])

    return res