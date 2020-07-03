# Standard library
import datetime as dt
from typing import Union, List
from dataclasses import dataclass, field
# Packages
import numpy as np
# Self-written modules
from ..data_extraction.test_OMNI import LoadOMNI
from ..data_structures.tpa import TPA


@dataclass
class TPADataset:
    """Dataclass for containing the data of transpolar arcs."""
    name: str
    average_calctime: float
    time_shift: float
    start_time: dt.datetime
    end_time: dt.datetime
    # TODO: change type of total, tpa_values, tpa_properties to pd.DataFrame instead?
    total: dict = field(default_factory=lambda: dict((paraname, []) for paraname in [*LoadOMNI.full_para_list, 'dipole']))
    tpa_values: dict = field(init=False)
    tpa_properties: dict = field(init=False, default_factory=lambda: {})

    def __post_init__(self):
        self.tpa_values = self.total.copy()

    def get_dataset_parameters(self, OMNI_dir: str, parameters: Union[List[str], str]):
        """Loads the value of parameters for the entire period of the dataset.
        Inputs:
        OMNI_dir (str): directory where OMNI data is stored.
        paras (List[str], str): parameters that will be extracted. A full list of available parameters can be seen in
                                LoadOMNI.full_para_list. """
        if isinstance(parameters, str):
            parameters = [parameters]

        parameters = parameters.copy()

        if 'dipole' in parameters:
            # TODO: add support for dipole of dataset
            # self.get_dipole_data(self.avgcalctime)
            # self.total['dipole'] = self.dipole
            parameters.remove('dipole')

        OMNI_data_loader = LoadOMNI(self.start_time, self.end_time, data_dir=OMNI_dir)
        OMNI_data_loader.load_OMNI_data(paras_in=parameters)

        for key, val in OMNI_data_loader.paras.items():
            if key in parameters:
                val = val.flatten()
                self.total[key] = val

    def append(self, tpa: TPA):
        """Add a transpolar arc (TPA) to the dataset.
         Takes the TPA's attributes and appends its values to self.tpa_values and self.tpa_properties.
        Inputs:
        tpa (data_structures.tpa_dataset.tpa.TPA): transpolar arc that will be added to the dataset.
        """
        for value in self.total.keys():
            if hasattr(tpa, value):
                self.tpa_values[value] = np.append(self.tpa_values[value], getattr(tpa, value))

        for prop in tpa.properties:
            if prop in self.tpa_properties.keys():
                self.tpa_properties[prop] = np.append(self.tpa_properties[prop], getattr(tpa, prop))
            else:
                self.tpa_properties[prop] = np.array([getattr(tpa, prop)])
