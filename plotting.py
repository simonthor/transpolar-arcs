from typing import Tuple, Sequence
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import numpy as np


def create_label(variable):
    xlabel = ""
    match = False
    if variable[0] == "v":
        xlabel += "v"
        match = True
    if "GSM" in variable:
        xlabel += "IMF "
        match = True
    if "B" in variable:
        xlabel += f"$B_{variable[variable.find('B')+1]}$ (nT)"
        match = True
    if variable == "vB^2":
        xlabel = f"${variable}$"
        match = True
    if not match:
        xlabel = variable

    return xlabel


def hist1d(foreground, background, axis: Axes, dataset_name: str, normalize=True, bins=np.linspace(-20, 20, 40), norm_ymax=10, log=False):
    axis.axvline(0, color="grey", lw=1, zorder=-1)
    # TODO?: make this iterable
    fg_hist_bin_values, _, _ = axis.hist(foreground, bins=bins, weights=np.ones_like(foreground) / len(foreground),
                                         label='Average IMF', histtype='step', zorder=1)
    # TODO: nbins is a bad name
    bg_hist_bin_values, nbins, _ = axis.hist(background, bins=bins, weights=np.ones_like(background) / len(background),
                                         label=dataset_name, histtype='step', zorder=0)
    if normalize:
        normalized_axes = axis.twinx()  # instantiate a second axes that shares the same x-axis
        normalized_axes.axhline(1, ls="--", color="lightgrey", lw=1)
        # TODO: midbins is a bad name
        midbins = 0.5 * (nbins[1:] + nbins[:-1])
        # TODO: hist_bin_values is a bad name
        hist_bin_values = np.ma.masked_where(bg_hist_bin_values == 0, bg_hist_bin_values)
        normalized_axes.step(midbins, fg_hist_bin_values / hist_bin_values, where='mid', c='g', label="IMF normalized", zorder=2)
        normalized_axes.set_ylim(0, norm_ymax)
        label = normalized_axes.set_ylabel('IMF normalized TPA distribution', color='g')
        label.set_color('g')

    axis.legend()
    axis.set_ylim(0, 0.2)
    if log:
        axis.set_xscale("log")

    axis.set_ylabel('Probability Distribution')

    axis.minorticks_on()
