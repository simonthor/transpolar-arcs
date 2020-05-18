import datetime
from dataclasses import dataclass
from geopack import geopack
import numpy as np
import test_OMNI


# TODO: Change to setattr everywhere instead
class TPA:
    """TODO: Include docstring"""
    def __init__(self, dataset, date, hemisphere=None, dadu=None, moving=None, dipole=None, **kwargs):
        self.dataset = dataset

        if isinstance(date, datetime.datetime):
            self.date = date
        else:
            raise TypeError("Format of TPA.date is incorrect. Must be datetime.datetime")

        if isinstance(hemisphere, str):
            self.hem = hemisphere
        else:
            self.hem = None

        if isinstance(dadu, str):
            self.dadu = dadu
        else:
            self.dadu = "unknown"

        if moving is not None:
            if isinstance(moving, str):
                self.moving = moving
            else:
                raise TypeError("Format of TPA.moving is incorrect. Must be str")
        else:
            self.moving = None

        self.IMF = {"BxGSM": np.nan, "ByGSM": np.nan, "BzGSM": np.nan, "BmagGSM": np.nan}

        if dipole is True:
            dipoles = []
            for i in range(self.avgcalctime):
                t = (date - datetime.datetime(1970, 1, 1) - datetime.timedelta(
                    minutes=i + self.timeshift)).total_seconds()
                dipoles.append(180 / np.pi * geopack.recalc(t))

            self.dipole = sum(dipoles) / len(dipoles)
        elif dipole is not None:
            self.dipole = dipole
        else:
            self.dipole = np.nan

        for key, val in kwargs.items():
            if key in ["BxGSM","ByGSM", "BzGSM", "BmagGSM"]:
                if isinstance(val, (int, float)):
                    self.IMF[key] = val
                elif isinstance(val, list):
                    val = np.array(val)
                    self.IMF[key] = val[~np.isnan(val)].mean()
                elif isinstance(val, np.ndarray):
                    self.IMF[key] = val[~np.isnan(val)].mean()
                else:
                    raise TypeError("Format of {} is incorrect. Must be int, float, list, or numpy array".format(key))
            else:
                if key == "vel":
                    if isinstance(val, (int, float)):
                        self.vel = val
                    elif isinstance(val, (list, np.ndarray)):
                        self.vel = np.nanmean(np.asarray(val))
                    else:
                        self.vel = np.nan
                else:
                    setattr(self, key, val)
                    print("{} is not a predefined variable in this version of the program".format(key))

    def __repr__(self):
        return "Transpolar Arc"

    def __str__(self):
        return "TPA identified by: {}\n" \
               "hemisphere: {}\n" \
               "formation date: {}\n" \
               "dipole tilt: {}\n" \
               "moving: {}\n" \
               "dawn/dusk: {}\n" \
               "Bx: {}\tBy: {}\tBz: {}\n".format(self.name, self.hem, self.date, self.dipole, self.moving, self.dadu,
                                                 self.BxGSM, self.ByGSM, self.BzGSM)

    def avg(self, OMNI_dir, paras):

        starttime = self.date - datetime.timedelta(minutes=self.timeshift + self.avgcalctime)
        endtime = self.date - datetime.timedelta(minutes=self.timeshift)

        loadObj = test_OMNI.LoadOMNI(starttime, endtime, data_dir=OMNI_dir)
        loadObj.laod_OMNI_data(paras_in=paras)
        if "BxGSM" in paras and "ByGSM" in paras and "BzGSM" in paras:
            self.IMF["BmagGSM"] = np.nanmean(np.sqrt(loadObj.paras["BxGSM"] ** 2 + loadObj.paras["BzGSM"] ** 2 + loadObj.paras["ByGSM"] ** 2))

        for key, val in loadObj.paras.items():
            if key in paras:
                clean_vals = val[~np.isnan(val)]
                if len(clean_vals) != 0:
                    setattr(self, key, clean_vals.mean())
                else:
                    setattr(self, key, np.nan)

    def get_avgcalctime(self):
        return self.dataset.avgcalctime
    def set_avgcalctime(self, val):
        self.dataset.avgcalctime = val
    avgcalctime = property(get_avgcalctime, set_avgcalctime)

    def get_timeshift(self):
        return self.dataset.timeshift
    def set_timeshift(self, val):
        self.dataset.timeshift = val
    timeshift = property(get_timeshift, set_avgcalctime)

    def get_name(self):
        return self.dataset.name
    def set_name(self, val):
        self.dataset.name = val
    name = property(get_name, set_name)

    def get_Bx(self):
        return self.IMF["BxGSM"]
    def set_Bx(self, val):
        self.IMF["BxGSM"] = val
    BxGSM = property(get_Bx, set_Bx)

    def get_By(self):
        return self.IMF["ByGSM"]
    def set_By(self, val):
        self.IMF["ByGSM"] = val
    ByGSM = property(get_By, set_By)

    def get_Bz(self):
        return self.IMF["BzGSM"]
    def set_Bz(self, val):
        self.IMF["BzGSM"] = val
    BzGSM = property(get_Bz, set_Bz)

    def get_Bmag(self):
            return self.IMF["BmagGSM"]
    def set_Bmag(self, val):
        self.IMF["BmagGSM"] = val
    BmagGSM = property(get_Bmag, set_Bmag)
