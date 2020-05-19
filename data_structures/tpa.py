import datetime as dt
from dataclasses import dataclass, field
from typing import Union, List, Sequence
from geopack import geopack
import numpy as np
import test_OMNI


@dataclass
class TPA:
    """Dataclass for storing information about a single transpolar arc."""
    date: dt.datetime
    hemisphere: str = ''
    dadu: str = ''
    moving: str = ''
    conjugate: bool = True
    dipole: float = field(init=False, default=np.nan)

    def __post_init__(self):
        self.dipole = np.nan

    def get_parameters(self, OMNI_dir: str, parameters: List[str], timeshift: int, avgcalctime: int):
        """Calculates TPA parameters (e.g. 'BxGSM' and adds them to the TPA object
        returns: calculated parameters
        """
        retrieved_parameters = {}
        if isinstance(parameters, str):
            parameters = [parameters]

        if 'dipole' in parameters:
            self.get_dipole_data(avgcalctime, timeshift)
            retrieved_parameters['dipole'] = self.dipole
            parameters.remove('dipole')

        start_time = self.date - dt.timedelta(minutes=timeshift + avgcalctime)
        end_time = self.date - dt.timedelta(minutes=timeshift)
        OMNI_data_loader = test_OMNI.LoadOMNI(start_time, end_time, data_dir=OMNI_dir)
        OMNI_data_loader.load_OMNI_data(paras_in=parameters)

        if "BxGSM" in parameters and "ByGSM" in parameters and "BzGSM" in parameters:
            self.BmagGSM = np.nanmean(np.sqrt(OMNI_data_loader.paras["BxGSM"] ** 2 + OMNI_data_loader.paras["BzGSM"] ** 2 + OMNI_data_loader.paras["ByGSM"] ** 2))

        for key, val in OMNI_data_loader.paras.items():
            if key in parameters:
                clean_vals = val[~np.isnan(val)]
                if len(clean_vals) != 0:
                    setattr(self, key, clean_vals.mean())
                else:
                    setattr(self, key, np.nan)

    def get_dipole_data(self, avgcalctime, timeshift):
        dipoles = []
        for i in range(avgcalctime):
            t = (self.date - dt.datetime(1970, 1, 1) - dt.timedelta(minutes=i + timeshift)).total_seconds()
            dipoles.append(180 / np.pi * geopack.recalc(t))

        self.dipole = np.nanmean(dipoles)

    # def __init__(self, dataset, date, hemisphere=None, dadu=None, moving=None, dipole=None, **kwargs):
    #     self.dataset = dataset
    #
    #     if isinstance(date, datetime.datetime):
    #         self.date = date
    #     else:
    #         raise TypeError("Format of TPA.date is incorrect. Must be datetime.datetime")
    #
    #     if isinstance(hemisphere, str):
    #         self.hem = hemisphere
    #     else:
    #         self.hem = None
    #
    #     if isinstance(dadu, str):
    #         self.dadu = dadu
    #     else:
    #         self.dadu = "unknown"
    #
    #     if moving is not None:
    #         if isinstance(moving, str):
    #             self.moving = moving
    #         else:
    #             raise TypeError("Format of TPA.moving is incorrect. Must be str")
    #     else:
    #         self.moving = None
    #
    #     self.IMF = {"BxGSM": np.nan, "ByGSM": np.nan, "BzGSM": np.nan, "BmagGSM": np.nan}
    #
    #     if dipole is True:
    #         dipoles = []
    #         for i in range(self.avgcalctime):
    #             t = (date - datetime.datetime(1970, 1, 1) - datetime.timedelta(
    #                 minutes=i + self.timeshift)).total_seconds()
    #             dipoles.append(180 / np.pi * geopack.recalc(t))
    #
    #         self.dipole = sum(dipoles) / len(dipoles)
    #     elif dipole is not None:
    #         self.dipole = dipole
    #     else:
    #         self.dipole = np.nan
    #
    #     for key, val in kwargs.items():
    #         if key in ["BxGSM","ByGSM", "BzGSM", "BmagGSM"]:
    #             if isinstance(val, (int, float)):
    #                 self.IMF[key] = val
    #             elif isinstance(val, list):
    #                 val = np.array(val)
    #                 self.IMF[key] = val[~np.isnan(val)].mean()
    #             elif isinstance(val, np.ndarray):
    #                 self.IMF[key] = val[~np.isnan(val)].mean()
    #             else:
    #                 raise TypeError("Format of {} is incorrect. Must be int, float, list, or numpy array".format(key))
    #         else:
    #             if key == "vel":
    #                 if isinstance(val, (int, float)):
    #                     self.vel = val
    #                 elif isinstance(val, (list, np.ndarray)):
    #                     self.vel = np.nanmean(np.asarray(val))
    #                 else:
    #                     self.vel = np.nan
    #             else:
    #                 setattr(self, key, val)
    #                 print("{} is not a predefined variable in this version of the program".format(key))

    # def __str__(self):
    #     return "TPA identified by: {}\n" \
    #            "hemisphere: {}\n" \
    #            "formation date: {}\n" \
    #            "dipole tilt: {}\n" \
    #            "moving: {}\n" \
    #            "dawn/dusk: {}\n" \
    #            "Bx: {}\tBy: {}\tBz: {}\n".format(self.name, self.hem, self.date, self.dipole, self.moving, self.dadu,
    #                                              self.BxGSM, self.ByGSM, self.BzGSM)

    # def get_avgcalctime(self):
    #     return self.dataset.avgcalctime
    # def set_avgcalctime(self, val):
    #     self.dataset.avgcalctime = val
    # avgcalctime = property(get_avgcalctime, set_avgcalctime)
    # def get_timeshift(self):
    #     return self.dataset.timeshift
    # def set_timeshift(self, val):
    #     self.dataset.timeshift = val
    # timeshift = property(get_timeshift, set_avgcalctime)
    #
    # def get_name(self):
    #     return self.dataset.name
    # def set_name(self, val):
    #     self.dataset.name = val
    # name = property(get_name, set_name)
    #
    # def get_Bx(self):
    #     return self.IMF["BxGSM"]
    # def set_Bx(self, val):
    #     self.IMF["BxGSM"] = val
    # BxGSM = property(get_Bx, set_Bx)
    #
    # def get_By(self):
    #     return self.IMF["ByGSM"]
    # def set_By(self, val):
    #     self.IMF["ByGSM"] = val
    # ByGSM = property(get_By, set_By)
    #
    # def get_Bz(self):
    #     return self.IMF["BzGSM"]
    # def set_Bz(self, val):
    #     self.IMF["BzGSM"] = val
    # BzGSM = property(get_Bz, set_Bz)
    #
    # def get_Bmag(self):
    #         return self.IMF["BmagGSM"]
    # def set_Bmag(self, val):
    #     self.IMF["BmagGSM"] = val
    # BmagGSM = property(get_Bmag, set_Bmag)
