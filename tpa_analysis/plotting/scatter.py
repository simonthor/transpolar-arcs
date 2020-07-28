from contextlib import contextmanager

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import matplotlib


# TODO: create template figure for scatter plots? E.g:
@contextmanager
def scatter_template(save: str = False, *args, **kwargs):
    fig, ax = plt.subplots(*args, **kwargs)
    if isinstance(ax, Axes):
        ax = [ax]

    for a in ax.flat:
        a.axhline(0, color='grey', zorder=-1)
        a.axvline(0, color='grey', zorder=-1)

    yield fig, ax

    fig.tight_layout()
    if save:
        fig.savefig(save)
    if 'inline' not in matplotlib.get_backend():
        fig.show()
    # TODO: Add functionality for deleting figure after use? E.g.: fig.clf()


def scatter(x, y, axis: Axes, dataset_name: str, marker_color: str = 'k', *args, **kwargs):
    axis.axhline(0, color='grey', zorder=-1)
    axis.axvline(0, color='grey', zorder=-1)
    axis.scatter(x, y, s=30, marker='P', edgecolors='w', linewidth=0.5, label=dataset_name, c=marker_color, zorder=2,
                 *args, **kwargs)
    axis.legend(loc=1)
