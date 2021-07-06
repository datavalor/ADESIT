
import pandas as pd
import logging
logging.basicConfig()

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None 
import base64
import io

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
    "selected_point": None
}

def gen_data_holder(df):
    for c in df.columns:
        if c in ['id', 'Id', 'ID']:
            df = df.drop(columns=c)
    cols = list(df.columns)
    df[ADESIT_INDEX] = df.index
    
    return {
        "data": df,
        "graph": None,
        "user_columns": cols,
        "X": [],
        "Y": []
    }

def get_data(session_id, pydata=False, clear=False, filename=None, contents=None, copy=None):    
    @cache.memoize()
    def handle_data(session_id):
        if not copy is None: 
            logger.debug("/!\ replacing stored data /!\\")
            return copy
        logger.debug(f"/!\ full data loading of {filename} /!\\")
        if pydata:
            df = pydataset.data(dataset_names[filename])
            if filename=="diamonds": df=df.sample(n=10000)
            data_holder = gen_data_holder(df)
        elif not filename is None:
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
                data_holder = None
            data_holder = gen_data_holder(df)
        else:
            data_holder = None

        final_data = default_data
        final_data["data_holder"]=data_holder
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