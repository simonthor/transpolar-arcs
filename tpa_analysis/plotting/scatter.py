from contextlib import contextmanager
from matplotlib import pyplot as plt
import matplotlib
import numpy as np


@contextmanager
def scatter_template(save: str = False, *args, **kwargs):
    fig, ax = plt.subplots(*args, **kwargs)
    if not isinstance(ax, np.ndarray):
        ax = np.array([ax])

    for a, letter in zip(ax.flat, 'abcdefghijklmnopqrstuvwxyz'.upper()):
        a.axhline(0, color='grey', zorder=-1)
        a.axvline(0, color='grey', zorder=-1)
        from . import subplot_label
        subplot_label(a, letter)

    yield fig, ax

    fig.tight_layout()
    if save:
        fig.savefig(save)
    if 'inline' not in matplotlib.get_backend():
        fig.show()
    # TODO: Add functionality for deleting figure after use? E.g.: fig.clf()


def scatter(x, y, axis, dataset_name: str, marker_color: str = 'k', *args, **kwargs):
    axis.axhline(0, color='grey', zorder=-1)
    axis.axvline(0, color='grey', zorder=-1)
    axis.scatter(x, y, s=30, marker='P', edgecolors='w', linewidth=0.5, label=dataset_name, c=marker_color, zorder=2,
                 *args, **kwargs)
    axis.legend(loc=1)


if __name__ == '__main__':
    with scatter_template() as (fig, ax):
        ax[0].plot([0, 1], [0, 1])
