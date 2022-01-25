import pandas as pd
import numpy as np
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

from constants import *

def num_or_cat(attr, df):
    if is_numeric_dtype(df[attr]):
        return NUMERICAL_COLUMN
    elif is_string_dtype(df[attr]):
        return CATEGORICAL_COLUMN
    else:
        return None

def which_proj_type(Xattrs, ctypes):
    n_nums = sum([1 for attr in Xattrs if ctypes[attr]==NUMERICAL_COLUMN])
    if n_nums==len(Xattrs): return "PCA"
    elif n_nums==0: return "MCA"
    else: return "FAMD"

def to_float(str):
    try:
        return float(str)
    except ValueError:
        return 0

def is_categorical(axis, session_infos):
    if session_infos["user_columns_type"][axis]==CATEGORICAL_COLUMN: return True
    else: return False

def is_numerical(axis, session_infos):
    if session_infos["user_columns_type"][axis]==NUMERICAL_COLUMN: return True
    else: return False
        
def parse_attributes_settings(tols, ctypes):
    #formarmating for fastg3
    attributes_settings = {}
    if tols is not None:
        for row in tols:
            attr_name = row['attribute']
            attr_type = ctypes[attr_name]
            if attr_type is not None:
                if attr_type == CATEGORICAL_COLUMN:
                    attributes_settings[attr_name] = {
                        "type": "categorical",
                        "predicate": "equality"
                    }
                elif attr_type == NUMERICAL_COLUMN:
                    attributes_settings[attr_name] = {
                        "type": "numerical",
                        "predicate": "abs_rel_uncertainties",
                        "params": [to_float(row['absolute']), to_float(row['relative'])]
                    }
        return attributes_settings
    else:
        return None