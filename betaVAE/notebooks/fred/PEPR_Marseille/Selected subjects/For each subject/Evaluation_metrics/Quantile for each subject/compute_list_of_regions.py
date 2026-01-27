import anatomist.direct.api as ana
from soma import aims, aimsalgo
from soma.qt_gui.qt_backend import Qt
import glob
import os.path as osp
import json

import os

import numpy as np
import pandas as pd

error_PEPR= pd.read_csv("/neurospin/tmp/fred/models/2025-11-10/SC-sylv_right_UKB_16-20-03_123/PEPR_Marseille/Reconstruction_error.csv")

selected_index = np.load("/neurospin/dico/fred/Runs/01_betaVAE/Program/2023_jlaval_STSbabies/betaVAE/notebooks/fred/PEPR_Marseille/All the subjects/histogram_non_zero/index_to_save.npy")

error_PEPR= error_PEPR.loc[selected_index].reset_index(drop=True)

Index_No_Position= np.load("/neurospin/dico/fred/Runs/01_betaVAE/Program/2023_jlaval_STSbabies/betaVAE/notebooks/fred/PEPR_Marseille/Selected subjects/Lesion_type/Resection/Index_No_Position.npy")

f_tract = '/neurospin/dico/data/human/F_TRACT'

mask_dir_pat = 'derivatives/deep_folding-2025/crops/2mm/*/mask'
mask_pat = f'{mask_dir_pat}/%(side)smask_cropped.nii.gz'
mask_def_pat = f'{mask_dir_pat}/%(side)sskeleton.json'
csv_data = 'PourTheotime.tsv'
regions_graph_dir = '/neurospin/dico/data/deep_folding/current/mask/2mm/regions/meshes'
regions_graph_pat = '%(side)sregions_model_1.arg'

def find_regions(f_tract, icbm_pos):
    icbm_h = aims.StandardReferentials.icbm2009cTemplateHeader()

    reg_def = {}

    for side in ('L', 'R'):
        print(f'{f_tract}/{mask_pat}' % {'side': side})
        for maskf in glob.glob(f'{f_tract}/{mask_pat}' % {'side': side}):
            # print('maskf:', maskf)
            region = osp.basename(osp.dirname(osp.dirname(maskf)))
            # print('region:', region, side)
            mask = aims.read(maskf, border=1)
            maskdeff = osp.join(osp.dirname(maskf), f'{side}skeleton.json')
            with open(maskdeff) as f:
                maskdef = json.load(f)
            bbmin = np.array(maskdef['bbmin'][:3], dtype=float)
            vs = mask.getVoxelSize()[:3]
            bbmin *= vs
            ivs = icbm_h['voxel_size'][:3]
            hvs = (np.array(vs) - ivs) / 2
            tr = aims.AffineTransformation3d()
            tr.setTranslation(bbmin + hvs)

            mc = aims.MassCenters_S16(mask)
            mc.doit()
            massc = np.array(mc.infos()['0'][0][0])
            # print('massc:', massc)
            # print(tr.transform(massc))

            tpl_to_icbm = aims.AffineTransformation3d(
                icbm_h['transformations'][0])
            reg_to_icbm = tpl_to_icbm * tr

            pos_m = reg_to_icbm.inverse().transform(icbm_pos)
            pos_m = np.round(pos_m.np / vs).astype(int)
            # print('pos_m:', pos_m)
            if np.all(pos_m >= 0) \
                    and np.all((np.array(mask.shape[:3]) - 1 - pos_m) >= 0) \
                    and mask.at(pos_m) != 0:
                reg_def[(region, side)] = {
                    'mask': mask,
                    'region': region,
                    'side': side,
                    'region_to_icbm': reg_to_icbm,
                    'native_to_region': tr,
                    'distance_mass_center': massc - pos_m,
                }

    return reg_def

points_fixes = {
    '0005GRE_26062015': [[114, 110, 79]],
    '0018BUC_10072015': [[165, 105, 100]],
    '0009GRE_30082010': [[95, 176, 117]],
}

def regions(sub):
    graph_pat = 'sourcedata/%(sub)s/t1mri/FreesurferAtlaspre_*/default_analysis/folds/3.1/%(side)s%(sub)s.arg'

    app = Qt.QApplication([])  # must be done first

    # get focus point
    focus_points = points_fixes.get(sub)
    if focus_points is None:
        sub_data = pd.read_csv(osp.join(f_tract, csv_data), sep='\t')
        dataline = sub_data.loc[np.where(sub_data['Patient Code'] == sub[:7])[0]]
        if dataline.shape[0] != 1:
            # try second shape
            print('sub code:', sub[:7] + sub[-2:])
            dataline = sub_data.loc[np.where(sub_data['Patient Code']
                                         == sub[:7] + sub[-2:])[0]]
        if dataline.iloc[0]['MR negative'] == 'y':
            raise ValueError('subject has no lesion coordinates')
        focus_points = dataline.iloc[0]['Position (Intranat XYZ)'].split('/')
        focus_points = [[float(x) for x in fps.strip().split()]
                        for fps in focus_points]

    # read sulcal graphs
    l_graph = aims.read(glob.glob(
        f'{f_tract}/{graph_pat}' % {'sub': sub, 'side': 'L'})[0])
    r_graph = aims.read(glob.glob(
        f'{f_tract}/{graph_pat}' % {'sub': sub, 'side': 'R'})[0])

    objs = []
    regions_def = {}

    for focus_point in focus_points:

        # masks
        sub_to_icbm = aims.GraphManip.getICBMTransform(l_graph)
        point_icbm = sub_to_icbm.transform(focus_point)
        regions_def.update(find_regions(f_tract, point_icbm))

        focus_mesh0 = aims.SurfaceGenerator.icosphere(focus_point, 3., 320)
        focus_mesh0.header()['material'] = {'diffuse': [1., 0.8, 0., 1.]}
        focus_mesh1 = aims.SurfaceGenerator.icosphere(focus_point, 10., 320)
        focus_mesh1.header()['material'] = {'diffuse': [1., 0., 0., 0.6]}


    return regions_def


rows = []

for i in range (len(error_PEPR)):
    print(i)
    if i in Index_No_Position:
        j=0


    elif i==28 or i==34 or i==80 or i==294 or i==625 or i==626 or i==750:
        j=0

    else:
        sub =error_PEPR.iloc[i,0]
        regions_def = regions(sub)

        if len(regions_def)>=1:
            rows.append({
    "index_subject": i,
    "list of regions": list(regions_def.keys())
})
        else:
            j=0

df_regions = pd.DataFrame(rows)

df_regions.to_csv("List_of_regions")

