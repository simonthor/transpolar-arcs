import matplotlib.pyplot as plt
from matplotlib import cm
#import numpy as np
from data_struct import *
from data_extract import DataExtract
from scipy.stats import mstats as st
#from TPA import test_OMNI
#import sys

# Declare variables
tpa_dir = "data/"
OMNI_dir = 'C:/Users/simon/MATLABProjects/Data/OMNI/OMNI_1min_Lv1/'
paras_in = ['ByGSM', 'BxGSM']
plotfig = False
savefig = True
avgcalctime = 20  # minutes
timeshift = [100]
hemadjust = True
cmap = "jet"
special = 'dadu'
filename = "results/TPA_scatter_hist2d_{}_all_{}_{}minavg_{}_{}_reidy_conj.pdf"

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
        # TODO: Try to make this counter shorter using numpy
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
    f, ax = plt.subplots(nrows=2, ncols=2, figsize=(10, 8), sharex="all", sharey="all")

    # Defining x- and y-axis labels
    labels = ["IMF ${}$ (nT)"] * len(paras_in)
    for i, para in enumerate(paras_in):
        if para == "BxGSM":
            labels[i] = labels[i].format("B_X")
        elif para == "ByGSM":
            labels[i] = labels[i].format("B_Y")
        elif para == "BzGSM":
            labels[i] = labels[i].format("B_Z")
        else:
            raise IndexError("unknown parameter")

    cmap = cm.get_cmap(cmap)
    bgc = cmap(0)
    # TODO: add progress indicators in plotting
    for i, dataset in enumerate(datasets):
        print("creating subplot for dataset %i/%i" % (i + 1, len(datasets)))
        sp = ax.flat[i]
        sp.axhline(0, color="grey", zorder=1)
        sp.axvline(0, color="grey", zorder=1)
        sp.set_xlabel(labels[0])
        sp.set_ylabel(labels[1])
        x = dataset.vars[paras_in[0]]
        x = x[~np.isnan(x)]
        y = dataset.vars[paras_in[1]]
        y = y[~np.isnan(y)]
        counts, xedges, yedges, im = sp.hist2d(x, y, bins=300, cmap=cmap, density=True, zorder=0)
        cbar = plt.colorbar(im, ax=sp)
        cbar.set_label('IMF probability distribution', rotation=270, labelpad=10)
        color = np.empty(len(dataset.tpas), dtype=str)
        # TODO: Add more options for special
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
        # TODO: finish conjugate marker
        if dataset.name == "Reidy et al. (2018)":
            color = np.where(dataset.get('conj'), 'teal', 'w')

        sp.scatter(dataset.get(paras_in[0]), dataset.get(paras_in[1]),
                   s=30, marker="P", edgecolors="w", linewidth=0.5, label=dataset.name,
                   c=color, zorder=2)
        #x = np.ma.masked_where(np.any(np.array([np.isnan(dataset.get(paras_in[0])), np.isnan(dataset.get(paras_in[1]))]), axis=0), dataset.get(paras_in[0]))
        #y = np.ma.masked_where(np.any(np.array([np.isnan(dataset.get(paras_in[0])), np.isnan(dataset.get(paras_in[1]))]), axis=0), dataset.get(paras_in[1]))
        #np.save(dataset.name, np.array([dataset.get(paras_in[0]), dataset.get(paras_in[1])]))
        #slope, intercept, _, _, _ = st.linregress(x, y)
        #print(slope, intercept)
        #spearman, _ = st.spearmanr(x, y, nan_policy="raise")
        #sp.plot(np.linspace(-20, 20, 10), slope*np.linspace(-20, 20, 10)+intercept, "--", c="w", label="Linear regression", zorder=2)
        #sp.text(0.05, 0.05, r"$\rho = $" + str(spearman)[:7], transform=sp.transAxes, color="w")
        sp.set_facecolor(bgc)
        sp.legend(loc=1)

    plt.minorticks_on()
    plt.axis([-20, 20, -20, 20])
    plt.tight_layout()
    paras = ""
    for i in paras_in:
        paras += i
    if savefig:
        print("saving plot")
        plt.savefig(filename.format(paras, ts, ts+avgcalctime, 'hemadjust' if hemadjust else '', special if special else ''))
        plt.close()
    if plotfig:
        plt.show()

print('Done')
