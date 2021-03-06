import datetime as dt
from dataclasses import dataclass, field
from typing import List

from geopack import geopack
import numpy as np

from ..data_extraction import test_OMNI


@dataclass
class TPA:
    """Dataclass for storing information about a single transpolar arc."""
    date: dt.datetime
    hemisphere: str = ''
    dadu: str = ''
    moving: str = ''
    conjugate: str = ''
    multiple: bool = False
    dipole: float = field(init=False, default=np.nan)
    properties: dict = field(init=False)

    def __post_init__(self):
        # TODO: automatically add fields here by e.g. using dir()?
        self.properties = {'date': self.date, 'hemisphere': self.hemisphere, 'dadu': self.dadu, 'moving': self.moving,
                           'conjugate': self.conjugate, 'multiple': self.multiple}

    def get_parameters(self, OMNI_dir: str, parameters: List[str], timeshift: int, avgcalctime: int):
        """Calculates TPA parameters (e.g. 'BxGSM' and adds them to the TPA object
        returns: calculated parameters
        """

        retrieved_parameters = {}
        if isinstance(parameters, str):
            parameters = [parameters]

        parameters = parameters.copy()

        if 'dipole' in parameters:
            self.get_dipole_data(avgcalctime)
            retrieved_parameters['dipole'] = self.dipole
            parameters.remove('dipole')

        start_time = self.date - dt.timedelta(minutes=timeshift + avgcalctime)
        end_time = self.date - dt.timedelta(minutes=timeshift)
        OMNI_data_loader = test_OMNI.LoadOMNI(start_time, end_time, data_dir=OMNI_dir)
        OMNI_data_loader.load_OMNI_data(paras_in=parameters)

        for key, val in OMNI_data_loader.paras.items():
            if key in parameters:
                clean_vals = val[~np.isnan(val)]
                if len(clean_vals) != 0:
                    setattr(self, key, clean_vals.mean())
                else:
                    setattr(self, key, np.nan)

    def get_dipole_data(self, avgcalctime: int):
        """Retrieves information about the dipole tile of the Earth during the transpolar arc.
        Inputs:
        avgcalctime (int): calculate the average dipole tilt over these number of minutes.
        """
        def get_dipole_tilt(minute):
            t = (self.date - dt.datetime(1970, 1, 1) - dt.timedelta(minutes=int(minute))).total_seconds()
            return 180 / np.pi * geopack.recalc(t)

        dipoles = np.vectorize(get_dipole_tilt)(np.arange(1, avgcalctime+1, dtype=int))
        self.dipole = np.nanmean(dipoles)

