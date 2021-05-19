if __name__ == '__main__':
    from data_extraction import DataExtract
    datareader = DataExtract('../data')
    datareader.get_tpas('This study', only_first_tpa=True)
