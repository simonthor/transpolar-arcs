import datetime
import scipy.io
import numpy
import os
import pickle
import tkinter as tk
from tkinter import filedialog
from geopack import geopack as dip
import importlib
test_OMNI = importlib.import_module('test_OMNI_2')


if __name__ == "__main__":

    # load objective that was saved before
    # loadObj = test_OMNI.load_objective()
    # loadObj = test_OMNI.load_objective(filepath=filepath, filename=filename)  # filepath is the file directory,
    # and filename is the name of the file you want to load.

    data_dir = '/home/lcai/01_work/00_data/OMNI/OMNI_1min_Lv1/'
    dt_start = datetime.datetime(1999, 1, 1, 0, 0, 0)
    dt_stop = datetime.datetime(2000, 1, 1, 0, 0, 0)
    paras_in = ['BxGSM', 'ByGSM', 'BzGSM', 'vel', 'vxGSE', 'vyGSE', 'vzGSE']

    loadObj = test_OMNI.LoadOMNI(dt_start, dt_stop, data_dir=data_dir)
    # loadObj.laod_OMNI_data() # load all the parameters
    loadObj.laod_OMNI_data(paras_in=paras_in)

    # add dipole tilt angle to loadObj
    loadObj.load_addition_dipole_tilt(solarwind='on', both='on')
    # save loadObj to file (*.pkl)
    loadObj.save_objective()

    BxGSM = loadObj.paras['BxGSM']
    datetimelist = loadObj.paras['datetime']


class LoadOMNI(object):
    def __init__(self, dt_start, dt_stop, data_dir = None):

        diff_month = (dt_stop.year - dt_start.year) * 12 + dt_stop.month - dt_start.month

        data_file_list = []
        dt_range_list = []
        year = dt_start.year
        month = dt_start.month
        for i in range(diff_month+1):

            dt = datetime.datetime(year, month, 1)
            filename = 'OMNI_1min_' + dt.strftime('%Y%m') + '_Lv1.mat'
            data_file_list.append(filename)
            if i == 0 and diff_month > 0:
                dt_range_list.append([(dt_start-dt).total_seconds(), -1])
            elif i == diff_month and diff_month > 0:
                dt_range_list.append([0, (dt_stop - dt).total_seconds()])
            elif diff_month == 0:
                dt_range_list.append([(dt_start-dt).total_seconds(), (dt_stop-dt).total_seconds()])
            else:
                dt_range_list.append([0, -1])
            month = month + 1
            if month > 12:
                month = 1
                year = year + 1

        self.data_files = data_file_list
        self.dt_ranges = dt_range_list
        self.data_dir = data_dir

    def laod_OMNI_data(self, paras_in=None):
        full_para_list = ['ID MF', 'ID PL', 'n  MF', 'n  PL', 'Inter',
                          'Dt', 'RMSDt', 'RMSMi', 'DBOT ', '<B>',
                          'BxGSE', 'ByGSE', 'BzGSE', 'ByGSM', 'BzGSM',
                          'RMSBs', 'RMSBv', 'vel', 'vxGSE', 'vyGSE',
                          'vzGSE', 'n', 'Temp', 'Pdyn', 'Ey',
                          'beta', 'MA', 'XGSE', 'YGSE', 'ZGSE',
                          'XBow', 'YBow', 'ZBow', 'AE', 'AL',
                          'AU', 'SYM/D', 'SYM/H', 'ASY/D', 'ASY/H',
                          'PC-N', 'Mms', 'clock', 'New07', 'Bt',
                          'E_sw '
                          ]
        para_dict = dict((paraname, ind) for ind, paraname in enumerate(full_para_list))
        if paras_in is None:
            paras_in = full_para_list
        paras = dict((paraname, numpy.empty((0, 1))) for paraname in paras_in)
        paras['datetime'] = numpy.empty((0, 1))
        for ind_f, filename in enumerate(self.data_files):
            matfile = scipy.io.loadmat(self.data_dir + filename)
            edesh = matfile['edesh']
            dtdelta_start = self.dt_ranges[ind_f][0]
            dtdelta_stop = self.dt_ranges[ind_f][1]
            dt0 = datetime.datetime.strptime(matfile['sdate'][0], '%Y-%m-%d')
            if dtdelta_start == 0:
                ind_t1 = 0
            else:
                ind_t1 = numpy.where(edesh >= dtdelta_start)[0][0]
            if dtdelta_stop == -1:
                ind_t2 = edesh.shape[0]
            else:
                ind_t2 = numpy.where(edesh <= dtdelta_stop)[0][-1]
            ind_t = list(range(ind_t1, ind_t2))

            dts = [dt0 + datetime.timedelta(seconds=second[0])
                   for second in edesh[ind_t].tolist()]

            dts = numpy.array(dts).reshape((len(ind_t), 1))
            paras['datetime'] = numpy.vstack((paras['datetime'], dts))
            data = matfile['comp']
            for paraname in paras_in:
                if paraname == 'BxGSM':
                    newdata = data[ind_t, para_dict['BxGSE']].reshape((len(ind_t), 1))
                else:
                    newdata = data[ind_t, para_dict[paraname]].reshape((len(ind_t), 1))

                paras[paraname] = numpy.vstack((paras[paraname], newdata))
        self.paras = paras

    def load_addition_dipole_tilt(self, solarwind='on', both='on'):
        kwargs1 = {
            'dts':      self.paras['datetime'],
            'vxGSE':    None,
            'vyGSE':    None,
            'vzGSE':    None
        }
        kwargs2 = {
            'dts':          self.paras['datetime'],
            'vxGSE':        self.paras['vxGSE'],
            'vyGSE':        self.paras['vyGSE'],
            'vzGSE':        self.paras['vzGSE'],
            'both':         both
        }
        if solarwind is 'on':
            self.paras['dipoletilt'] = dip.cal_dipole_tilt_angle(**kwargs2)
        else:
            self.paras['dipoletilt'] = dip.cal_dipole_tilt_angle(**kwargs1)

    def save_objective(self, filepath=None, filename=None):
        if filepath is None:
            filepath = os.getcwd()
        if filename is None:
            filename = 'OMNI_1min_'     \
                       + self.paras['datetime'][0, 0].strftime('%Y%m%d_%H%M') + '_' \
                       + self.paras['datetime'][-1, 0].strftime('%Y%m%d_%H%M') \
                       + '.pkl'
        fullpath = os.path.join(filepath, filename)
        with open(fullpath, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)


def load_objective(filepath=None, filename=None):
    if filepath is None:
        filepath = os.getcwd()

    if filename is None:
        root = tk.Tk()
        root.withdraw()

        filename = filedialog.askopenfilename(initialdir=filename, title="Select objective file:")
    else:
        filename = os.path.join(filepath, filename)
    with open(filename, 'rb') as input:
        return pickle.load(input)






