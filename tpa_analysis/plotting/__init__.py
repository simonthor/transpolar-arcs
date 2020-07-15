from .hist import *
from .scatter import *


def vB2(v, bx, by, bz):
    """Calculate magnetic flux of IMF"""
    return v * (bx**2+by**2+bz**2)
