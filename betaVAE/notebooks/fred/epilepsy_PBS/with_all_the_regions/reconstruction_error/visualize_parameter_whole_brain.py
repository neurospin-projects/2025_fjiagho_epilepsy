from soma import aims
import json
import sys
import pandas as pd
import scipy
import scipy.stats
import numpy as np
import glob

import anatomist.api as anatomist
from soma.qt_gui.qtThread import QtThreadCall
from soma.qt_gui.qt_backend import Qt

a = anatomist.Anatomist()

Rspam_model = "/casa/host/build/share/brainvisa-share-5.2/models/models_2008/descriptive_models/segments/global_registered_spam_right/meshes/Rspam_model_meshes_1.arg"

Lspam_model = "/casa/host/build/share/brainvisa-share-5.2/models/models_2008/descriptive_models/segments/global_registered_spam_left/meshes/Lspam_model_meshes_1.arg"


json_regions = "/neurospin/dico/data/deep_folding/current/sulci_regions_gridsearch.json"

path_summary = "/neurospin/dico/fred/Runs/01_betaVAE/Program/2023_jlaval_STSbabies/betaVAE/notebooks/fred/with_all_the_regions/reconstruction_error"
path_file = "Distance_between_controls_and_patients"

with open(json_regions) as f:
    regions = json.load(f)
print(regions)

file_to_display = f"{path_summary}/{path_file}"

next(iter(regions['brain']))

df = pd.read_csv(file_to_display)[["region", "p"]]
df["p"] = -np.log10(df["p"])

res = df.groupby(['region']).mean()
res["side"] = res.index.str.split('_').str[-1]
res = res.reset_index()

res = res[~res.region.str.contains("fronto-parietal")]
res = res[~res.region.str.contains("STs-SGSM")]
res = res[~res.region.str.contains("FCLp-SGSM")]
res = res[~res.region.str.contains("CINGULATE")]

"CINGULATE_left".replace("CINGULATE", "CINGULATE.")


def get_sulci(region):
    region = region.replace("CINGULATE", "CINGULATE.")
    region = region.replace("ORBITAL", "S.Or.")
    list_sulci = list(regions['brain'][f"{region}"].keys())
    list_sulci = [x.replace("paracingular.", "S.F.int.") for x in list_sulci]
    return list_sulci


get_sulci("CINGULATE_left")

dic = {
    "FCLp-subsc-FCLa-INSULA": "F.C.L.p.-subsc.-F.C.L.a.-INSULA.",
    "FCMpost-SpC": "F.C.M.post.-S.p.C.",
    "FColl-SRh": "F.Coll.-S.Rh.",
    "FIP": "F.I.P.",
    "FPO-SCu-ScCal": "F.P.O.-S.Cu.-Sc.Cal.",
    "Lobule_parietal_sup": "Lobule_parietal_sup.",
    "ORBITAL": "S.Or.",
    "SC-SPeC": "S.C.-S.Pe.C.",
    "SC-SPoC": "S.C.-S.Po.C.",
    "SC-sylv": "S.C.-sylv.",
    "SFinf-BROCA-SPeCinf": "S.F.inf.-BROCA-S.Pe.C.inf.",
    "SFint-FCMant": "S.F.int.-F.C.M.ant.",
    "SFint-SR": "S.F.int.-S.R.",
    "SFinter-SFsup": "S.F.inter.-S.F.sup.",
    "SFmarginal-SFinfant":"S.F.marginal-S.F.inf.ant.",
    "SFmedian-SFpoltr-SFsup": "S.F.median-S.F.pol.tr.-S.F.sup.",
    "SOr-SOlf": "S.Or.-S.Olf.",
    "SPeC": "S.Pe.C.",
    "SPoC": "S.Po.C.",
    "STi-SOTlat": "S.T.i.-S.O.T.lat.",
    "STi-STs-STpol": "S.T.i.-S.T.s.-S.T.pol.",
    "STsbr": "S.T.s.br.",
    "STs": "S.T.s.",
    "ScCal-SLi": "Sc.Cal.-S.Li.",
    "SsP-SPaint": "S.s.P.-S.Pa.int.",
}

for key in dic.keys():
    res["region"] = res["region"].str.replace(key, dic[key])


res['sulcus'] = res.apply(lambda x: get_sulci(x.region), axis=1)

res = res.sort_values(by="p", ascending=False)
res = res.explode("sulcus")
res[res.region.str.contains("S.T.s.")]

for _, row in res.iterrows():
    print(row.sulcus)

res[res.sulcus=="S.F.orbitaire._right"]

def set_color_property(res, side):
    global dic

    if side == "L":
        spam_model_file = Lspam_model
    else:
        spam_model_file = Rspam_model
        
    dic[f"aims{side}"] = aims.read(spam_model_file)

    for vertex in dic[f"aims{side}"].vertices():
        vertex['p_value'] = 0.

    for _, row in res.iterrows():
        for vertex in dic[f"aims{side}"].vertices():
            vname = vertex.get('name')
            if vname == row.sulcus:
                    vertex['p_value'] = max(vertex['p_value'],
                                                row.p)
                    # if row.p < -np.log10(0.05/56):
                    #     vertex['p_value'] = 0.
                    # elif vertex['p_value'] != 0.: 
                    #     vertex['p_value'] = min(vertex['p_value'],
                    #                             row.p)
                    # else:
                    #     vertex['p_value'] = row.p
    
    dic[f"ana{side}"] = a.toAObject(dic[f"aims{side}"])

    dic[f"ana{side}"].setColorMode(dic[f"ana{side}"].PropertyMap)
    dic[f"ana{side}"].setColorProperty('p_value')
    dic[f"ana{side}"].notifyObservers()
    
                
def visualize_whole_hemisphere(view_quaternion, side, i):
    global block
    global dic
    try:
        block
    except NameError:
        block = a.createWindowsBlock(4)

    dic[f"win{i}"] = a.createWindow('3D',
                                    block=block,
                                    no_decoration=True,
                                    options={'hidden': 1})
    dic[f"win{i}"].addObjects(dic[f"ana{side}"])
    dic[f"ana{side}"].setPalette("green_yellow_red",
                              minVal=-np.log10(0.05/56), maxVal=10,
                              absoluteMode=True)
    
    dic[f"win{i}"].camera(view_quaternion=view_quaternion)

middle_view = [0.5, -0.5, -0.5, 0.5]
side_view = [0.5, 0.5, 0.5, 0.5]
bottom_view = [0, -1, 0, 0]
top_view = [0, 0, 0, -1]
 
def visualize_whole(res, side, start):
    set_color_property(res, side)
    visualize_whole_hemisphere(middle_view if side == "L" else side_view, side, start+0)
    visualize_whole_hemisphere(top_view, side, start+1)
    visualize_whole_hemisphere(bottom_view, side, start+2)
    visualize_whole_hemisphere(side_view if side == "L" else middle_view, side, start+3)

dic = {}

visualize_whole(res, "L", 0)
visualize_whole(res, "R", 4)