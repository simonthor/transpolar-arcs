from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib import cm
import numpy as np


def hist1d(foreground, background, axis: Axes, dataset_name: str, normalize=True, nbins=40, norm_ymax=10, log=False):
    """Plots 1D histogram of e.g. BxGSM.
    foreground (array_like): data for the TPAs.
    background (array_like): all the data for the IMF during the period of the dataset.
    """
    foreground = foreground[~np.isnan(foreground)]
    background = background[~np.isnan(background)]

    axis.axvline(0, color="grey", lw=1, zorder=-1)
    fg_hist_values, bins, _ = axis.hist(foreground, bins=nbins, weights=np.ones_like(foreground) / len(foreground),
                                        label=dataset_name, histtype='step', zorder=1)
    bg_hist_values, _, _ = axis.hist(background, bins=bins, weights=np.ones_like(background) / len(background),
                                        label='total IMF', histtype='step', zorder=0)
    if normalize:
        normalized_axis = axis.twinx()  # instantiate a second axes that shares the same x-axis
        normalized_axis.axhline(1, ls="--", color='lightgrey', lw=1)
        masked_bg_hist_values = np.ma.masked_where(bg_hist_values == 0, bg_hist_values)
        normalized_axis.step((bins[1:]+bins[:-1]) / 2, fg_hist_values / masked_bg_hist_values,
                             where='mid', c='g', label='IMF normalized', zorder=2)
        normalized_axis.set_ylim(0, norm_ymax)
        label = normalized_axis.set_ylabel('IMF normalized TPA distribution', color='g')
        label.set_color('g')

    axis.legend()
    if log:
        axis.set_xscale('log')

    axis.set_ylabel('Probability Distribution')
    axis.minorticks_on()

    return fg_hist_values, bg_hist_values, bins


def hist2d_scatter(x, y, bg_x, bg_y, axis: Axes, dataset_name: str, normalize=True, marker_color: str = 'k', bins=300,
                   colormap_name: str = 'jet', color_bar=False):
    """Plots 2D histogram with two parameters (e.g. BxGSM and ByGSM).
    x, y (array_like): Values of the TPAs for the parameter that will be plotted on the x- or y-axis.
                       This data will correspond to the dots in the plot.
    bg_x, bg_y (array_like): Values of the IMF over the period of the dataset.
                             These will form the background (colored tiles) of the plot
    """
    colormap = cm.get_cmap(colormap_name)
    axis.axhline(0, color='grey', zorder=1)
    axis.axvline(0, color='grey', zorder=1)
    omit_index = np.isnan(x) | np.isnan(y)
    x = x[~omit_index]
    y = y[~omit_index]
    bg_omit_index = np.isnan(bg_x) | np.isnan(bg_y)
    bg_x = bg_x[~bg_omit_index]
    bg_y = bg_y[~bg_omit_index]
    counts, xedges, yedges, im = axis.hist2d(bg_x, bg_y, bins=bins, cmap=colormap, density=normalize, zorder=0)

    if color_bar:
        cbar = plt.colorbar(im, ax=axis)
        cbar.set_label('IMF probability distribution', rotation=270, labelpad=10)

    axis.scatter(x, y, s=30, marker='P', edgecolors='w', linewidth=0.5, label=dataset_name, c=marker_color, zorder=2)
    axis.set_facecolor(colormap(0))
    axis.legend(loc=1)

