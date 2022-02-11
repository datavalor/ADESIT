import fastg3.ncrisp as g3ncrisp

import multiprocessing as mp
import numpy as np

import constants
from constants import *
import utils.data_utils as data_utils

def make_analysis(df, xparams, yparams, g3_computation):
    df = df.copy()
    df[G12_COLUMN_NAME] = 0
    df[G3_COLUMN_NAME] = 0  

    # Making analysis
    manager = mp.Manager()
    return_dict = manager.dict()
    process = mp.Process(target=fastg3_analysis, args=(df, xparams, yparams, g3_computation=="exact", return_dict,))
    process.daemon = True
    process.start()
    if constants.RESOURCE_LIMITED: 
        process.join(VPE_TIMEOUT)
        if process.is_alive():
            process.terminate()
            return None
    else: 
        process.join()

    vps = return_dict["vps"]
    involved_tuples = np.unique(np.array(vps))

    n_tuples = len(df.index)
    if involved_tuples is None: 
        return None
    elif len(df.index)==0:
        data = {
            'df': df,
            'df_free': None,
            'df_prob': None,
            'indicators': None,
            'graph': None
        }
    else: 
        indicators = {
            'ncounterexamples': involved_tuples.size,
            'g1': len(vps)/n_tuples**2,
            'g2': involved_tuples.size/n_tuples
        }
        if g3_computation=='exact': 
            cover = return_dict['g3_exact_cover']
            indicators['g3_computation'] = 'exact'
            g3 = len(cover)/n_tuples
            if g3 is None: return None
            indicators['g3']=g3
        else:
            cover = return_dict['g3_ub_cover']
            indicators['g3_computation'] = 'approx'
            indicators['g3']=[
                return_dict['g3_lb'], 
                len(cover)/n_tuples
            ]
        # Merging
        df[G12_COLUMN_NAME][involved_tuples] = 1
        df[G3_COLUMN_NAME][cover] = 1
        data = {
            'df': df,
            'df_free': df.loc[df[G12_COLUMN_NAME] == 0],
            'df_prob': df.loc[df[G12_COLUMN_NAME] > 0],
            'indicators': indicators,
            'graph': return_dict['vps_al']
        }
    
    return data
    



def fastg3_analysis(df, xparams, yparams, exact, return_dict):
    VPE = g3ncrisp.create_vpe_instance(
        df, 
        xparams, 
        yparams,
        verbose=False
    )
    rg3 = g3ncrisp.RSolver(VPE, precompute=True)
    vps = rg3.get_vps()
    return_dict["vps"]=vps
    return_dict["vps_al"]=rg3.get_vps(as_map=True)
    if exact:
        return_dict["g3_exact_cover"]=rg3.exact(method="wgyc", return_cover=True)
    else:
        return_dict["g3_lb"]=rg3.lower_bound(method="maxmatch")
        return_dict["g3_ub"]=rg3.lower_bound(method="maxmatch")
        gic, approx2 = rg3.upper_bound(method="gic", return_cover=True), rg3.upper_bound(method="2approx", return_cover=True)
        return_dict["g3_ub_cover"]=gic if len(gic)<len(approx2) else approx2