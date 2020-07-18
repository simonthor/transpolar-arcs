import numpy as np
from scipy import stats
from typing import Tuple


def compare_dists(sample: np.ndarray, comparison: np.ndarray, bins: np.ndarray, *args, **kwargs) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """Calculate chi-square test p-value for sample and comparison.
    Will bin samples with fewer values than smaller than 5
    """
    if (total := comparison.sum()) < 5:
        raise ValueError(f'Sum of comparison must be at least 5 but comparison only contained a total of {total}.')
    if comparison.size != sample.size or (bins.size - comparison.size) == 1:
	raise ValueError(f'comparison and sample must be equal size with bins being sample.size + 1. Instead, sizes {sample.size=}, {comparison.size=}, {bins.size=} were given.')

    if (comparison >= 5).all():
        _, p_value = stats.chisquare(sample, comparison, *args, **kwargs)
        return p_value, sample, comparison, bins

    # Use algorithm to merge bins to contain at least 5 elements
    merged_comparison, merged_sample, merged_bins = np.copy(comparison), np.copy(sample), np.array(bins, copy=True, dtype=float)

    for i in range(merged_comparison.size-1):
        if merged_comparison[i] < 5:
            merged_comparison[i+1] += merged_comparison[i]
            merged_comparison[i] = -1
            merged_sample[i+1] += merged_sample[i]
            merged_sample[i] = -1
            merged_bins[i+1] = np.nan

    merged_comparison = merged_comparison[merged_comparison != -1]
    merged_sample = merged_sample[merged_sample != -1]
    merged_bins = merged_bins[~np.isnan(merged_bins)]

    for i in reversed(range(1, merged_comparison.size)):
        if merged_comparison[i] < 5:
            merged_comparison[i-1] += merged_comparison[i]
            merged_comparison[i] = -1
            merged_sample[i-1] += merged_sample[i]
            merged_sample[i] = -1
            merged_bins[i] = np.nan

    merged_comparison = merged_comparison[merged_comparison != -1]
    merged_sample = merged_sample[merged_sample != -1]
    merged_bins = merged_bins[~np.isnan(merged_bins)]

    assert (merged_comparison >= 5).all(), merged_comparison

    _, p_value = stats.chisquare(merged_sample, merged_comparison, *args, **kwargs)
    return p_value, merged_comparison, merged_sample, merged_bins
