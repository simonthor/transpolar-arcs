#import datetime
#import sys
import matplotlib.pyplot as plt
import numpy as np
from data_struct import *
from data_extract import DataExtract
#from TPA import test_OMNI

tpa_dir = "data/"
OMNI_dir = 'C:/Users/simon/MATLABProjects/Data/OMNI/OMNI_1min_Lv1/'
# TODO: automate plotting labels, axis limits, paras_in etc using variable instead of paras_in
variable = "vB^2"
#set_paras_in(parameter)
paras_in = ['vel', 'BxGSM', 'ByGSM', 'BzGSM']
plotfig = False
savefig = True
avgcalctime = 20  # minutes
timeshift = [100]
ts = timeshift[0]
hemadjust = True
norm = True
ylim = [35]
filename = "results/TPA_hist_{}_all_{}_{}minavg{}{}{}_reidy.pdf"

print("Creating datasets")
datasets = [Dataset("Fear & Milan (2012)", avgcalctime, timeshift[0], datetime.date(2000, 6, 1), datetime.date(2005, 10, 1)),
            Dataset("Kullen et al. (2002)", avgcalctime, timeshift[0], datetime.date(1998, 12, 1), datetime.date(1999, 3, 1)),
            Dataset("Cumnock et al. (2009)", avgcalctime, timeshift[0] + 120, datetime.date(1996, 1, 1), datetime.date(1999, 1, 1)),
            Dataset("Reidy et al. (2018)", avgcalctime, timeshift[0], datetime.date(2015, 12, 1), datetime.date(2016, 1, 1))
            #Dataset("Cumnock (2005)", avgcalctime, timeshift[0], datetime.date(1996, 3, 1), datetime.date(2000, 10, 1))
            ]

# Extracting IMF during the period of the dataset and loading it into the datasets
for i, dataset in enumerate(datasets):
    print("loading background (%i/%i)" % (i + 1, len(datasets)))
    dataset.total(OMNI_dir, paras_in)
    #dataset.vars["BmagGSM"] = np.sqrt(dataset.get_total("BxGSM") ** 2 + dataset.get_total("ByGSM") ** 2 + dataset.get_total("ByGSM") ** 2)
    print("Background loaded")

# Loading TPAs into the datasets
extract_data = DataExtract(tpa_dir)
extract_data.fear_dataclean(datasets[0])
extract_data.kullen_dataclean(datasets[1])
extract_data.cumnock0_dataclean(datasets[2])
extract_data.reidy_dataclean(datasets[3])
#extract_data.cumnock1_dataclean(datasets[3])
del extract_data

for yl in ylim:
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

        print("Average for TPAs calculated")
        # TODO: Try to make this counter shorter using numpy
        # Counting number of TPAs that had valid OMNIdata
        for i, tpa in enumerate(dataset.tpas):
            valid_tpa = True
            for para in paras_in:
                if np.isnan(getattr(tpa, para)):
                    valid_tpa = False
                    break
            if valid_tpa:
                clean_tpas[dn][i] = True
            else:
                clean_tpas[dn][i] = False

        print(dn + ":", len(dataset.tpas) - np.sum(clean_tpas[dn]), "TPAs missing ({}/{})".format(int(np.sum(clean_tpas[dn])), len(dataset.tpas)))

    print("plotting")
    if not plotfig:
        plt.ioff()

    f, ax = plt.subplots(nrows=2, ncols=2, figsize=(9, 8), sharex="all", sharey="all")
    xlabel = ""
    match = False
    bins = np.linspace(-20, 20, 40)
    if variable[0] == "v":
        xlabel += "v"
        match = True
        bins = np.linspace(0, 1000, 40)
    if "GSM" in variable:
        xlabel += "IMF "
        match = True
    if "B" in variable:
        xlabel += "$B_{} (nT)$".format(variable[variable.find("B")+1])
        match = True
    if variable == "vB^2":
        xlabel = "${}$".format(variable)
        match = True
        log = True
        bins = np.logspace(2, 6, 40)
    else:
        log = False
    if not match:
        xlabel = variable
    # if variable == "vB^2":
    #     xlabel = "$v B^2$"
    # elif variable == "BxGSM":
    #     xlabel = "IMF $B_X$"
    # elif variable == "ByGSM":
    #     xlabel = "IMF $B_Y$"
    # elif variable == "BzGSM":
    #     xlabel = "IMF $B_Z$"
    # elif variable == "|B|":
    #     xlabel = "IMF |B|"
    # elif variable == "vel":
    #     xlabel = "velocity"
    # elif variable == "vBy":
    #     xlabel = "$v B_Y$"
    # elif variable == "vBx":
    #     xlabel = "$v B_X$"
    # elif variable == "vBz":
    #     xlabel = "$v B_Z$"
    # else:
    #     xlabel = variable

    for i, dataset in enumerate(datasets):
        sp = ax.flat[i]
        #sp.axhline(0, color="grey")
        sp.axvline(0, color="grey", lw=1, zorder=-1)
        sp.set_xlabel(xlabel)
        sp.set_ylabel("Probability Distribution")
        bg = dataset.vars['vel'] * dataset.vars["BmagGSM"]**2
        bg = bg[~np.isnan(bg)]
        fg = dataset.get('vel') * dataset.get("BmagGSM")**2
        #fg_m = fg[np.where(dataset.get("moving") == "yes", True, False)]
        #fg_nm = fg[np.where(dataset.get("moving") == "no", True, False)]
        #fg_m = fg_m[~np.isnan(fg_m)]
        #fg_nm = fg_nm[~np.isnan(fg_nm)]
        #print("Size of movin:", fg_m.shape, "\nSize of oval-aligned", fg_nm.shape)
        #print(bg, fg)
        #sp.hist(fg_m, bins=bins, label=dataset.name + " moving", weights=np.ones_like(fg_m)/len(fg_m), histtype="step")

        fg = fg[~np.isnan(fg)]
        #bins = np.linspace(-20, 20, 40)
        histIMF, _, _ = sp.hist(bg, bins=bins, weights=np.ones_like(bg)/len(bg), label="Average IMF", histtype="step", zorder=0)
        hist, x, _ = sp.hist(fg, bins=bins, label=dataset.name, weights=np.ones_like(fg) / len(fg), histtype="step", zorder=0)
        if norm:
            sp2 = sp.twinx()  # instantiate a second axes that shares the same x-axis
            sp2.axhline(1, ls="--", color="lightgrey", lw=1)
            x = 0.5*(x[1:] + x[:-1])
            histIMF = np.ma.masked_where(histIMF == 0, histIMF)
            sp2.plot(x, hist/histIMF, "-", c="g", label="IMF normalized", zorder=1)
            sp2.set_ylim(0, yl)
            label = sp2.set_ylabel('IMF normalized TPA distribution', color="g")
            label.set_color("g")
            #lines, labels = sp.get_legend_handles_labels()
            #lines2, labels2 = sp2.get_legend_handles_labels()
            #sp2.legend(lines + lines2, labels + labels2)
        #else:
        sp.legend()
        #print("hist:", hist)
        #print("IMF:", histIMF)
        sp.set_ylim(0, 0.2)
        if log:
            sp.set_xscale("log")

    plt.minorticks_on()
    #plt.axis([-20, 20, 0, 0.02])
    plt.tight_layout()

    if savefig:
        plt.savefig(filename.format(variable, ts, ts+avgcalctime, "_hemadjust" if hemadjust else "", "_norm" if norm else "", yl))
        plt.close()
    if plotfig:
        plt.show()
