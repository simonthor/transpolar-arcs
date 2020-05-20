# %%
import pandas as pd
import datetime
from geopack import geopack
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import importlib
test_OMNI = importlib.import_module('test_OMNI')


# %%
class TPA:
    def __init__(self, dataset, date, hemisphere="unknown", dipole=True, Bx=None, By=None, moving=None):
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

        if type(By) == int or type(By) == float or By is None:
            self.By = By
        elif type(By) == list:
            self.By = sum(By) / len(By)
        else:
            raise TypeError("Format of TPA.By is incorrect. Must be int, float or list")

        if moving is not None:
            if type(moving) in (int, float):
                self.moving = moving
            else:
                raise TypeError("Format of TPA.moving is incorrect. Must be int or float")

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
    Dataset with conjugate TPAs.
    TODO: add this function when I have received the data"""
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
if __name__ == "__main__":
    tpa_dir = "data/"
    OMNI_dir = 'C:/Users/simon/MATLABProjects/Data/OMNI/OMNI_1min_Lv1/'
    paras_in = ['BxGSM', 'ByGSM']
    plotfig = False
    savefig = True
    avgcalctime = 30  # minutes
    timeshift = 120
    hemadjust = True
    cmap = "jet"
    IMF = {}

    print("filtering TPAs and creating lists")
    data = {"Fear": fear_dataclean(),
            "Kullen": kullen_dataclean(),
            "Cumnock0": cumnock0_dataclean(),
            "Cumnock1": cumnock1_dataclean(),
            }

    for i, dataset in enumerate(data):
        print("loading OMNI data (%i/%i)" % (i+1, len(data)))
        vals = data[dataset]
        start_mon = min([tpa.date for tpa in vals])
        start_mon = start_mon.replace(day=1, hour=0, minute=0, second=0)
        end_mon = max([tpa.date for tpa in vals])
        end_mon = end_mon.replace(year=end_mon.year + int((end_mon.month + 1)/12), month=end_mon.month % 12 + 1,
                                  day=1, hour=0, minute=0, second=0)

        print(start_mon, end_mon)

        loadObj = test_OMNI.LoadOMNI(start_mon, end_mon, data_dir=OMNI_dir)
        loadObj.load_OMNI_data(paras_in=paras_in)
        totalBx = [Bx[0] for Bx in loadObj.paras['BxGSM'] if not np.isnan(Bx)]
        totalBy = [By[0] for By in loadObj.paras['ByGSM'] if not np.isnan(By)]

        if len(totalBx) == 0:
            raise FloatingPointError("No data found for this time period")

        if len(totalBy) == 0:
            raise FloatingPointError("No data found for this time period")

        indIMF = {'Bx': totalBx, 'By': totalBy}
        IMF[dataset] = indIMF
        print("\tBackground IMF loaded")

        for tpa in vals:
            # change IMF calculation time for each dataset (including both start month and end month):
            # Cumnock0 (2009): 1/1996-12/1998   Cumnock1 (2005): 3/1996-9/2000 (preliminary)
            # Kullen: 12/1998-2/1999            Fear: 6/2000-9/2005
            start_time = tpa.date - datetime.timedelta(minutes=avgcalctime+timeshift)
            end_time = tpa.date - datetime.timedelta(minutes=timeshift)
            loadObj = test_OMNI.LoadOMNI(start_time, end_time, data_dir=OMNI_dir)
            loadObj.load_OMNI_data(paras_in=paras_in)
            BxGSM = [Bx[0] for Bx in loadObj.paras['BxGSM'] if not np.isnan(Bx)]
            ByGSM = [By[0] for By in loadObj.paras['ByGSM'] if not np.isnan(By)]
            if len(BxGSM) == 0:
                tpa.Bx = np.nan
            else:
                tpa.Bx = sum(BxGSM) / len(BxGSM)

            if len(ByGSM) == 0:
                tpa.By = np.nan
            else:
                tpa.By = sum(ByGSM) / len(ByGSM)

            if hemadjust:
                if tpa.hem == "s":
                    tpa.dipole *= -1
                    tpa.Bx *= -1
            #datetimelist = loadObj.paras['datetime']
        valid_tpa_num = len([tpa for tpa in vals if not np.isnan(tpa.Bx)])
        print(dataset + ":", len(vals) - valid_tpa_num, "TPAs missing ({}/{})".format(valid_tpa_num, len(vals)))

    print("plotting")
    if not plotfig:
        plt.ioff()

    f, ax = plt.subplots(nrows=2, ncols=2, figsize=(9, 8), sharex="all", sharey="all")

    cmap = cm.get_cmap(cmap)
    bgc = cmap(0)

    for i, dataset in enumerate(data):
        sp = ax.flat[i]
        sp.axhline(0, color="grey")
        sp.axvline(0, color="grey")
        axislabels = list(IMF[dataset].keys())
        sp.set_xlabel(axislabels[1])
        sp.set_ylabel(axislabels[0])
        counts, xedges, yedges, im = sp.hist2d(IMF[dataset]['By'], IMF[dataset]['Bx'], bins=300, cmap=cmap)
        plt.colorbar(im, ax=sp)
        sp.plot([tpa.By for tpa in data[dataset]], [tpa.Bx for tpa in data[dataset]],
                "P", markerfacecolor='k', markeredgewidth=0.5, markeredgecolor="w", markersize=4, label=dataset)
        sp.set_facecolor(bgc)
        sp.legend()

    plt.minorticks_on()
    plt.axis([-20, 20, -20, 20])
    plt.tight_layout()

    if savefig:
        plt.savefig("results/TPA_scatter_hist2d_{}{}_all_{}_{}minavg_hemadjust.pdf".format(axislabels[0], axislabels[1], timeshift, timeshift+avgcalctime))
    if plotfig:
        plt.show()


## %%
# start_mon = datetime.datetime(2000, 1, 1, 0,0,0)
# end_mon = datetime.datetime(2000, 1, 2, 0,0,0)
#
# loadObj = test_OMNI.LoadOMNI(start_mon, end_mon, data_dir=OMNI_dir)
# loadObj.laod_OMNI_data(paras_in=["BxGSM", "ByGSM"])
# totalBx = [Bx[0] for Bx in loadObj.paras['BxGSM'] if not np.isnan(Bx)]
# totalBy = [By[0] for By in loadObj.paras['ByGSM'] if not np.isnan(By)]
#
# if len(totalBx) == 0:
#     raise FloatingPointError("No data found for this time period")
#
# if len(totalBy) == 0:
#     raise FloatingPointError("No data found for this time period")
#
# print(totalBx)
#
# plt.hist2d(totalBy, totalBx, bins=100)
# plt.axhline(0, color="grey")
# plt.axvline(0, color="grey")
# plt.xlabel("IMF $B_Y$")
# plt.ylabel("IMF $B_X$")
# plt.minorticks_on()
#
# plt.show()
