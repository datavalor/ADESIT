import fastg3.ncrisp as g3ncrisp

def make_analysis(df, xparams, yparams, exact, return_dict):
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