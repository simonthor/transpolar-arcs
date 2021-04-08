from .hist import *
from .scatter import *
from scipy.constants import mu_0


def magnetic_energy_flux(v, bx, by, bz):
    """Calculate magnetic flux of IMF"""
    return v * (bx**2+by**2+bz**2)/2*mu_0


def get_legend_texts(xlabel):
    """Create str that can be used as legend in plots based on which parameter that is plotted."""
    plot_variable = xlabel[:xlabel.find('(')-1]
    return plot_variable + ' at arc start', plot_variable + ' background'


def get_pvalue_text(p_value: float, decimals: int = 4) -> str:
    """Convert p value into a concise string that can be included in plots."""
    p_str = f'%.{decimals}'
    if 0.01 < p_value:
        return (p_str + 'f') % p_value
    return (p_str + 'e') % p_value


def subplot_label(ax, letter=None, x=-0.07, y=1.02):
    """Add a, b, c etc to subplot"""
    if not isinstance(ax, np.ndarray):
        ax = np.array([ax])

    for a, l in zip(ax.flat, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if letter is None else letter):
        a.text(x, y, l, transform=a.transAxes, fontsize='xx-large', fontweight='bold')


