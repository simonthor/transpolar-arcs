import matplotlib.pyplot as plt
import numpy as np
from TPA.data_struct import *
from TPA.data_extract import DataExtract
from scipy.stats import mstats as st
#from TPA import test_OMNI
#import sys

# Declare variables
tpa_dir = "data/"
OMNI_dir = 'C:/Users/simon/MATLABProjects/Data/OMNI/OMNI_1min_Lv1/'
paras_in = ['BxGSM']
plotfig = False
savefig = True
avgcalctime = 20  # minutes
timeshift = [100]
hemadjust = True
special = 'hem'
filename = "results/TPA_scatter_{}_all_{}_{}minavg_dipole_{}_{}_reidy.pdf"

# Creating datasets that will hold TPAs
print("Creating datasets")
datasets = [Dataset("Fear & Milan (2012)", avgcalctime, timeshift[0], datetime.date(2000, 6, 1), datetime.date(2005, 10, 1)),
            Dataset("Kullen et al. (2002)", avgcalctime, timeshift[0], datetime.date(1998, 12, 1), datetime.date(1999, 3, 1)),
            Dataset("Cumnock et al. (2009)", avgcalctime, timeshift[0] + 120, datetime.date(1996, 1, 1), datetime.date(1999, 1, 1)),
            Dataset("Reidy et al. (2018)", avgcalctime, timeshift[0], datetime.date(2015, 12, 1), datetime.date(2016, 1, 1))
            #Dataset("Cumnock (2005)", avgcalctime, timeshift[0], datetime.date(1996, 3, 1), datetime.date(2000, 10, 1))
            ]

# Extracting IMF during the period of the dataset and loading it into the datasets
for i, dataset in enumerate(datasets):
    print("loading background IMF (%i/%i)" % (i + 1, len(datasets)))
    dataset.total(OMNI_dir, paras_in)
    print("Background IMF loaded")

# Loading TPAs into the datasets
extract_data = DataExtract(tpa_dir)
extract_data.fear_dataclean(datasets[0], filename="Fear_TPA_data_frompaper.txt")
extract_data.kullen_dataclean(datasets[1])
extract_data.cumnock0_dataclean(datasets[2], filename="Single_Multiple_Arcs_IMF_dipole_list_2015_AK.xls", usecols="A, C, D")
#extract_data.cumnock1_dataclean(datasets[3], usecols="A, G, M")
extract_data.reidy_dataclean(datasets[3])
del extract_data

# Iterating through all timeshifts and creating different plots for each timeshift
for ts in timeshift:
    clean_tpas = {}
    # Loading OMNI data for each TPA
    for i, dataset in enumerate(datasets):
        dn = dataset.name
        clean_tpas[dn] = np.empty(len(dataset.tpas), dtype=bool)
        dataset.timeshift = ts
        for tpa in dataset.tpas:
            tpa.avg(OMNI_dir, paras_in)
            # Adjust for hemisphere
            if hemadjust and tpa.hem == "s":
                tpa.dipole *= -1
                tpa.IMF["BxGSM"] *= -1
                tpa.IMF["ByGSM"] *= -1

        print("Average IMF for TPAs calculated")
        # Counting number of TPAs that had valid OMNIdata
        for i, tpa in enumerate(dataset.tpas):
            valid_tpa = True
            for para in paras_in:
                if np.isnan(tpa.IMF[para]):
                    valid_tpa = False
                    break
            if valid_tpa:
                clean_tpas[dn][i] = True
            else:
                clean_tpas[dn][i] = False

        print(dn + ":", len(dataset.tpas) - np.sum(clean_tpas[dn]), "TPAs missing ({}/{})".format(int(np.sum(clean_tpas[dn])), len(dataset.tpas)))

    # Plot
    print("plotting")
    if not plotfig:
        plt.ioff()
    f, ax = plt.subplots(nrows=2, ncols=2, figsize=(9, 8), sharex="all", sharey="all")

    # Defining x- and y-axis labels

    for i, dataset in enumerate(datasets):
        print("creating subplot for dataset %i/%i" % (i + 1, len(datasets)))
        sp = ax.flat[i]
        sp.axhline(0, color="grey", zorder=1)
        sp.axvline(0, color="grey", zorder=1)
        sp.set_xlabel('Dipole tilt (degrees)')
        sp.set_ylabel('IMF $B_X$ (nT)')
        x = dataset.vars[paras_in[0]]
        x = x[~np.isnan(x)]
        color = np.empty(len(dataset.tpas), dtype=str)
        color[:] = "k"
        if special == "moving":
            color = np.where(dataset.get(special) == "yes", "magenta", color)
        elif special == "dadu":
            color = []
            for dadu in dataset.get(special):
                if "dawn" in dadu:
                    color.append('r')
                elif "dusk" in dadu:
                    color.append('k')
                else:
                    color.append('teal')
        elif special == "hem":
            color = np.where(dataset.get(special) == "s", "c", color)
        elif not special:
            color = "k"
        else:
            raise ValueError("Variable {} is not implemented for plotting yet".format(special))

        sp.scatter(dataset.get('dipole'), dataset.get(paras_in[0]),
                   s=30, marker="P", edgecolors="w", linewidth=0.5, label=dataset.name,
                   c=color, zorder=2)

        sp.legend(loc=1)

    plt.minorticks_on()
    plt.axis([-40, 40, -20, 20])
    plt.tight_layout()
    paras = ""
    for i in paras_in:
        paras += i
    if savefig:
        print("saving plot")
        plt.savefig(filename.format(paras, ts, ts+avgcalctime, 'hemadjust' if hemadjust else '', special))
        plt.close()
    if plotfig:
        plt.show()

print('Done.')
