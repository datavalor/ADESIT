from constants import *

def dataset_infos(name, ntuples, nattributes):
    return f'''
                Dataset: {name}  
                Number of tuples: {ntuples}  
                Number of attributes: {nattributes}
            '''

def format_date_period(period_min, period_max, format=None):
    if format is not None:
        return f'{period_min.strftime(format)} → {period_max.strftime(format)}'
    else:
        return f'{period_min} → {period_max}'

def which_proj_type(Xattrs, user_columns):
    n_nums = sum([1 for attr in Xattrs if user_columns[attr].is_numerical()])
    if n_nums==len(Xattrs): return "PCA"
    elif n_nums==0: return "MCA"
    else: return "FAMD"

def to_float(str):
    try:
        return float(str)
    except ValueError:
        return 0

def find_res(n):
    a, b = "{:e}".format(n).split("e")
    b = int(b.split('+')[-1])
    a = a.split('.')[1]
    i = len(a)-1
    while i>=0 and a[i]=='0':
        i-=1 
    i+=1
    return 10**(-i+b)
        
def parse_attributes_settings(tols, user_columns):
    #formarmating for fastg3
    attributes_settings = {}
    if tols is not None:
        for row in tols:
            attr_name = row['attribute']
            if user_columns.get(attr_name, None) is not None:
                if user_columns[attr_name].is_categorical():
                    attributes_settings[attr_name] = {
                        "type": "categorical",
                        "predicate": "equality"
                    }
                elif user_columns[attr_name].is_numerical():
                    attributes_settings[attr_name] = {
                        "type": "numerical",
                        "predicate": "abs_rel_uncertainties",
                        "params": [to_float(row['absolute']), to_float(row['relative'])]
                    }
        return attributes_settings
    else:
        return None