from typing import Tuple, Sequence
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib import cm
import numpy as np


def create_label(variable):
    """"""
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
    """Plots 1D histogram of e.g. BxGSM.
    foreground (array_like): data for the TPAs.
    background (array_like): all the data for the IMF during the period of the dataset.
    """
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
    if log:
        axis.set_xscale("log")

    axis.set_ylabel('Probability Distribution')
    axis.minorticks_on()


def hist2d(x, y, bg_x, bg_y, axis: Axes, labels: Tuple[str, str], dataset_name: str, marker_color: str = 'k',
           normalize=True, bins=300, colormap_name: str = 'jet', color_bar=False):
    """Plots 2D histogram with two parameters (e.g. BxGSM and ByGSM).
    x, y (array_like): Values of the TPAs for the parameter that will be plotted on the x- or y-axis.
                       This data will correspond to the dots in the plot.
    bg_x, bg_y (array_like): Values of the IMF over the period of the dataset.
                             These will form the background (colored tiles) of the plot
    """
    colormap = cm.get_cmap(colormap_name)
    axis.axhline(0, color='grey', zorder=1)
    axis.axvline(0, color='grey', zorder=1)
    counts, xedges, yedges, im = axis.hist2d(bg_x, bg_y, bins=bins, cmap=colormap, density=normalize, zorder=0)

    if color_bar:
        cbar = plt.colorbar(im, ax=axis)
        cbar.set_label('IMF probability distribution', rotation=270, labelpad=10)

    axis.scatter(x, y, s=30, marker="P", edgecolors="w", linewidth=0.5, label=dataset_name, c=marker_color, zorder=2)
    axis.set_facecolor(colormap(0))
    axis.legend(loc=1)
    axis.set_xlabel(labels[0])
    axis.set_ylabel(labels[1])

