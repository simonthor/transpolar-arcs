# Standard library
import warnings
import datetime as dt
import re
from typing import Iterable
# Packages
import pandas as pd
import numpy as np
# Self-written modules
from ..data_structures.tpa import TPA


# TODO: create factory class?
class DataExtract:
    """Extracts transpolar arc (TPA) data from different datasets."""

    def __init__(self, tpa_dir):
        self.data_dir = tpa_dir
        self.name_to_function = {'Fear & Milan (2012)': self.fear_dataclean,
                                 'Kullen et al. (2002)': self.kullen_dataclean,
                                 'Cumnock et al. (2009)': self.cumnock2009_dataclean,
                                 'Reidy et al. (2018)': self.reidy_dataclean,
                                 'Cumnock (2005)': self.cumnock2005_dataclean,
                                 'New dataset': self.new_thor_dataclean,
                                 'This study': self.new_thor_dataclean}

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
        filename = self.data_dir + filename
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
        filename = self.data_dir + filename

        judy = pd.read_excel(filename, sheet_name=sheet_name, index_col=None, usecols=usecols)
        for index, row in judy.iterrows():
            try:
                if int(row[0]) > 1:
                    num = True
                else:
                    num = False
            except Exception as e:
                # TODO: check these cases
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
        filename = self.data_dir + filename

        judy = pd.read_excel(filename, sheet_name=sheet_name, index_col=None, usecols=usecols, skiprows=[1, 2])

        for index, row in judy.iterrows():
            if "Do not" in str(row[0]):
                break
            elif isinstance(row[0], int) or "00" in str(row[0]):
                if len(str(row[0])) >= 5:
                    yield TPA(dt.datetime.strptime(str(row[0]) + str(row[1]), "%y%j%X"), hemisphere="n", moving="yes",
                              dadu=row[2])
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
        filename = self.data_dir + filename

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
        filename = self.data_dir + filename
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
    def merge_sn(row):
        """Merge northern and southern hemisphere into one column"""
        northern = row.iloc[:row.index.get_loc('Conjugacy/FOV')]
        southern = row.iloc[row.index.get_loc('Date.1'):]
        southern.index = [name.replace('.1', '') for name in southern.index]
        x_index = [colname for colname in southern.index if re.fullmatch('X[0-9]', colname[:2])]
        notes = pd.concat([northern[['Notes']], southern[['Notes']], row[['Conjugacy/FOV']]])
        notes.index = ['Note N', 'Note S', 'Conjugacy/FOV']
        return pd.concat([southern.iloc[:-1] if pd.notnull(southern['Time']) else northern[:-1], notes])

    def thor_dfs(self, filename: str = 'Sept_Oct_2015_TPAs_final_210518.xlsx', *args, **kwargs):
        datafile = pd.read_excel(self.data_dir + filename, *args, **kwargs)
        datafile.replace(' ', np.nan, inplace=True)

        # TODO: Slow, do not use apply
        merged_sn_df = datafile.apply(self.merge_sn, axis=1)

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
        all_tpa_df.insert(loc=all_tpa_df.columns.get_loc('Hemi-sphere') + 1, column='X',
                          value=merged_sn_df.apply(listify, axis=1,
                                                   x_index=[colname for colname in merged_sn_df.columns if
                                                            re.fullmatch('X[0-9]', colname[:2])]))
        all_tpa_df.drop([colname for colname in merged_sn_df.columns if re.fullmatch('X[0-9]', colname[:2])], axis=1,
                        inplace=True)
        # Create separate dataframe for each TPA event
        tpa_separator_index = all_tpa_df.index[all_tpa_df.isnull().all(1)]
        tpa_dfs = [all_tpa_df.iloc[:tpa_separator_index[0], :]]
        for i, j in zip(tpa_separator_index, np.append(tpa_separator_index[1:], None)):
            tpa_dfs.append(all_tpa_df.iloc[i + 1:j, :])

        return tpa_dfs

    def thor_dataclean(self, filename: str = 'Sept_Oct_2015_TPAs_final_210518.xlsx', ignore_noimage: bool = True,
                       ignore_singlearcs_with_multiple: bool = False, only_first_tpa: bool = False, *args, **kwargs):
        """TODO: add docstring"""
        tpa_dfs = self.thor_dfs(filename, *args, **kwargs)

        # TODO: guard clauses
        # TODO: This is horrendous spaghetti code. Must be refactored.
        #  Begin by taking all first TPAs, then check for multiple arcs
        for tpa in tpa_dfs:
            if tpa['Conjugacy/FOV'].str.contains('- ignore!', na=False).any():
                continue

            if ignore_noimage and (tpa['Conjugacy/FOV'].str.contains('no image', na=False)).all():
                continue

            tpa = tpa.sort_values(by=['Date', 'Time'])

            if only_first_tpa:
                for hemisphere in 'ns':
                    hemisphere_tpas = tpa[tpa['Hemi-sphere'].str.lower() == hemisphere]
                    if not (hemisphere_tpas.empty or hemisphere_tpas['Time'].isnull().all()):
                        first_detection = hemisphere_tpas.iloc[0, :]
                        if pd.isnull(first_detection['Conjugacy/FOV']):
                            conjugate_type = 'conjugate'
                        elif 'multiple arcs' in first_detection['Conjugacy/FOV']:
                            conjugate_type = 'multiple'
                        elif 'non-conjugate' in first_detection['Conjugacy/FOV']:
                            conjugate_type = 'non-conjugate'
                        elif 'conjugate' in first_detection['Conjugacy/FOV']:
                            conjugate_type = 'conjugate below'
                        elif 'no image' in first_detection['Conjugacy/FOV']:
                            conjugate_type = ''
                        else:
                            conjugate_type = 'conjugate'
                            print(f"encountered unexpected value '{first_detection['Conjugacy/FOV']}'.\n"
                                  f"Setting conjugate_type value to default: '{conjugate_type}'.")

                        if isinstance(first_detection['X'], list) and len(first_detection['X']) == 1:
                            # (181+260)/2 = 220.5
                            dadu = 'dawn' if first_detection['X'][0] > 220.5 else 'dusk'
                        else:
                            dadu = ''

                        yield TPA(dt.datetime.combine(first_detection['Date'].date(), first_detection['Time']),
                                  hemisphere=hemisphere, conjugate=conjugate_type, dadu=dadu)
                continue

            if (multiple_arc_idx := tpa['Conjugacy/FOV'].str.contains('multiple arcs', na=False)).any():
                for i, first_detection_m in tpa[multiple_arc_idx].iterrows():
                    # TODO: add x-axis coordinate when initializing TPA
                    yield TPA(dt.datetime.combine(first_detection_m['Date'].date(), first_detection_m['Time']),
                              hemisphere=first_detection_m['Hemi-sphere'].lower(), conjugate='multiple')
                if ignore_singlearcs_with_multiple:
                    continue

            for hemisphere in 'ns':
                hemisphere_tpas = tpa[tpa['Hemi-sphere'].str.lower() == hemisphere]
                if not (hemisphere_tpas.empty or hemisphere_tpas['Time'].isnull().all()):
                    first_detection = hemisphere_tpas.iloc[0, :]
                    if not (first_detection.name in multiple_arc_idx.index[multiple_arc_idx]):
                        if pd.isnull(first_detection['Conjugacy/FOV']):
                            conjugate_type = 'conjugate'
                        elif 'non-conjugate' in first_detection['Conjugacy/FOV']:
                            conjugate_type = 'non-conjugate'
                        elif 'conjugate' in first_detection['Conjugacy/FOV']:
                            conjugate_type = 'conjugate below'
                        elif 'no image' in first_detection['Conjugacy/FOV']:
                            conjugate_type = ''
                        else:
                            conjugate_type = 'conjugate'
                            print(f"encountered unexpected value '{first_detection['Conjugacy/FOV']}'.\n"
                                  f"Setting conjugate_type value to default: '{conjugate_type}'.")

                        if isinstance(first_detection['X'], list) and len(first_detection['X']) == 1:
                            # (181+260)/2 = 220.5
                            dadu = 'dawn' if first_detection['X'][0] > 220.5 else 'dusk'
                        else:
                            dadu = ''

                        yield TPA(dt.datetime.combine(first_detection['Date'].date(), first_detection['Time']),
                                  hemisphere=hemisphere, conjugate=conjugate_type, dadu=dadu)

    def new_thor_dataclean(self, filename: str = 'Sept_Oct_2015_TPAs_final_210518.xlsx', ignore_noimage: bool = True,
                           ignore_singlearcs_with_multiple: bool = False, only_first_tpa: bool = False, debug: bool = False,
                           ignore_single_image: bool = False, *args, **kwargs):
        """More efficient TPA extracter with cleaner code. This will become `thor_dataclean` in future versions."""
        raw_datafile = pd.read_excel(self.data_dir + filename, *args, **kwargs)

        # Clean data and merge SH columns with NH columns
        merged_sn_df = raw_datafile.replace(' ', pd.NA)

        s_idx = merged_sn_df['Time.1'].notnull()
        assert not (sn_overlap_idx := (s_idx & merged_sn_df['Time'].notnull())).any(), \
            f'Both NH and SH arcs exist on same time for lines {merged_sn_df.index[sn_overlap_idx] + 2}'
        merged_sn_df.loc[s_idx, 'Time':'Notes'] = merged_sn_df.loc[s_idx, 'Time.1':'Notes.1'].values
        # Remove all SH columns and beyond as I have merged SH with NH
        merged_sn_df.drop(columns=merged_sn_df.columns[merged_sn_df.columns.get_loc('Date.1'):], inplace=True)

        # Separate dataframe into separate events by adding an event number
        linebreak = merged_sn_df.index[merged_sn_df.isnull().all(axis=1)]
        df_with_eventnr = merged_sn_df.copy()
        # Add eventnr column
        df_with_eventnr['event nr'] = pd.NA
        df_with_eventnr.loc[linebreak + 1, 'event nr'] = np.arange(linebreak.size)
        df_with_eventnr = df_with_eventnr.drop(index=linebreak).reset_index()
        df_with_eventnr.rename(columns={'index': 'xlsx row'}, inplace=True)
        df_with_eventnr['xlsx row'] += 2
        df_with_eventnr['event nr'] = df_with_eventnr['event nr'].fillna(method='ffill')
        # Remove rows where there are no TPA coordinates listed
        tpa_count = (df_with_eventnr.loc[:, 'X1 dusk':'X4 dawn'].notnull()).sum(axis=1)
        df_with_eventnr = df_with_eventnr[tpa_count != 0]

        clean_df = df_with_eventnr.groupby('event nr').filter(
            lambda event_df: not event_df['Conjugacy/FOV'].str.contains('- ignore', na=False).any())
        clean_df.reset_index(drop=True, inplace=True)

        clean_df['dawn/dusk'] = None
        tpa_count = (clean_df.loc[:, 'X1 dusk':'X4 dawn'].notnull()).sum(axis=1)
        location = clean_df.loc[:, 'X1 dusk':'X4 dawn'].sum(axis=1, skipna=True)
        location[tpa_count != 1] = pd.NA
        clean_df.loc[(tpa_count == 1) & (location > 220.5), 'dawn/dusk'] = 'dawn'
        clean_df.loc[(tpa_count == 1) & (location <= 220.5), 'dawn/dusk'] = 'dusk'
        clean_df['conjugate type'] = 'conjugate'

        clean_df['Hemi-sphere'] = clean_df['Hemi-sphere'].str.lower()

        # Checks if both N and S are in the event. If they are not, it is a non-conjugate event
        # TODO: Probably slow but works. Can maybe use the fact that event nr is ordered
        # TODO: if ignore_single_image is True, this might need to be changed
        clean_df.loc[
            clean_df['event nr'].isin(clean_df['event nr'].unique()[clean_df.groupby('event nr')['Hemi-sphere'].agg(set) != {'n', 's'}])
            , 'conjugate type'] = 'non-conjugate'

        clean_df.loc[
            clean_df['Conjugacy/FOV'].str.contains('conjugate', na=False)
            & ~clean_df['Conjugacy/FOV'].str.contains('non-conjugate', na=False), 'conjugate type'] = 'conjugate below'

        clean_df.loc[clean_df['Conjugacy/FOV'].str.contains('no image', na=False), 'conjugate type'] = ''

        if debug:
            yield clean_df

        first_sn_index = clean_df.reset_index().groupby(['event nr', 'Hemi-sphere']).first()['index'].values
        chosen_tpas_index = pd.Series(index=clean_df.index, data=False, dtype=bool)
        chosen_tpas_index[first_sn_index] = True
        if not only_first_tpa:
            chosen_tpas_index[clean_df[clean_df['Conjugacy/FOV'].str.contains('multiple', na=False)].index] = True
        if ignore_noimage:
            assert chosen_tpas_index.shape == clean_df['Conjugacy/FOV'].str.contains('no image', na=False).shape
            chosen_tpas_index &= ~clean_df['Conjugacy/FOV'].str.contains('no image', na=False)
        if ignore_singlearcs_with_multiple:
            # TODO: This code is probably slow. Might be possible to remove for-loop
            for _, event_df in clean_df.groupby('event nr'):
                if (multiple_idx := event_df['Conjugacy/FOV'].str.contains('multiple', na=False)).any() and \
                        event_df.index[0] != event_df.index[multiple_idx][0]:
                    chosen_tpas_index[event_df.index[0]] = False
        if ignore_single_image:
            # TODO: This code is probably slow. Might be possible to remove for-loop
            for i, event in clean_df.groupby(['event nr', 'Hemi-sphere']):
                if event.shape[0] <= 1:
                    chosen_tpas_index[event.index[0]] = False

        print('number of TPAs:', chosen_tpas_index.sum())
        for row in clean_df[chosen_tpas_index].itertuples():
            yield TPA(dt.datetime.combine(row.Date.date(), row.Time), hemisphere=row[4], conjugate=row[13],
                      dadu=row[12], multiple=True if 'multiple' in str(row[10]).lower() else False)

    def from_cache(self, all_datasets: Iterable):
        # Load cached data
        for dataset in all_datasets:
            dataset.tpa_values = dict(np.load(f'{self.data_dir}{dataset.name}/tpa_values.npz'))
            dataset.tpa_properties = dict(
                np.load(f'{self.data_dir}{dataset.name}/tpa_properties.npz', allow_pickle=True))
            dataset.total = dict(np.load(f'{self.data_dir}{dataset.name}/total.npz'))
        return all_datasets

    def to_cache(self, all_datasets: Iterable, settings: dict):
        # cache data
        for dataset in all_datasets:
            np.savez(f'{self.data_dir}{dataset.name}/tpa_values.npz', **dataset.tpa_values)
            np.savez(f'{self.data_dir}{dataset.name}/total.npz', **dataset.total)
            np.savez(f'{self.data_dir}{dataset.name}/tpa_properties.npz', **dataset.tpa_properties)

        with open('F:/Simon TPA research/cached data/README.txt', 'w') as data_config_file:
            data_config_file.write(f'Settings used when generating this data:\n')
            for setting_name, value in settings.items():
                data_config_file.write(f'{setting_name} = {value}\n')

    @staticmethod
    def calc_motion(mlt_start, mlt_end):
        """Checks if TPA is moving or not."""
        d = abs(mlt_end - mlt_start)
        if d > 12:
            d = 24 - d
        if d > 2:
            return "yes"
        else:
            return "no"

    @staticmethod
    def calc_dadu(mlt):
        """Checks if TPA is on dawn or dusk side."""
        if 0 < mlt <= 12:
            return "dawn"
        else:
            return "dusk"
        # else:
        #    print("Unknown value of dadu (dawn or dusk): {}".format(mlt1))
        #    dadu = None
