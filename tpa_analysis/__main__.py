import tpa_analysis.statistics as tst
import numpy as np

if __name__ == '__main__':
    sample = np.array([0, 1, 0, 1, 2, 1, 0, 0, 1])
    print(tst.compare_dists(sample, sample, np.arange(-1, sample.size)))