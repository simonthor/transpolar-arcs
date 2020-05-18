# %%
import pandas as pd
import datetime
from geopack import geopack
import matplotlib.pyplot as plt
import numpy as np
import sys
import importlib
test_OMNI = importlib.import_module('test_OMNI')


# %%
class TPA:
    def __init__(self, dataset, date, hemisphere="unknown", dipole=True, Bx=None):
        self.dataset = dataset

        if type(date) == datetime.datetime:
            self.date = date
            self.hem = hemisphere
        else:
            raise TypeError("Format of TPA.date is incorrect. Must be datetime.datetime")

        if dipole is True:
            dipoles = []
            for i in range(avgcalctime):
                t = (date - datetime.datetime(1970, 1, 1) - datetime.timedelta(minutes=i+timeshift)).total_seconds()
                dipoles.append(180 / np.pi * geopack.recalc(t))

            self.dipole = sum(dipoles) / len(dipoles)
        elif dipole is not None:
            self.dipole = dipole

        if type(Bx) == int or type(Bx) == float or Bx is None:
            self.Bx = Bx
        elif type(Bx) == list:
            self.Bx = sum(Bx) / len(Bx)
        else:
            raise TypeError("Format of TPA.Bx is incorrect. Must be int, float or list")

    def __repr__(self):
        return "Transpolar Arc class (by sthor)"

    def __str__(self):
        return "TPA identified by: {}\n" \
               "hemisphere: {}\n" \
               "formation date:{}\n" \
               "dipole tilt: {}\n" \
               "Bx: {}\n".format(self.dataset, self.hem, self.date, self.dipole, self.Bx)


# %%
def kullen_dataclean(filename="datafile_tpa_location.dat"):
    """Cleaning Kullen's data (dat)"""
    filename = tpa_dir + filename
    TPAs = []

    with open(filename) as dat:
        kullen = dat.readlines()

    for line in kullen:
        cl = line.split()
        if line[0] not in "\n;" and cl[1][2] == "1":
            if cl[1][:2] != "bd":
                TPAs.append(TPA("Kullen", datetime.datetime.strptime(cl[0] + line[11:15], "%y%m%d%H%M"), "n"))
            elif cl[1][:4] == "bd1h":
                TPAs.append(TPA("Kullen", datetime.datetime.strptime(cl[0] + line[11:15], "%y%m%d%H%M"), "n"))
    #for tpa in TPAs:
    #    print(tpa.date)
    return TPAs


# %%
def cumnock0_dataclean(filename="Single_Multiple_Arcs_IMF_dipole_list_2015_AK.xls", sheet_name="Sheet1", usecols="A, C, D"):
    """Cleaning Judy's first data (excel)"""

    filename = tpa_dir + filename
    TPAs = []

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
            date = datetime.datetime.strptime(str(row[0]) + row[2][:row[2].find("-")], "%y%j%H%M%S")# - datetime.timedelta(minutes=30)
            TPAs.append(TPA("Cumnock0", date, row[1]))

    #for tpa in TPAs:
    #    print(tpa.date)

    return TPAs


# %%
def cumnock1_dataclean(filename="listoftimes.xls", sheet_name="Sheet1", usecols="A, G"):
    """Cleaning Judy's second data (excel)"""
    TPAs = []
    filename = tpa_dir + filename

    judy = pd.read_excel(filename, sheet_name=sheet_name, index_col=None, usecols=usecols, skiprows=[1, 2])

    for index, row in judy.iterrows():
        if type(row[0]) == int:
            if len(str(row[0])) >= 5:
                TPAs.append(TPA("Cumnock1", datetime.datetime.strptime(str(row[0]) + str(row[1]), "%y%j%X"), "n"))
            else:
                date = "0" * (5-len(str(row[0]))) + str(row[0]) + str(row[1])
                TPAs.append(TPA("Cumnock1", datetime.datetime.strptime(date, "%y%j%X")))
    #for tpa in TPAs:
    #    print(tpa.date)
    return TPAs


# %%
def cai_dataclean(filename=""):
    """Empty function that will later be used for cleaning Cai's dataset of TPAs from DMSP.
    Dataset with conjugate TPAs."""
    return


# %%
def fear_fileclean():
    """Cleaning Fear's data to readable txt (txt)"""
    clean = ""
    with open("fear_TPA_data.txt", "r") as fear:
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


# %%
def fear_dataclean(filename="fear_TPA_data.txt"):
    """Cleaning Fear's data (txt)"""

    filename = tpa_dir + filename
    TPAs = []

    with open(filename) as fear:
        for line in fear:
            try:
                int(line.split()[0])
                tpa = True
            except:
                tpa = False
            if tpa:
                l = line.split()
                TPAs.append(TPA("Fear", datetime.datetime.strptime(l[1] + l[2][:8], "%d-%b-%Y%X"), l[3]))

    #for date in TPAs:
    #    print(date)
    return TPAs


# %%
def plot_settings():
    plt.axhline(0, color="grey")
    plt.axvline(0, color="grey")
    plt.axis([-40, 40, -10, 10])
    plt.xlabel("Dipole tilt")
    plt.ylabel("IMF $B_X$")
    plt.minorticks_on()


# %%
if __name__ == "__main__":

    tpa_dir = "data/"
    OMNI_dir = 'C:/Users/simon/MATLABProjects/Data/OMNI/OMNI_1min_Lv1/'
    paras_in = ['BxGSM']
    plotfig = True
    savefig = False
    avgcalctime = 30  # minutes

    print("filtering TPAs and creating lists")
    for timeshift in range(30, 31, 1000000):
        data = {"Fear": fear_dataclean(),
                "Kullen": kullen_dataclean(),
                "Cumnock0": cumnock0_dataclean(),
                "Cumnock1": cumnock1_dataclean(),
                }

        for dataset in data.values():
            print(len(dataset))

        for i, dataset in enumerate(data):
            print("loading OMNI data and calculating dipole tilt (%i/%i)" % (i+1, len(data)))
            for tpa in data[dataset]:
                start_time = tpa.date - datetime.timedelta(minutes=avgcalctime+timeshift)
                end_time = tpa.date - datetime.timedelta(minutes=timeshift)
                loadObj = test_OMNI.LoadOMNI(start_time, end_time, data_dir=OMNI_dir)
                loadObj.laod_OMNI_data(paras_in=paras_in)
                BxGSM = [Bx for Bx in loadObj.paras['BxGSM'] if not np.isnan(Bx)]
                if len(BxGSM) == 0:
                    tpa.Bx = np.nan
                else:
                    tpa.Bx = sum(BxGSM) / len(BxGSM)

                if tpa.hem == "s":
                    tpa.dipole *= -1
                    tpa.Bx *= -1
                #datetimelist = loadObj.paras['datetime']
            print(dataset + ":", len(data[dataset]) - len([tpa for tpa in data[dataset] if not np.isnan(tpa.Bx)]), "TPAs missing", len(data[dataset]))

        print("plotting")
        if not plotfig:
            plt.ioff()
        plt.figure(figsize=(7, 7))
        #plt.title("IMF $B_x$ & dipole tilt dependence (hemisphere-adjusted)")

        for i, dataset in enumerate(data):
            plt.subplot(2, 2, i+1)
            plot_settings()
            plt.plot([tpa.dipole for tpa in data[dataset]], [tpa.Bx for tpa in data[dataset]], ".", ms=4, label=dataset)
            plt.legend()

        plt.tight_layout()
        if plotfig:
            plt.show()
        #else:
        #    plt.ioff()
        if savefig:
            plt.savefig("results/TPA_scatter_alldata_{}_{}minavg.pdf".format(timeshift, timeshift+avgcalctime))
    #input("press enter to continue to next plot")
    #plt.close()

# %%
print("date\tBx\tDipole tilt")
for tpa in data["Cumnock0"]:
    print(tpa.date, "\t", tpa.Bx, "\t", tpa.dipole)

## %%
#for dataset in data:
#    for tpa in data[dataset]:
#        bf = tpa.date.timestamp()
#        af = tpa.date.replace(tzinfo=datetime.timezone.utc).timestamp()
#        if bf != af:
#            print(False)
#            print((af - bf)/60)
#        else:
#            print(True)
