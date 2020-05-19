import datetime
import scipy.io
import numpy


class LoadOMNI:
    def __init__(self, dt_start, dt_stop, data_dir=None):

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

    def load_OMNI_data(self, paras_in=None):
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
        paras = dict((paraname, numpy.empty(0)) for paraname in paras_in)
        paras['datetime'] = numpy.empty(0, dtype=numpy.datetime64)
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

            dts = numpy.datetime64(dt0) + edesh[ind_t1:ind_t2].astype('timedelta64[s]')

            paras['datetime'] = numpy.append(paras['datetime'], dts)
            data = matfile['comp']
            for paraname in paras_in:
                if paraname == 'BxGSM':
                    newdata = data[ind_t1:ind_t2, para_dict['BxGSE']]
                else:
                    newdata = data[ind_t1:ind_t2, para_dict[paraname]]

                paras[paraname] = numpy.append(paras[paraname], newdata)
        self.paras = paras


if __name__ == "__main__":

    data_dir = '/home/lcai/01_work/00_data/OMNI/OMNI_1min_Lv1/'
    dt_start = datetime.datetime(2013, 11, 3, 0, 0, 0)
    dt_stop = datetime.datetime(2013, 11, 5, 0, 0, 0)
    paras_in = ['BxGSM', 'ByGSM', 'BzGSM', 'vel']

    loadObj = LoadOMNI(dt_start, dt_stop, data_dir=data_dir)
    # loadObj.laod_OMNI_data() # load all the parameters
    loadObj.load_OMNI_data(paras_in=paras_in)
    BxGSM = loadObj.paras['BxGSM']
    datetimelist = loadObj.paras['datetime']