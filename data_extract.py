from data_struct import *
import datetime
import pandas as pd


class DataExtract:
    def __init__(self, tpa_dir):
        self.tpa_dir = tpa_dir

    def kullen_dataclean(self, dataset, filename="datafile_tpa_location.dat"):
        """Extracting Kullen's data (dat)"""
        filename = self.tpa_dir + filename
        TPAs = dataset.tpas

        with open(filename) as dat:
            kullen = dat.readlines()

        for line in kullen:
            cl = line.split()
            if line[0] not in "\n;" and cl[1][2] == "1":
                motion = calc_motion(float(cl[3]), float(cl[6]))
                #elif cl[1][2] == "2":
                #    motion = "unknown"
                #else:
                #    continue
                dadu = calc_dadu(float(cl[3]))
                if cl[1][:2] != "bd":
                    TPAs.append(TPA(dataset, datetime.datetime.strptime(cl[0] + line[11:15], "%y%m%d%H%M"), "n", moving=motion, dadu=dadu, dipole=True))
                elif cl[1][:4] == "bd1h":
                    TPAs.append(TPA(dataset, datetime.datetime.strptime(cl[0] + line[11:15], "%y%m%d%H%M"), "n", moving=motion, dadu=dadu, dipole=True))

        return TPAs

    def cumnock0_dataclean(self, dataset, filename="Single_Multiple_Arcs_IMF_dipole_list_2015_AK_prel_dadu.xls", usecols="A, C, D, N", sheet_name="Sheet1"):
        """Extracting Judy's first data (excel)"""

        filename = self.tpa_dir + filename
        TPAs = dataset.tpas

        judy = pd.read_excel(filename, sheet_name=sheet_name, index_col=None, usecols=usecols)
        for index, row in judy.iterrows():
            try:
                if int(row[0]) > 1:
                    num = True
                else:
                    num = False
            except:
                num = False
                if type(row[0]) == str and "Single" in row[0]:
                    break
            if num:
                # Warning: Change the last timedelta object to vary the shift backwards in time
                date = datetime.datetime.strptime(str(row[0]) + row[2][:row[2].find("-")], "%y%j%H%M%S") - datetime.timedelta(minutes=120)
                if "dadu" in filename:
                    dadu = row[3]
                else:
                    dadu = None
                TPAs.append(TPA(dataset, date, row[1], moving="yes", dadu=dadu, dipole=True))

        return TPAs

    def cumnock1_dataclean(self, dataset, filename="listoftimes.xls", sheet_name="Sheet1",  usecols="A, G, M"):
        """Extracting Judy's second data (excel)"""
        TPAs = dataset.tpas
        filename = self.tpa_dir + filename

        judy = pd.read_excel(filename, sheet_name=sheet_name, index_col=None, usecols=usecols, skiprows=[1, 2])

        for index, row in judy.iterrows():
            if "Do not" in str(row[0]):
                break
            elif isinstance(row[0], int) or "00" in str(row[0]):
                if len(str(row[0])) >= 5:
                    TPAs.append(TPA(dataset, datetime.datetime.strptime(str(row[0]) + str(row[1]), "%y%j%X"), "n", moving="yes", dadu=row[2], dipole=True))
                else:
                    date = "0" * (5-len(str(row[0]))) + str(row[0]) + str(row[1])
                    if len(usecols.split()) > 2:
                        dadu = row[2]
                    else:
                        dadu = None
                    TPAs.append(TPA(dataset, datetime.datetime.strptime(date, "%y%j%X"), "n", moving="yes", dadu=dadu, dipole=True))
        #for tpa in TPAs:
        #    print(tpa.date)
        return TPAs

    def cai_dataclean(self, dataset, filename=""):
        """Empty function that will later be used for extracting Cai's dataset of TPAs from DMSP.
        Dataset with conjugate TPAs.
        TODO: add this function when I have received the data"""
        return

    def fear_fileclean(self, filename="Fear_TPA_data_frompaper.txt"):
        """Cleaning Fear's data to readable txt (txt)"""
        clean = ""
        with open(filename, "r") as fear:
            for line in fear:
                if not line.split() == []:
                    if line[0] == " ":
                        space = 0
                        for ch in line:
                            if ch == " ":
                                space += 1
                            else:
                                break
                        clean += line[space:]
                    else:
                        clean += line
        with open("fear_TPA_data.txt", "w") as fear:
            fear.write(clean)

    def fear_dataclean(self, dataset, filename="fear_TPA_data_frompaper.txt"):
        """Extracting Fear's data (txt)"""
        filename = self.tpa_dir + filename
        TPAs = dataset.tpas

        if "frompaper" in filename:
            with open(filename) as fear:
                for line in fear:
                    try:
                        int(line.split()[0])
                        tpa = True
                    except ValueError:
                        tpa = False
                    if tpa:
                        l = line.split()
                        if l[10] == "N":
                            motion = "no"
                        elif l[10] == "Y":
                            motion = "yes"
                        else:
                            motion = l[10]
                            # TODO: better error message
                            print("WARNING: input for motion is neither Yes nor No")
                        dadu = calc_dadu(float(l[7]))

                        TPAs.append(TPA(dataset, datetime.datetime.strptime(l[1] + l[2] + ":00", "%d-%b-%Y%X"),
                                        hemisphere=l[9].lower(), moving=motion, dadu=dadu, dipole=True))
        else:
            with open(filename) as fear:
                for line in fear:
                    try:
                        int(line.split()[0])
                        tpa = True
                    except ValueError:
                        tpa = False
                    if tpa:
                        l = line.split()
                        TPAs.append(TPA(dataset, datetime.datetime.strptime(l[1] + l[2][:8], "%d-%b-%Y%X"), l[3], dipole=True))

        return TPAs

    def reidy_dataclean(self, dataset, filename="reidy_TPA_data.txt"):
        filename = self.tpa_dir + filename
        TPAs = dataset.tpas
        with open(filename) as reidy:
            for line in reidy:
                if line[0] != "#":
                    l = line.split()
                    if l[9] == "NS":
                        TPAs.append(TPA(dataset, datetime.datetime.strptime(l[1] + l[2] + l[3] + l[4], "%d%b%Y%H:%M"),
                                        hemisphere="n", dipole=True, conj=True))
                        TPAs.append(TPA(dataset, datetime.datetime.strptime(l[1] + l[2] + l[3] + l[4], "%d%b%Y%H:%M"),
                                        hemisphere="s", dipole=True, conj=True))
                    else:
                        TPAs.append(TPA(dataset, datetime.datetime.strptime(l[1] + l[2] + l[3] + l[4], "%d%b%Y%H:%M"),
                                        hemisphere=l[9].lower(), dipole=True, conj=False))
        return TPAs


def calc_motion(mlt1, mlt2):
    d = abs(mlt2 - mlt1)
    if d > 12:
        d = 24 - d
    if d > 2:
        motion = "yes"
    else:
        motion = "no"

    return motion


def calc_dadu(mlt):
    if 0 < mlt <= 12:
        dadu = "dawn"
    else:
        dadu = "dusk"
    # else:
    #    print("Unknown value of dadu (dawn or dusk): {}".format(mlt1))
    #    dadu = None

    return dadu


if __name__ == "__main__":
    a = Dataset("reidy", 20, 100, datetime.date(2000, 10, 20), datetime.date(2000, 10, 30))
    b = DataExtract("data/")
    b.reidy_dataclean(a)
    print(len(a.tpas))
    for tpa in a.tpas:
        print(tpa)
