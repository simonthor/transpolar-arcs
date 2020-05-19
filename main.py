# Standard library
import datetime as dt
from pathlib import Path
# Packages
from matplotlib import pyplot as plt
import numpy as np
# Self-written modules
from data_extract import DataExtract
from data_structures.tpa_dataset import TPADataset
from plotting import *


if __name__ == '__main__':
    variable = 'BxGSM'
    tpa_dir = 'data/'
    OMNI_data_dir = 'C:/Users/simon/MATLABProjects/KTH research/Data/OMNI/OMNI_1min_Lv1/'
    # TODO: automate plotting labels, axis limits, paras_in etc using variable instead of paras_in
    paras_in = ['BxGSM']
    plotfig = True
    savefig = False
    avgcalctime = 20    # minutes
    timeshift = 100     # minutes
    hemadjust = False   # Whether to revert the sign due to hemisphere or not
    norm = True         # Normalize and show relationship between background and TPA data
    ylim = 35           # Max number of normalized factors that the second axis will show
    figure_filename = "results/TPA_hist_{}_all_{}_{}minavg{}{}{}_reidy.pdf"

    datasets = (#TPADataset('Fear & Milan (2012)', avgcalctime, timeshift, dt.datetime(2000, 6, 1), dt.datetime(2005, 10, 1)),
                TPADataset('Kullen et al. (2002)', avgcalctime, timeshift, dt.datetime(1998, 12, 1), dt.datetime(1999, 3, 1)),
                #TPADataset('Cumnock et al. (2009)', avgcalctime, timeshift + 120, dt.datetime(1996, 1, 1),
                #           dt.datetime(1999, 1, 1)),
                TPADataset('Reidy et al. (2018)', avgcalctime, timeshift, dt.datetime(2015, 12, 1), dt.datetime(2016, 1, 1)))

    data_extractor = DataExtract(tpa_dir)
    print('gathering data')
    for dataset in datasets:
        dataset.get_dataset_parameters(OMNI_data_dir, paras_in)
        print('dataset parameters collected\nGathering TPA parameters')
        for TPA in data_extractor.get_tpas(dataset.name):
            TPA.get_parameters(OMNI_data_dir, paras_in, timeshift=dataset.time_shift, avgcalctime=dataset.average_calctime)
            dataset.append(TPA)

    # %% Plotting
    print("plotting")
    fig, axes = plt.subplots(ncols=len(datasets), figsize=(5*len(datasets), 5), sharey='all', sharex='all')
    axes = np.asarray(axes).flatten()
    for ax, dataset in zip(axes, datasets):
        hist1d(dataset.tpa_values[variable], dataset.total[variable], ax, dataset.name, normalize=norm, norm_ymax=ylim)
        ax.set_xlabel(create_label(variable))
    fig.tight_layout()

    if savefig:
        plt.savefig(figure_filename.format(variable, timeshift, timeshift + avgcalctime, "_hemadjust" if hemadjust else "", f"_norm{ylim}" if norm else ""))

    if plotfig:
        plt.show()
