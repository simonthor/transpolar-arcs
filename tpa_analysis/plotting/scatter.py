from contextlib import contextmanager

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes


# TODO: create template figure for scatter plots? E.g:
@contextmanager
def scatter_template(xlim=None, ylim=None, save=False, *args, **kwargs):
    fig, ax = plt.subplots(*args, **kwargs)
    ax.axhline(0, color='grey', zorder=-1)
    ax.axvline(0, color='grey', zorder=-1)
    yield fig, ax
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    if save:
        fig.savefig(save)
    fig.show()
    fig.close()


def scatter(x, y, axis: Axes, dataset_name: str, marker_color: str = 'k', *args, **kwargs):
    axis.axhline(0, color='grey', zorder=-1)
    axis.axvline(0, color='grey', zorder=-1)
    omit_index = np.isnan(x) | np.isnan(y)
    x = x[~omit_index]
    y = y[~omit_index]
    axis.scatter(x, y, s=30, marker='P', edgecolors='w', linewidth=0.5, label=dataset_name, c=marker_color, zorder=2,
                 *args, **kwargs)
    axis.legend(loc=1)
