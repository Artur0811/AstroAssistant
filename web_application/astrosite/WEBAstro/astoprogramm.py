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
        if 1/wmin > 150:
            step = 0.00001
        elif 1/wmin > 100:
            step = 0.00005
        elif 1/wmin < 100:
            step = 0.0001
        elif 1/wmin < 10:
            step = 0.0005
        else:
            step = 0.001
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