#import datetime
#import sys
import matplotlib.pyplot as plt
#import numpy as np
from data_struct import *
from data_extract import DataExtract
#from TPA import test_OMNI


tpa_dir = "data/"
OMNI_dir = 'C:/Users/simon/MATLABProjects/Data/OMNI/OMNI_1min_Lv1/'
paras_in = ['ByGSM']
plotfig = False
savefig = True
avgcalctime = 20  # minutes
timeshift = [0]
hemadjust = True

print("filtering TPAs and creating lists")

# change IMF calculation time for each dataset (including both start month and end month):
# Cumnock0 (2009): 1/1996-12/1998   Cumnock1 (2005): 3/1996-9/2000 (preliminary)
# Kullen: 12/1998-2/1999            Fear: 6/2000-9/2005

datasets = {"Fear":     Dataset("Fear", avgcalctime, timeshift[0], datetime.date(2000, 6, 1), datetime.date(2005, 10, 1)),
            "Kullen":   Dataset("Kullen", avgcalctime, timeshift[0], datetime.date(1998, 12, 1), datetime.date(1999, 3, 1)),
            "Cumnock0": Dataset("Cumnock2009", avgcalctime, timeshift[0] + 120, datetime.date(1996, 1, 1), datetime.date(1999, 1, 1)),
            "Cumnock1": Dataset("Cumnock2005", avgcalctime, timeshift[0], datetime.date(1996, 3, 1), datetime.date(2000, 10, 1))
            }

extract_data = DataExtract(tpa_dir)
extract_data.fear_dataclean(datasets["Fear"])
extract_data.kullen_dataclean(datasets["Kullen"])
extract_data.cumnock0_dataclean(datasets["Cumnock0"])
extract_data.cumnock1_dataclean(datasets["Cumnock1"])

del extract_data

for i, dataset in enumerate(datasets.values()):
    print("loading background IMF (%i/%i)" % (i + 1, len(datasets)))
    dataset.total_IMF(OMNI_dir, paras_in)
    print("\tBackground IMF loaded")

for ts in timeshift:
    clean_tpas = {}
    for i, dataset in enumerate(datasets.values()):
        dataset.timeshift = ts
        for tpa in dataset.tpas:
            tpa.avg_IMF(OMNI_dir, paras_in)

            if hemadjust and tpa.hem == "s":
                tpa.dipole *= -1
                tpa.IMF["BxGSM"] *= -1
                tpa.IMF["ByGSM"] *= -1
            #datetimelist = loadObj.paras['datetime']
        print("\tAverage IMF for TPAs calculated")
        if len(paras_in) == 1:
            clean_tpas[dataset.name] = [tpa for tpa in dataset.tpas if not np.isnan(tpa.IMF[paras_in[0]])]
            valid_tpa_num = len(clean_tpas[dataset.name])
        else:
            raise IndexError("too many parameters for the current version of the program to handle")

        print(dataset.name + ":", len(dataset.tpas) - valid_tpa_num, "TPAs missing ({}/{})".format(valid_tpa_num, len(dataset.tpas)))

    print("plotting")
    if not plotfig:
        plt.ioff()

    f, ax = plt.subplots(nrows=2, ncols=2, figsize=(9, 8), sharex="all", sharey="all")

    xlabel = "IMF ${}$"
    if paras_in[0] == "BxGSM":
        xlabel = xlabel.format("B_X")
    elif paras_in[0] == "ByGSM":
        xlabel = xlabel.format("B_Y")
    elif paras_in[0] == "BzGSM":
        xlabel = xlabel.format("B_Z")
    else:
        raise IndexError("unknown parameter")

    for i, dataset in enumerate(datasets.values()):
        vals = dataset.tpas
        sp = ax.flat[i]
        sp.axhline(0, color="grey")
        sp.axvline(0, color="grey")
        sp.set_xlabel(xlabel)
        sp.set_ylabel("Distribution (%)")
        sp.hist(dataset.IMF[paras_in[0]], bins=np.linspace(-20, 20, 300), density=True, histtype="step")
        sp.hist([tpa.IMF[paras_in[0]] for tpa in clean_tpas[dataset.name]], bins=np.linspace(-20, 20, 40), label=dataset.name, density=True, histtype="step")
        sp.legend()

    plt.minorticks_on()
    plt.axis([-20, 20, 0, 0.25])
    plt.tight_layout()

    if savefig:
        plt.savefig("results/TPA_hist_{}_all_{}_{}minavg_hemadjust.pdf".format(paras_in[0], timeshift, timeshift+avgcalctime))
        plt.close()
    if plotfig:
        plt.show()
