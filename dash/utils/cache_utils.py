import pandas as pd
pd.options.mode.chained_assignment = None 
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import numpy as np
from sklearn import preprocessing
import logging
logging.basicConfig()

# Miscellaneous
import base64
import io

import constants
from constants import *

import pydataset
dataset_names={
    'iris':'iris',
    'housing': 'Housing',
    'diamonds': 'diamonds',
    'kidney': 'kidney'
}

logger=logging.getLogger('adesit_callbacks')
cache = None

default_data = {
    "data_holder": None,
    "graphs": {},
    "thresolds_settings": {},
    "table_data": None,
    "selected_point": {
        "point": None,
        "in_violation_with": []
    }
}

def find_resolution_of_attribute(col):
    scol = np.sort(np.unique(col))
    diff = scol[1:]-scol[:-1]
    return diff.min()


def gen_data_holder(df):
    # Proprocessing dataframe
    df = df.dropna()
    cols_type = {}
    cols_minmax = {}
    cols_ncats = {}
    cols_res = {}
    time_cols = []
    for c in df.columns:
        if c in ['id', 'Id', 'ID']:
            df = df.drop(columns=c)
        elif is_string_dtype(df[c]):  
            try:
                cols_type[c] = DATETIME_COLUMN
                df[c] = pd.to_datetime(df[c], infer_datetime_format=True)
                time_cols.append(c)
                cols_minmax[c] = [df[c].min(), df[c].max()]
                cols_res[c] = find_resolution_of_attribute(df[c])
            except ValueError:
                cols_type[c] = CATEGORICAL_COLUMN
                cols_res[c] = 1
                le = preprocessing.LabelEncoder()
                le.fit(df[c])
                cols_ncats[c] = {
                    "unique_values": sorted(le.classes_),
                    "label_encoder": le,
                }
                cols_minmax[c] = [0, len(le.classes_)-1]
        elif is_numeric_dtype(df[c]):
            cols_type[c] = NUMERICAL_COLUMN
            cols_minmax[c] = [df[c].min(), df[c].max()]
            cols_res[c] = find_resolution_of_attribute(df[c])
        else:
            df = df.drop(columns=c)

    cols = list(cols_type.keys())
    df = df[cols]
    df = df.reset_index(drop=True)
    df.insert(0, ADESIT_INDEX, df.index)
    return {
        "data": df,
        "full_data": df,
        "graph": None,
        "user_columns": cols,
        "user_columns_type": cols_type,
        "columns_minmax": cols_minmax,
        "cat_columns_ncats": cols_ncats,
        "columns_res": cols_res,
        "time_columns": time_cols,
        "time_infos": None,
        "X": [],
        "Y": []
    }

def get_data(session_id, pydata=False, clear=False, filename=None, contents=None, copy=None):    
    @cache.memoize()
    def handle_data(session_id):
        if copy is not None: return copy

        if pydata:
            df = pydataset.data(dataset_names[filename])
            if filename=="diamonds": df = df.sample(n=10000)
        elif filename is not None:
            _, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            try:
                if 'csv' in filename:
                    # Assume that the user uploaded a CSV file
                    df = pd.read_csv(
                        io.StringIO(decoded.decode('utf-8')))
                elif 'xls' in filename:
                    # Assume that the user uploaded an excel file
                    df = pd.read_excel(io.BytesIO(decoded))
            except Exception as e:
                logger.error(e)
                return None
            if constants.RESOURCE_LIMITED and (len(df.index)>MAX_N_TUPLES or len(df.columns)>MAX_N_ATTRS): 
                return None
        else:
            return None

        final_data = default_data
        final_data["data_holder"]=gen_data_holder(df)
        return final_data

    if clear: 
        cache.delete_memoized(handle_data, session_id)
        return None
    else:
        return handle_data(session_id)

def clear_session(session_id):
    get_data(session_id, clear=True)

def overwriters(name):
    def overwrite(session_id, data=default_data[name]):
        session_data=get_data(session_id)
        session_data[name]=data
        clear_session(session_id)
        get_data(session_id, copy=session_data)
    return overwrite

for k in default_data:
    exec(f"overwrite_session_{k}=overwriters('{k}')")