#!/usr/bin/env python

import anatomist.direct.api as ana
from soma import aims, aimsalgo
from soma.qt_gui.qt_backend import Qt
import glob
import os.path as osp
import json
import numpy as np
import pandas as pd

'''
subjects = [
    '0001FLO_02052012',
    '0005GRE_26062015',
    '0005LIL_20012016',
    '0003LYO_05052015',
    '0013ROT_17042013',
    '0018BUC_10072015',
    '0006GRE_16072015',
    '0032ROT_16012014',
    '0032ROT_31012017',
    '0009GRE_30082010',
]'''

points_fixes = {
    '0005GRE_26062015': [[114, 110, 79]],
    '0018BUC_10072015': [[165, 105, 100]],
    '0009GRE_30082010': [[95, 176, 117]],
}

sub = '0013ROT_17042013'
print('sub:', sub)

f_tract = '/neurospin/dico/data/human/F_TRACT'
graph_pat = 'sourcedata/%(sub)s/t1mri/FreesurferAtlaspre_*/default_analysis/folds/3.1/%(side)s%(sub)s.arg'
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


# def regions_meshes(regions_def, erosion=7.):
#     regions = []
#     mesher = aimsalgo.Mesher()
#     a = ana.Anatomist()
#     long_side = {'L': 'left', 'R': 'right'}
#
#     nom = aims.read(
#         aims.carto.Paths.findResourceFile(
#             'nomenclature/hierarchy/champollion_v1.hie'))
#
#     for reg_def in regions_def.values():
#         mask = reg_def['mask']
#         region = reg_def['region']
#         side = reg_def['side']
#         reg_to_icbm = reg_def['region_to_icbm']
#         # tr = reg_def['native_to_region']
#         # dist = reg_def['distance_mass_center']
#         mask[mask.np != 0] = 32767
#         mg = aimsalgo.MorphoGreyLevel_S16()
#         mask = mg.doErosion(mask, erosion)
#         reg_mesh = aims.AimsSurfaceTriangle()
#         mesher.getBrain(mask, reg_mesh)
#         areg_mesh = a.toAObject(reg_mesh)
#         ref = a.createReferential()
#         trline = list(reg_to_icbm.translation()) \
#             + list(reg_to_icbm.rotation()[:3, :3, 0, 0].ravel())
#         a.execute('LoadTransformation',
#                   matrix=trline,
#                   origin=ref,
#                   destination=a.mniTemplateRef)
#         areg_mesh.setReferential(ref)
#         areg_mesh.setName(f'{region}_{long_side[side]}')
#         col = list(nom.find_color(f'{region}_{long_side[side]}',
#                                   default_color=[0.7, 0.7, 0.7, 1.]))
#         if len(col) < 4:
#             col.append(1.)
#         col[3] = 0.59
#         areg_mesh.setMaterial(diffuse=col, selectable_mode='always_selectable')
#         areg_mesh.setChanged()
#         areg_mesh.notifyObservers()
#         regions.append(areg_mesh)
#
#     return regions


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

print(focus_points)

# read sulcal graphs
l_graph = aims.read(glob.glob(
    f'{f_tract}/{graph_pat}' % {'sub': sub, 'side': 'L'})[0])
r_graph = aims.read(glob.glob(
    f'{f_tract}/{graph_pat}' % {'sub': sub, 'side': 'R'})[0])

# visu
a = ana.Anatomist()
l_agraph = a.toAObject(l_graph)
r_agraph = a.toAObject(r_graph)

l_agraph.applyBuiltinReferential()
r_agraph.setReferential(l_agraph.referential)
r_agraph.setChanged()
r_agraph.notifyObservers()

long_side = {'L': 'left', 'R': 'right'}
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
    afmesh0 = a.toAObject(focus_mesh0)
    afmesh1 = a.toAObject(focus_mesh1)
    afmesh0.setReferential(l_agraph.referential)
    afmesh1.setReferential(l_agraph.referential)

    objs += [afmesh0, afmesh1]

# regions = regions_meshes(regions_def)
nom = a.loadObject(aims.carto.Paths.findResourceFile(
    'nomenclature/hierarchy/champollion_v1.hie'))

l_reg_graph = a.loadObject(osp.join(regions_graph_dir,
                                    regions_graph_pat % {'side': 'L'}))
r_reg_graph = a.loadObject(osp.join(regions_graph_dir,
                                    regions_graph_pat % {'side': 'R'}))
l_reg_graph.applyBuiltinReferential()
r_reg_graph.applyBuiltinReferential()
print(f"regions_def = {regions_def}")
w = a.createWindow('3D')
w.addObjects([l_agraph, r_agraph] + objs)
# w.addObjects(regions)
w.addObjects([l_reg_graph, r_reg_graph], add_graph_nodes=False)
w.moveLinkedCursor(focus_points[0])
w.setReferential(l_agraph.referential)
sel_regions = ' '.join(f'{r[0]}_{long_side[r[1]]}' for r in regions_def.keys())
print('sel_regions:', sel_regions)
a.execute('SelectByNomenclature', nomenclature=nom, names=sel_regions)
a.execute('SelectByNomenclature', nomenclature=nom, names=sel_regions,
        modifiers='toggle')

app.exec()
del objs