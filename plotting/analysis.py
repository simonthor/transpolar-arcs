import numpy as np
from scipy import stats


def compare_dists(sample: np.ndarray, comparison: np.ndarray, bins: np.ndarray, dof: int = 0) -> float:
    """Calculate chi-square test p-value for sample and comparison.
    Will bin samples with fewer values than smaller than 5"""
    if not (comparison < 5).sum():
        _, p_value = stats.chisquare(sample, comparison, dof)
        return p_value

    for bin_val, bin in zip(comparison, bins):
        if bin_val < 5:
            # Merge categories to make them at least 5
            pass

