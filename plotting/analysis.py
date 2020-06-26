import numpy as np
from scipy import stats


def compare_dists(sample: np.ndarray, comparison: np.ndarray, bins: np.ndarray, dof: int = 0) -> float:
    """Calculate chi-square test p-value for sample and comparison.
    Will bin samples with fewer values than smaller than 5"""
    if (comparison >= 5).all():
        _, p_value = stats.chisquare(sample, comparison, dof)
        return p_value

    merged_comparison, merged_sample, merged_bins = np.copy(comparison), np.copy(sample), np.copy(bins)
    for i, (sample_val, comparison_val, bin) in enumerate(zip(merged_sample[:-1], merged_comparison[:-1], merged_bins[:-1])):
        if comparison_val < 5:
            # Merge categories to make them at least 5
            merged_sample[i+1] += sample_val
            merged_comparison[i+1] += comparison_val
            merged_sample[i] = -1
            merged_comparison[i] = -1
            # TODO: do something with merged_bins too
    # Remove all invalid values and bins (in this case with value -1)
    merged_sample = merged_sample[merged_sample != -1]
    merged_comparison = merged_comparison[merged_comparison != -1]

    for i, (sample_val, comparison_val, bin) in reversed(list(enumerate(zip(merged_sample[1:], merged_comparison[1:], merged_bins[1:])))):
        if comparison_val < 5:
            # Merge categories to make them at least 5
            merged_sample[i-1] += sample_val
            merged_comparison[i-1] += comparison_val
            merged_sample[i] = -1
            merged_comparison[i] = -1
            # TODO: do something with merged_bins too
    merged_sample = merged_sample[merged_sample != -1]
    merged_comparison = merged_comparison[merged_comparison != -1]

    # TODO: use other dof value?
    _, p_value = stats.chisquare(merged_sample, merged_comparison, dof)
    return p_value
