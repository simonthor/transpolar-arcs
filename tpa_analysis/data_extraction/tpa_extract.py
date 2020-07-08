# Standard library
import warnings
import datetime as dt
import re
# Packages
import pandas as pd
import numpy as np
# Self-written modules
from ..data_structures.tpa import TPA


# TODO: create factory class?
class DataExtract:
    """Extracts transpolar arc (TPA) data from different datasets."""

    def __init__(self, tpa_dir):
        self.tpa_dir = tpa_dir
        self.name_to_function = {'Fear & Milan (2012)': self.fear_dataclean,
                                 'Kullen et al. (2002)': self.kullen_dataclean,
                                 'Cumnock et al. (2009)': self.cumnock2009_dataclean,
                                 'Reidy et al. (2018)': self.reidy_dataclean,
                                 'Cumnock (2005)': self.cumnock2005_dataclean,
                                 'New dataset': self.simon_dataclean}

    def get_tpas(self, dataset_name: str, *args, **kwargs):
        """Small wrapper for calling all TPA extraction functions based on dataset_name.
        Input: dataset_name (str): name of the authors of the paper where the dataset was presented.
        All other parameters passed will be forwarded to the retriever function.
        """
        try:
            retriever_function = self.name_to_function[dataset_name]
        except KeyError:
            raise KeyError(f'No TPA data extracting function for dataset with name {dataset_name}')
        return retriever_function(*args, **kwargs)

    def kullen_dataclean(self, filename="datafile_tpa_location.dat"):
        """Extracting Kullen's data.
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

    def cumnock2009_dataclean(self, filename="Single_Multiple_Arcs_IMF_dipole_list_2015_AK_prel_dadu.xls",
                              usecols="A, C, D, N", sheet_name="Sheet1"):
        """Extracting Cumnock's first dataset."""
        filename = self.tpa_dir + filename

        judy = pd.read_excel(filename, sheet_name=sheet_name, index_col=None, usecols=usecols)
        for index, row in judy.iterrows():
            try:
                if int(row[0]) > 1:
                    num = True
                else:
                    num = False
            except Exception as e:
                #TODO: check these cases
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
                yield TPA(date, hemisphere=row[1], moving="yes", dadu=dadu)

    def cumnock2005_dataclean(self, filename="listoftimes.xls", sheet_name="Sheet1", usecols="A, G, M"):
        """Extracting Cumnock's second data."""
        filename = self.tpa_dir + filename

        judy = pd.read_excel(filename, sheet_name=sheet_name, index_col=None, usecols=usecols, skiprows=[1, 2])

        for index, row in judy.iterrows():
            if "Do not" in str(row[0]):
                break
            elif isinstance(row[0], int) or "00" in str(row[0]):
                if len(str(row[0])) >= 5:
                    yield TPA(dt.datetime.strptime(str(row[0]) + str(row[1]), "%y%j%X"), hemisphere="n", moving="yes", dadu=row[2])
                else:
                    date = "0" * (5 - len(str(row[0]))) + str(row[0]) + str(row[1])
                    if len(usecols.split()) > 2:
                        dadu = row[2]
                    else:
                        dadu = None
                    yield TPA(dt.datetime.strptime(date, "%y%j%X"), hemisphere="n", moving="yes", dadu=dadu)

    def cai_dataclean(self, filename=""):
        """Function that will later be used for extracting Cai's dataset of TPAs from DMSP.
        Includes conjugate TPAs.
        TODO: add this function when I have received the data"""

    @staticmethod
    def fear_fileclean(filename="Fear_TPA_data_frompaper.txt"):
        """Cleaning Fear's data to readable txt"""
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
        """Extracting Fear's data"""
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
        """Extracts dataset by Reidy et al. (2018)."""
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

    def simon_dataclean(self, filename: str = 'Simon identified arcs_200704.xlsx', ignore_noimage=True, *args, **kwargs):
        datafile = pd.read_excel(self.tpa_dir + filename, *args, **kwargs)
        datafile.replace(' ', np.nan, inplace=True)

        def merge_sn(row):
            """Merge northern and southern hemisphere into one column"""
            northern = row.iloc[:row.index.get_loc('Conjugacy/FOV')]
            southern = row.iloc[row.index.get_loc('Date.1'):]
            southern.index = [name.replace('.1', '') for name in southern.index]
            x_index = [colname for colname in southern.index if re.fullmatch('X[0-9]', colname[:2])]
            notes = pd.concat([northern[['Notes']], southern[['Notes']], row[['Conjugacy/FOV']]])
            notes.index = ['Note N', 'Note S', 'Conjugacy/FOV']
            return pd.concat([southern.iloc[:-1] if pd.notnull(southern['Time']) else northern[:-1], notes])

        # TODO: Slow
        merged_sn_df = datafile.apply(merge_sn, axis=1)
        # northern = datafile.iloc[:, :datafile.columns.get_loc('Date.1')]
        # southern = datafile.iloc[:, datafile.columns.get_loc('Date.1'):]
        # southern.columns = [name.replace('.1', '') for name in southern.columns]
        # pd.concat([northern, southern], axis=1, join='inner')

        def listify(row, x_index):
            """merge all X position columns (X1-X6) into one list
            TODO: Probably inefficient. Use pd.Series.notna() and turn Series into list?
            """
            tpa_list = [tpa_loc for tpa_loc in row[x_index] if pd.notnull(tpa_loc)]
            if tpa_list:
                return tpa_list
            else:
                return np.nan

        all_tpa_df = merged_sn_df.copy()
        all_tpa_df.insert(loc=all_tpa_df.columns.get_loc('Hemi-sphere')+1, column='X',
                          value=merged_sn_df.apply(listify, axis=1, x_index=[colname for colname in merged_sn_df.columns if re.fullmatch('X[0-9]', colname[:2])]))
        all_tpa_df.drop([colname for colname in merged_sn_df.columns if re.fullmatch('X[0-9]', colname[:2])], axis=1, inplace=True)
        # Create separate dataframe for each TPA event
        tpa_separator_index = all_tpa_df.index[all_tpa_df.isnull().all(1)]
        tpa_dfs = [all_tpa_df.iloc[:tpa_separator_index[0], :]]
        for i, j in zip(tpa_separator_index[:-1], tpa_separator_index[1:]):
            tpa_dfs.append(all_tpa_df.iloc[i+1:j, :])

        for tpa in tpa_dfs:
            if ignore_noimage and (tpa['Conjugacy/FOV'].str.contains('no image', na=False)).all():
                continue

            tpa = tpa.sort_values(by=['Date', 'Time'])
            if (multiple_arc_idx := tpa['Conjugacy/FOV'].str.contains('multiple arcs', na=False)).any():
                for i, first_detection_m in tpa[multiple_arc_idx].iterrows():
                    yield TPA(dt.datetime.combine(first_detection_m['Date'].date(), first_detection_m['Time']),
                              hemisphere=first_detection_m['Hemi-sphere'].lower(), conjugate='multiple')

            for hemisphere in 'ns':
                hemisphere_tpas = tpa[tpa['Hemi-sphere'].str.lower() == hemisphere]
                if not (hemisphere_tpas.empty or hemisphere_tpas['Time'].isnull().all()):
                    first_detection = hemisphere_tpas.iloc[0, :]
                    if not (first_detection.name in multiple_arc_idx.index[multiple_arc_idx]):
                        yield TPA(dt.datetime.combine(first_detection['Date'].date(), first_detection['Time']), hemisphere=hemisphere)
                    else:
                        print(first_detection)

    @staticmethod
    def calc_motion(mlt_start, mlt_end):
        """Checks if TPA is moving or not."""
        d = abs(mlt_end - mlt_start)
        if d > 12:
            d = 24 - d
        if d > 2:
            motion = "yes"
        else:
            motion = "no"

        return motion

    @staticmethod
    def calc_dadu(mlt):
        """Checks if TPA is on dawn or dusk side."""
        if 0 < mlt <= 12:
            dadu = "dawn"
        else:
            dadu = "dusk"
        # else:
            #    print("Unknown value of dadu (dawn or dusk): {}".format(mlt1))
        #    dadu = None

        return dadu

