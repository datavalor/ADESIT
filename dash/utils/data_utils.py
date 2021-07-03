import pandas as pd
import numpy as np
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

def num_or_cat(attr, df):
    if is_numeric_dtype(df[attr]):
        return 'numerical'
    elif is_string_dtype(df[attr]):
        return 'categorical'
    else:
        return None

def to_float(str):
    try:
        return float(str)
    except ValueError:
        return 0
        
def parse_attributes_settings(tols, df):
    attributes_settings = {}
    if tols is not None:
        for row in tols:
            attr_name = row['attribute']
            attr_type = num_or_cat(attr_name, df)
            if attr_type is not None:
                if attr_type == 'categorical': # or (to_float(row['absolute'])==0 and to_float(row['relative'])==0):
                    attributes_settings[attr_name] = {
                        "type": "categorical",
                        "predicate": "equality"
                    }
                elif attr_type == 'numerical':
                    attributes_settings[attr_name] = {
                        "type": "numerical",
                        "predicate": "abs_rel_uncertainties",
                        "params": [to_float(row['absolute']), to_float(row['relative'])]
                    }
        return attributes_settings
    else:
        return None

# percentage of counter-exs for x axis
def calc_percentage(total_df,prob_df,xaxis):
    nb_tuples = len(total_df.index)
    #Custom
    nb_bins = 2 * int(round(-0.5+(2.5*np.log(nb_tuples))))
    #print(str(nb_tuples)+ " tuples and "+str(nb_bins)+" bins")
    xmax = max(total_df[str(xaxis)])
    xmin = min(total_df[str(xaxis)])
    x_range = xmax - xmin
    bin_size = x_range/nb_bins
    #Plotlys
    #bin_size = 2 * total_df[str(xaxis)].std(axis = 0, skipna = True) / pow(nb_tuples,0.25)
    #print(str(xrange/bin_size))
    x_points = []
    curve_points = []
    nall = []
    nbad = []
    b = xmin
    while b <= xmax:
        nb_all = len(total_df.loc[ (total_df[str(xaxis)] >= b) & ((total_df[str(xaxis)] < b+bin_size)) ].index)
        nb_bad = len(prob_df.loc[ (prob_df[str(xaxis)] >= b) & ((prob_df[str(xaxis)] < b+bin_size)) ].index)
        x_points.append(b+(bin_size/2))
        nall.append(nb_all)
        nbad.append(nb_bad)
        if nb_all > 0:
            ratio = nb_bad/nb_all
            curve_points.append(ratio)
        else:
            curve_points.append(0)
        #print(str(b)+" - "+str(b+bin_size)+" : "+str(nb_all)+" all and "+str(nb_bad)+" bad _ middle point : " +str(b+(bin_size/2)) )
        b += bin_size

    d = {str(xaxis) : x_points, 'Ratio' : curve_points, 'nb-all' : nall, 'nb-bad' : nbad ,'bin-size' : bin_size, 'start' : xmin}
    df = pd.DataFrame(d)
    return df

# percentage of counter-exs for y axis
def calc_vertical_percentage(total_df,prob_df,yaxis):
    nb_tuples = len(total_df.index)
    nb_bins = 2 * int(round(-0.5+(2.5*np.log(nb_tuples))))
    #print(str(nb_tuples)+ " tuples and "+str(nb_bins)+" bins")
    ymax = max(total_df[str(yaxis)])
    ymin = min(total_df[str(yaxis)])
    yrange = ymax - ymin
    bin_size = yrange/nb_bins
    y_points = []
    curve_points = []
    b = ymin
    max_nb_all = len(total_df.loc[ (total_df[str(yaxis)] >= 0) & ((total_df[str(yaxis)] < bin_size)) ].index)
    while b <= ymax:
        nb_all = len(total_df.loc[ (total_df[str(yaxis)] >= b) & ((total_df[str(yaxis)] < b+bin_size)) ].index)
        nb_bad = len(prob_df.loc[ (prob_df[str(yaxis)] >= b) & ((prob_df[str(yaxis)] < b+bin_size)) ].index)
        y_points.append(b+(bin_size/2))
        if nb_all > 0:
            ratio = nb_bad/nb_all
            curve_points.append(ratio)
        else:
            curve_points.append(0)
        #print(str(b)+" - "+str(b+bin_size)+" : "+str(nb_all)+" all and "+str(nb_bad)+" bad")
        #print(max_nb_all)
        b += bin_size
        if nb_all > max_nb_all:
            max_nb_all = nb_all
    
    #Normalize so that it fits vertical graph
    maxp = max(curve_points)
    minp = min(curve_points)
    normalized_points = []
    for p in curve_points:
        if (maxp-minp)!=0:
            normalized_points.append((p-minp)/(maxp-minp) * max_nb_all)
        else:
             normalized_points.append(0)
    d = {'Ratio' : normalized_points, str(yaxis) : y_points,'bin-size':bin_size, 'start': ymin}
    
    df = pd.DataFrame(d)
    return df