# Standard library
import datetime as dt
from typing import Union, List, Dict
from dataclasses import dataclass, field
# Packages
import numpy as np
# Self-written modules
import test_OMNI
from data_structures.tpa import TPA


@dataclass
class TPADataset:
    """Dataclass for containing the data of transpolar arcs."""
    name: str
    average_calctime: float
    time_shift: float
    start_time: dt.datetime
    end_time: dt.datetime
    total: dict = field(default_factory=lambda: {"BxGSM": [], "ByGSM": [], "BzGSM": [], "BmagGSM": [], "vel": [], "vB^2": []})
    tpa_values: dict = field(init=False)

    def __post_init__(self):
        self.tpa_values = self.total.copy()

    def get_dataset_parameters(self, OMNI_dir: str, paras: Union[List[str], str]):
        """Loads the value of parameters for the entire period of the dataset."""
        if isinstance(paras, str):
            paras = [paras]

        OMNI_data_loader = test_OMNI.LoadOMNI(self.start_time, self.end_time, data_dir=OMNI_dir)
        OMNI_data_loader.load_OMNI_data(paras_in=paras)

        if "BxGSM" in paras and "ByGSM" in paras and "BzGSM" in paras:
            val = np.sqrt(OMNI_data_loader.paras["BxGSM"] ** 2 + OMNI_data_loader.paras["BzGSM"] ** 2 + OMNI_data_loader.paras["ByGSM"] ** 2)
            self.total["BmagGSM"] = val.reshape(val.size)

        for key, val in OMNI_data_loader.paras.items():
            if key in paras:
                val = val.flatten()
                self.total[key] = val

    def append(self, tpa: TPA):
        for variable in self.total.keys():
            if hasattr(tpa, variable):
                self.tpa_values[variable].append(getattr(tpa, variable))
