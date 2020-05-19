import datetime as dt

from matplotlib import pyplot as plt
import numpy as np

from data_extract import DataExtract
from data_structures.tpa_dataset import TPADataset
from plotting import *


if __name__ == '__main__':
    variable = 'BxGSM'
    tpa_dir = 'data/'
    OMNI_data_dir = r'C:\Users\simon\MATLABProjects\KTH research\Data\OMNI\OMNI_1min_Lv1'
    # TODO: automate plotting labels, axis limits, paras_in etc using variable instead of paras_in
    paras_in = ['vel', 'BxGSM', 'ByGSM', 'BzGSM']
    plotfig = True
    savefig = False
    avgcalctime = 20  # minutes
    timeshift = 100
    hemadjust = True
    norm = True
    ylim = 35
    figure_filename = "results/TPA_hist_{}_all_{}_{}minavg{}{}{}_reidy.pdf"

    datasets = [TPADataset('Fear & Milan (2012)', avgcalctime, timeshift, dt.date(2000, 6, 1), dt.date(2005, 10, 1)),
                TPADataset('Kullen et al. (2002)', avgcalctime, timeshift, dt.date(1998, 12, 1), dt.date(1999, 3, 1)),
                TPADataset('Cumnock et al. (2009)', avgcalctime, timeshift + 120, dt.date(1996, 1, 1),
                           dt.date(1999, 1, 1)),
                TPADataset('Reidy et al. (2018)', avgcalctime, timeshift, dt.date(2015, 12, 1), dt.date(2016, 1, 1))]

    data_extractor = DataExtract(dir)
    for dataset in datasets:
        # TODO?: asyncio/yield?
        TPAs = data_extractor.get_tpas(dataset.name)
        for TPA in TPAs:
            TPA.get_parameters(variable, timeshift=dataset.time_shift, avgcalctime=dataset.average_calctime)

        dataset.append(TPAs)

    fig, axes = plt.subplots(nrows=2, ncols=2, sharey='all', sharex='all')
    axes = np.asarray(axes).flatten()
    for ax, dataset in zip(axes, datasets):
        hist1d((dataset.tpa_values[variable], dataset.total[variable]), ax, ratio=True)
        ax.set_xlabel()

    plt.savefig(figure_filename)
