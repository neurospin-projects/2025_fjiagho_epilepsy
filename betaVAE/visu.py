# visu.py
"""
bv bash

cd 2025_Champollion_Decoder/decoder

python3 reconstruction/visu.py \
  -p example \
  -l bce \
  -s 1110622,1150302
"""

import anatomist.api as ana
from soma.qt_gui.qt_backend import Qt
from soma import aims
import numpy as np
import argparse
import os
import glob


# ===========================
# Utility Functions
# ===========================

def build_gradient(pal):
    """Build a gradient palette for Anatomist visualization."""
    gw = ana.cpp.GradientWidget(None, 'gradientwidget', pal.header()['palette_gradients'])
    gw.setHasAlpha(True)
    nc = pal.shape[0]
    rgbp = gw.fillGradient(nc, True)
    rgb = rgbp.data()
    npal = pal.np['v']
    pb = np.frombuffer(rgb, dtype=np.uint8).reshape((nc, 4))
    npal[:, 0, 0, 0, :] = pb
    # Convert BGRA to RGBA
    npal[:, 0, 0, 0, :3] = npal[:, 0, 0, 0, :3][:, ::-1]
    pal.update()


def load_and_prepare_volume(anatomist, file_path, referential, palette=None, min_val=None, max_val=None):
    """Load a volume into Anatomist, wrap it into a fusion object, assign referential."""
    print('AIMS NOT READ')
    vol = aims.read(file_path)
    print('AIMS JUST READ')
    a_obj = anatomist.toAObject(vol)
    fusion = anatomist.fusionObjects(objects=[a_obj], method='VolumeRenderingFusionMethod')

    if palette:
        fusion.setPalette(palette, minVal=min_val, maxVal=max_val, absoluteMode=True)

    fusion.releaseAppRef()
    fusion.assignReferential(referential)
    return fusion


# ===========================
# Core Logic
# ===========================

def get_output_files(recon_dir, listsub, n_subjects_to_display):
    """Get decoded files either from provided subjects"""
    if listsub:
        decoded_files = [os.path.join(recon_dir, f"{sub}_output.nii.gz") for sub in listsub]
    else:
        print("No list of subjects provided, taking the first subjects.")
        decoded_files = glob.glob(os.path.join(recon_dir, "output_*.nii.gz"))

        if not decoded_files:
            raise FileNotFoundError(f"No decoded files found in {recon_dir}")
        print(decoded_files)
        decoded_files = decoded_files[0:n_subjects_to_display]
        print("Randomly selected decoded files:", [os.path.basename(f) for f in decoded_files])

    return decoded_files


def plot_ana(recon_dir, n_subjects_to_display, loss_name, listsub,
             dataset="UkBioBank40", region="S.T.s.br.", side="L"):
    """
    Display pairs of input and decoded volumes in Anatomist,
    side-by-side for each subject.
    """
    referential = a.createReferential()

    # Palette settings based on loss
    palette_config = {
        'bce': {
            'gradient': "1;1#0;1;1;0#0.994872;0#0;0;0.635897;0.266667;1;1",
            'min_val': 0, 'max_val': 0.5
        },
        'mse': {
            'gradient': "1;1#0;1;1;0#0.994872;0#0;0;0.694872;0.244444;1;1",
            'min_val': 0, 'max_val': 0.5
        },
        'ce': {
            'gradient': "1;1#0;1;0.292308;0.733333;0.510256;0;0.679487;"
                        "0.733333#1;0#0;0;0.341026;0.111111;0.507692;"
                        "0.911111;0.697436;0.111111;1;0",
            'min_val': -1.6, 'max_val': 0.33
        }
    }

    decoded_files = get_output_files(recon_dir, listsub, n_subjects_to_display)

    # Prepare palette
    pal = a.createPalette('VR-palette')
    pal.header()['palette_gradients'] = palette_config[loss_name]['gradient']
    build_gradient(pal)

    for i, decoded_path in enumerate(decoded_files):
        subject_id = os.path.basename(decoded_path).split('output_')[1]
        subject_id = subject_id.replace(".nii.gz", "")

        # ---- Load decoded file ----
        try:
            dic_windows[f'r_output_{i}'] = load_and_prepare_volume(
                a, decoded_path, referential,
                palette='VR-palette',
                min_val=palette_config[loss_name]['min_val'],
                max_val=palette_config[loss_name]['max_val']
            )
            dic_windows[f'w_output_{i}'] = a.createWindow('3D', block=block)
            dic_windows[f'w_output_{i}'].addObjects([dic_windows[f'r_output_{i}']])
        except FileNotFoundError:
            print(f"ERROR: Decoded file not found for {subject_id}. Skipping.")
            continue

        # ---- Load input file ----
        input_path = os.path.join(recon_dir, f"input_{subject_id}.nii.gz")
        print(input_path)
        if not os.path.isfile(input_path):
            print(f"Local input file missing for {subject_id}, searching in original dataset...")
            mm_skeleton_path = f"/neurospin/dico/data/deep_folding/current/datasets/{dataset}/crops/2mm/{region}/mask/{side}crops"
            input_path = os.path.join(mm_skeleton_path, f"{subject_id}_cropped_skeleton.nii.gz")

        try:
            dic_windows[f'r_input_{i}'] = load_and_prepare_volume(
                a, input_path, referential
            )
            dic_windows[f'w_input_{i}'] = a.createWindow('3D', block=block)
            dic_windows[f'w_input_{i}'].addObjects([dic_windows[f'r_input_{i}']])
        except FileNotFoundError:
            print(f"ERROR: Input file not found for {subject_id}. Skipping.")
            continue


    print("All subjects loaded and displayed successfully.")


# ===========================
# CLI
# ===========================

def main():
    parser = argparse.ArgumentParser(description="Visualize input vs decoded volumes in Anatomist.")
    parser.add_argument('-p', '--path', type=str, required=True, help="Base folder path to the reconstructions.")
    parser.add_argument('-s', '--subjects', type=str, default=None,
                        help="Comma-separated list of subject IDs to plot (e.g., 1110622,1150302).")
    parser.add_argument('-n', '--nsubjects', type=int, default=4, help="Number of subjects to plot.")

    args = parser.parse_args()
    subjects = args.subjects.split(',') if args.subjects else None

    if not os.path.isdir(args.path):
        raise FileNotFoundError(f"Provided path not found: {args.path}")

    region_name, side, loss = 'S.C.sylv.', 'R', 'mse'

    plot_ana(recon_dir=args.path,
            n_subjects_to_display=args.nsubjects,
            listsub=subjects, 
            region = region_name, 
            side = side,
            loss_name=loss)


if __name__ == "__main__":
    a = ana.Anatomist()
    nb_columns = 2
    block = a.createWindowsBlock(nb_columns)
    dic_windows = {}

    main()

    # Keep GUI open
    qt_app = Qt.QApplication.instance()
    if qt_app is not None:
        qt_app.exec_()