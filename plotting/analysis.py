import numpy as np
from scipy import stats


def compare_dists(sample: np.ndarray, comparison: np.ndarray, dof: int = 0, priority='sample', order=0) -> float:

    if (sample < 5).sum() or (comparison < 5).sum():
        # Merge categories to make them at least 5
        pass

    return stats.chisquare(sample, comparison, dof)
