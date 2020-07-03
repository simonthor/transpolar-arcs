from .data_extraction.tpa_extract import DataExtract

if __name__ == '__main__':
    extractor = DataExtract(r'F:/Simon TPA research/2019 Lei DMSP TPA list/DMSP_arcs/')
    for tpa in extractor.simon_dataclean('Simon identified arcs_200702b.xlsx'):
        print(tpa)
