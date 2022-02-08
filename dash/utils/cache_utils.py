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
    'data_holder': None,
    'graphs': {},
    'thresolds_settings': {},
    'table_data': None,
    'selection_infos': {
        'point': None,
        'in_violation_with': pd.DataFrame()
    }
}

class AdesitAttribute:
    def __init__(self, column):
        if is_string_dtype(column):
            try:
                column = pd.to_datetime(column, infer_datetime_format=True)
                self.type = DATETIME_COLUMN
                self.minmax = [column.min(), column.max()]
                self.resolution = find_resolution_of_attribute(column)
            except ValueError:
                self.type = CATEGORICAL_COLUMN
                self.resolution = 1
                le = preprocessing.LabelEncoder()
                le.fit(column)
                self.sorted_classes = sorted(le.classes_)
                self.label_encoder = le
                self.minmax = [0, len(le.classes_)-1]
        elif is_numeric_dtype(column):
            self.type = NUMERICAL_COLUMN
            self.minmax = [column.min(), column.max()]
            self.resolution = find_resolution_of_attribute(column)
        self.original_minmax = self.minmax

    def get_type(self):
        return self.type

    def is_numerical(self):
        if self.type == NUMERICAL_COLUMN: return True
        else: return False

    def is_datetime(self):
        if self.type == DATETIME_COLUMN: return True
        else: return False
    
    def is_categorical(self):
        if self.type == CATEGORICAL_COLUMN: return True
        else: return False

    def get_minmax(self, relative_margin=0, auto_margin=False, original=False):
        if original: min, max = self.original_minmax
        else: min, max = self.minmax
        abs_margin = (max-min)*relative_margin
        if auto_margin:
            if self.is_categorical():
                min-=0.5
                max+=0.5
            else:
                abs_margin = (max-min)*0.05
        else:
            abs_margin = (max-min)*relative_margin

        return [min-abs_margin, max+abs_margin]

def find_resolution_of_attribute(col):
    scol = np.sort(np.unique(col))
    diff = scol[1:]-scol[:-1]
    return diff.min()

def gen_data_holder(df):
    # Proprocessing dataframe
    df = df.dropna()
    columns = {}
    for c in df.columns:
        if c in ['id', 'Id', 'ID'] or not (is_string_dtype(df[c]) or is_numeric_dtype(df[c])):
            df = df.drop(columns=c)
        else:
            NewAttribute = AdesitAttribute(df[c])
            columns[c] = NewAttribute
            if NewAttribute.is_datetime():
                df[c] = pd.to_datetime(df[c], infer_datetime_format=True)

    df = df[list(columns.keys())]
    df = df.reset_index(drop=True)
    df.insert(0, ADESIT_INDEX, df.index)
    data_holder =  {
        'data': {
            'df': df,
            'df_free': None,
            'df_prob': None,
        },
        'df_full': df,
        'indicators': None,
        'graph': None,
        'user_columns': columns,
        'time_infos': None,
        "X": [],
        "Y": []
    }
    return data_holder

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
        final_data['data_holder']=gen_data_holder(df)
        return final_data

    if clear: 
        cache.delete_memoized(handle_data, session_id)
        return None
    else:
        return handle_data(session_id)

def clear_session(session_id):
    get_data(session_id, clear=True)

def overwriters(name):
    def overwrite(session_id, data=default_data[name], source=''):
        logger.debug(f'====================> Overwriting {name} from {source}')
        session_data=get_data(session_id)
        session_data[name]=data
        clear_session(session_id)
        get_data(session_id, copy=session_data)
    return overwrite

for k in default_data:
    exec(f"overwrite_session_{k}=overwriters('{k}')")