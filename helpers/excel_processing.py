import pandas as pd
import xlrd

def load_match_info(file_path):
    workbook = xlrd.open_workbook(file_path, ignore_workbook_corruption=True)
    return pd.read_excel(workbook)

def get_match_info_from_excel(match_val, match_info_df):
    match_info = match_info_df[match_info_df['Match'].str.contains(match_val)]
    if not match_info.empty:
        return match_info.iloc[0].to_dict()
    else:
        return None
