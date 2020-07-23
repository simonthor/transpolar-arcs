import numpy as np
from scipy import stats
from typing import Tuple


def compare_dists(sample: np.ndarray, comparison: np.ndarray, bins: np.ndarray, *args, **kwargs) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """Calculate chi-square test p-value for sample and comparison.

    This function uses scipy.stats.chisquare to calculate the p value.
    However, if necessary, this function will merge bins with fewer than 5 counts in `comparison` with neighboring bins to yield a statistically significant result.

    Parameters
    ----------
    sample : numpy.ndarray
        The measured counts. Must have `size(sample) < 1`.
    comparison : numpy.ndarray
        The expected counts. Must have `size(comparison) = size(sample)`.
    bins : numpy.ndarray
        The bin edges of the counts measured and the expected counts. Must have `size(bins) = size(sample)+1.
    *args : any, optional
        Other input arguments for scipy.stats.chisquare.
    **kwargs : any, optional
        Other input keyword arguments for scipy.stats.chisquare.

    Returns
    ----------
    p_value : float
        p value measuring how well `sample` and `comparison` match. 1 means a perfect match and 0 means not similar at all.
    merged_sample : numpy.ndarray
        The `sample` input array but bins with fewer than 5 counts have been merged with neighboring bins.
    merged_comparison :  numpy.ndarray
        The `comparison` input array but bins with fewer than 5 counts have been merged with neighboring bins.
    merged_bins : numpy.ndarray
        The `bins` input array but bins with fewer than 5 counts have been merged with neighboring bins.

    See also
    ----------
    `scipy.stats.chisquare <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chisquare.html>`_
    """

    if (total := comparison.sum()) < 5:
        raise ValueError(f'Sum of comparison must be at least 5 but comparison only contained a total of {total}.')
    if (comparison.size != sample.size) or (bins.size != comparison.size + 1):
        raise ValueError('comparison and sample must be equal size with bins being sample.size + 1. '
                         f'Instead, sizes {sample.size=}, {comparison.size=}, {bins.size=} were given.')

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
