# Builtins
import warnings
import datetime as dt
# Packages
import pandas as pd
# Self-written modules
from data_structures.tpa import TPA


# TODO: move to data_structures
class DataExtract:
    def __init__(self, tpa_dir):
        self.tpa_dir = tpa_dir
        self.name_to_function = {'Fear & Milan (2012)': self.fear_dataclean,
                                 'Kullen et al. (2002)': self.kullen_dataclean,
                                 'Cumnock et al. (2009)': self.cumnock0_dataclean,
                                 'Reidy et al. (2018)': self.reidy_dataclean,
                                 'Cumnock et al. (2005)': self.cumnock1_dataclean}

    def get_tpas(self, dataset_name, *args, **kwargs):
        retriever_function = self.name_to_function[dataset_name]
        return retriever_function(*args, **kwargs)

    def kullen_dataclean(self, filename="datafile_tpa_location.dat"):
        """Extracting Kullen's data
         Input file type: .dat
         """
        filename = self.tpa_dir + filename
        with open(filename) as dat:
            kullen = dat.readlines()

        for line in kullen:
            tpa_parameters = line.split()
            if line[0] not in "\n;" and tpa_parameters[1][2] == "1":
                motion = DataExtract.calc_motion(float(tpa_parameters[3]), float(tpa_parameters[6]))
                # elif cl[1][2] == "2":
                #    motion = "unknown"
                # else:
                #    continue
                dadu = DataExtract.calc_dadu(float(tpa_parameters[3]))
                if tpa_parameters[1][:2] != "bd":
                    yield TPA(dt.datetime.strptime(tpa_parameters[0] + line[11:15], "%y%m%d%H%M"), hemisphere="n",
                              moving=motion, dadu=dadu)
                elif tpa_parameters[1][:4] == "bd1h":
                    yield TPA(dt.datetime.strptime(tpa_parameters[0] + line[11:15], "%y%m%d%H%M"), hemisphere="n",
                              moving=motion, dadu=dadu)

    def cumnock0_dataclean(self, filename="Single_Multiple_Arcs_IMF_dipole_list_2015_AK_prel_dadu.xls",
                           usecols="A, C, D, N", sheet_name="Sheet1"):
        """Extracting Cumnock's first data (excel)"""

        filename = self.tpa_dir + filename

        judy = pd.read_excel(filename, sheet_name=sheet_name, index_col=None, usecols=usecols)
        for index, row in judy.iterrows():
            try:
                if int(row[0]) > 1:
                    num = True
                else:
                    num = False
            except Exception as e:
                print(f'error: {e}')
                num = False
                if type(row[0]) == str and "Single" in row[0]:
                    break
            if num:
                # Warning: Change the last timedelta object to vary the shift backwards in time
                date = dt.datetime.strptime(str(row[0]) + row[2][:row[2].find("-")],
                                            "%y%j%H%M%S") - dt.timedelta(minutes=120)
                if "dadu" in filename:
                    dadu = row[3]
                else:
                    dadu = None
                yield TPA(date, row[1], moving="yes", dadu=dadu)

    def cumnock1_dataclean(self, filename="listoftimes.xls", sheet_name="Sheet1", usecols="A, G, M"):
        """Extracting Cumnock's second data (excel)"""
        filename = self.tpa_dir + filename

        judy = pd.read_excel(filename, sheet_name=sheet_name, index_col=None, usecols=usecols, skiprows=[1, 2])

        for index, row in judy.iterrows():
            if "Do not" in str(row[0]):
                break
            elif isinstance(row[0], int) or "00" in str(row[0]):
                if len(str(row[0])) >= 5:
                    yield TPA(dt.datetime.strptime(str(row[0]) + str(row[1]), "%y%j%X"), "n", moving="yes", dadu=row[2])
                else:
                    date = "0" * (5 - len(str(row[0]))) + str(row[0]) + str(row[1])
                    if len(usecols.split()) > 2:
                        dadu = row[2]
                    else:
                        dadu = None
                    yield TPA(dt.datetime.strptime(date, "%y%j%X"), "n", moving="yes", dadu=dadu)

    def cai_dataclean(self, filename=""):
        """Function that will later be used for extracting Cai's dataset of TPAs from DMSP.
        Includes conjugate TPAs.
        TODO: add this function when I have received the data"""

    @staticmethod
    def fear_fileclean(filename="Fear_TPA_data_frompaper.txt"):
        """Cleaning Fear's data to readable txt (txt)"""
        clean = ""
        with open(filename, "r") as fear:
            for line in fear:
                if not line.split() == []:
                    if line[0] == " ":
                        space = 0
                        for ch in line:
                            if ch == " ":
                                space += 1
                            else:
                                break
                        clean += line[space:]
                    else:
                        clean += line
        with open('fear_TPA_data.txt', 'w') as fear:
            fear.write(clean)

    def fear_dataclean(self, filename='fear_TPA_data_frompaper.txt'):
        """Extracting Fear's data (txt)"""
        filename = self.tpa_dir + filename

        if 'frompaper' in filename:
            with open(filename) as fear:
                for line in fear:
                    try:
                        int(line.split()[0])
                        tpa = True
                    except ValueError:
                        tpa = False
                    if tpa:
                        tpa_parameters = line.split()
                        if tpa_parameters[10] == "N":
                            motion = "no"
                        elif tpa_parameters[10] == "Y":
                            motion = "yes"
                        else:
                            motion = tpa_parameters[10]
                            warnings.warn(f'WARNING: input for motion is neither Yes nor No but instead "{motion}"')
                        dadu = DataExtract.calc_dadu(float(tpa_parameters[7]))

                        yield TPA(dt.datetime.strptime(f'{tpa_parameters[1]}{tpa_parameters[2]}:00', '%d-%b-%Y%X'),
                                  hemisphere=tpa_parameters[9].lower(), moving=motion, dadu=dadu)
        else:
            with open(filename) as fear:
                for line in fear:
                    try:
                        int(line.split()[0])
                        tpa = True
                    except ValueError:
                        tpa = False
                    if tpa:
                        tpa_parameters = line.split()
                        yield TPA(dt.datetime.strptime(tpa_parameters[1] + tpa_parameters[2][:8], '%d-%b-%Y%X'),
                                  tpa_parameters[3])

    def reidy_dataclean(self, filename='reidy_TPA_data.txt'):
        filename = self.tpa_dir + filename
        with open(filename) as reidy:
            for line in reidy:
                if line[0] != '#':
                    parameters = line.split()
                    if parameters[9] == 'NS':
                        yield TPA(dt.datetime.strptime(parameters[1] + parameters[2] + parameters[3] + parameters[4],
                                                       '%d%b%Y%H:%M'), hemisphere='n',
                                  conjugate=True)
                        yield TPA(dt.datetime.strptime(parameters[1] + parameters[2] + parameters[3] + parameters[4],
                                                       '%d%b%Y%H:%M'), hemisphere='s',
                                  conjugate=True)
                    else:
                        yield TPA(dt.datetime.strptime(parameters[1] + parameters[2] + parameters[3] + parameters[4],
                                                       '%d%b%Y%H:%M'),
                                  hemisphere=parameters[9].lower(), conjugate=False)

    @staticmethod
    def calc_motion(mlt1, mlt2):
        d = abs(mlt2 - mlt1)
        if d > 12:
            d = 24 - d
        if d > 2:
            motion = "yes"
        else:
            motion = "no"

        return motion

    @staticmethod
    def calc_dadu(mlt):
        if 0 < mlt <= 12:
            dadu = "dawn"
        else:
            dadu = "dusk"
        # else:
        #    print("Unknown value of dadu (dawn or dusk): {}".format(mlt1))
        #    dadu = None

        return dadu


# Used for testing purposes
if __name__ == "__main__":
    from data_structures.tpa_dataset import TPADataset

    test_dataset = TPADataset("reidy", 20, 100, dt.date(2000, 10, 20), dt.date(2000, 10, 30))
    data_extractor = DataExtract("data/")
    test_dataset.append(data_extractor.reidy_dataclean())
    print(len(test_dataset.tpas))
    for tpa in test_dataset.tpas:
        print(tpa)
