import datetime
import matplotlib.pyplot as plt
import numpy as np
from data_struct import *
from data_extract import DataExtract
from TPA import test_OMNI

tpa_dir = "data/"
OMNI_dir = 'C:/Users/simon/MATLABProjects/Data/OMNI/OMNI_1min_Lv1/'
# TODO: automate plotting labels, axis limits, paras_in etc using variable instead of paras_in
variable = "BxGSM"
paras_in = ['BxGSM', 'ByGSM', 'BzGSM']
plotfig = True
savefig = False
avgcalctime = 20  # minutes
timeshift = [100]
ts = timeshift[0]
hemadjust = True
norm = True
ylim = 35
filename = "results/TPA_hist_{}_combined_{}_{}minavg{}{}{}_reidy.pdf"

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
    print("Background loaded")

# Loading TPAs into the datasets
extract_data = DataExtract(tpa_dir)
extract_data.fear_dataclean(datasets[0])
extract_data.kullen_dataclean(datasets[1])
extract_data.cumnock0_dataclean(datasets[2])
extract_data.reidy_dataclean(datasets[3])
#extract_data.cumnock1_dataclean(datasets[3])
del extract_data

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

#%%
print("plotting")
if not plotfig:
    plt.ioff()

f, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 8))
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
    xlabel += "$B_{}$ (nT)".format(variable[variable.find("B")+1].upper())
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

bg = np.array([np.nan])
fg = np.array([np.nan])

for d in datasets:
    bg = np.append(bg, d.vars[variable])
    fg = np.append(fg, d.get(variable))

bg = bg[~np.isnan(bg)]
fg = fg[~np.isnan(fg)]

histIMF, _, _ = ax.hist(bg, bins=bins, weights=np.ones_like(bg)/len(bg), label="Average IMF", histtype="step", zorder=0)
hist, x, _ = ax.hist(fg, bins=bins, label='All datasets', weights=np.ones_like(fg) / len(fg), histtype="step", zorder=0)

if norm:
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.axhline(1, ls="--", color="lightgrey", lw=1)
    x = 0.5*(x[1:] + x[:-1])
    histIMF = np.ma.masked_where(histIMF == 0, histIMF)
    ax2.plot(x, hist/histIMF, "-", c="g", label="IMF normalized", zorder=1)
    ax2.set_ylim(0, ylim)
    label = ax2.set_ylabel('IMF normalized TPA distribution', color="g")
    label.set_color("g")
ax.legend()
ax.set_ylim(0, 0.2)
ax.set_ylabel("Probability Distribution")
ax.set_xlabel(xlabel)
print(xlabel)
ax.axvline(0, color="grey", lw=1, zorder=-1)

if log:
    ax.set_xscale("log")

plt.minorticks_on()
plt.tight_layout()

if savefig:
    plt.savefig(filename.format(variable, ts, ts+avgcalctime, "_hemadjust" if hemadjust else "", "_norm" if norm else "", ylim))
    plt.close()
if plotfig:
    plt.show()
