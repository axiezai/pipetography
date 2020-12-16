# AUTOGENERATED! DO NOT EDIT! File to edit: 02_nodes.ipynb (unless otherwise specified).

__all__ = ['PreProcNodes', 'ACPCNodes', 'PostProcNodes']

# Internal Cell
import os
import bids
bids.config.set_option('extension_initial_dot', True)

from pathlib import Path
from itertools import product

import pipetography.core as ppt

from nipype import IdentityInterface, Function
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.pipeline import Node, MapNode, Workflow
from nipype.interfaces.mrtrix3.utils import BrainMask, TensorMetrics, DWIExtract, MRMath, Generate5tt
from nipype.interfaces.mrtrix3.preprocess import MRDeGibbs, DWIBiasCorrect, ResponseSD
from nipype.interfaces.mrtrix3.reconst import FitTensor, EstimateFOD, ConstrainedSphericalDeconvolution
from nipype.interfaces import ants
from nipype.interfaces import fsl

# Cell
class PreProcNodes:
    """
    Initiate DWI preprocessing pipeline nodes.

    Inputs:
        - bids_dir (str) -
        - bids_path_template (dict) - template for file naming conventions
        - bids_ext (str) -
        - rpe_design (str)
        - mrtrix_nthreads (int)
        - regrid (bool)
        - sub_list (List)
        - ses_list (List)
        - exclude_list (tuple)
    """
    def __init__(self, bids_dir, bids_path_template, bids_ext, rpe_design, mrtrix_nthreads, regrid, sub_list, ses_list, exclude_list = [()]):
        # create sub-graphs for subjects and sessions combos
        all_sub_ses_combos = set(product(sub_list, ses_list))
        # Create BIDS output folder list
        BIDSFolders = [('preprocessed/ses-%ssub-%s' % (session, subject), 'sub-%s/ses-%s/preprocessed' % (subject,  session))
                                 for session in ses_list
                                 for subject in sub_list]
        filtered_sub_ses_list = list(all_sub_ses_combos - set(exclude_list))
        sub_iter = [tup[0] for tup in filtered_sub_ses_list]
        ses_iter = [tup[1] for tup in filtered_sub_ses_list]
        # if regrid, output name has 1mm resolution, or name has orig resolution tag
        if regrid:
            self.img_resol = '1mm'
        else:
            self.img_resol = 'orig'
        self.subject_source = Node(IdentityInterface(fields=["subject_id", "session_id"]),
                                   iterables=[("subject_id", sub_iter), ("session_id", ses_iter)],
                                   synchronize=True,
                                   name = "sub_source")
        self.subject_source.inputs.ext=bids_ext
        # reverse phase encoding design selection
        if rpe_design == '-rpe_none':
            # self.sub_grad_files.inputs.ext = bids_ext
            self.sub_grad_files = Node(
                Function(input_names=['sub_dwi', 'ext'],
                        output_names=["fslgrad"],
                        function=ppt.get_sub_gradfiles,
                        ext = bids_ext
                ),
                name = 'sub_grad_files',
            )
            self.mrconvert = Node(
                ppt.Convert(out_file='raw_dwi.mif', export_grad='raw_dwi.b', nthreads=mrtrix_nthreads),
                name='mrtrix_image',
            )
        elif rpe_design == '-rpe_all':
            # self.sub_grad_files1.inputs.ext = bids_ext
            # self.sub_grad_files2.inputs.ext = bids_ext
            self.sub_grad_files1 = Node(
                Function(
                    input_names=["sub_dwi", "ext"],
                    output_names=["fslgrad"],
                    function=ppt.get_sub_gradfiles,
                    ext = bids_ext
                ),
                name = "sub_grad_files1",
            )
            self.sub_grad_files2 = Node(
                Function(
                    input_names=["sub_dwi", "ext"],
                    output_names=["fslgrad"],
                    function=ppt.get_sub_gradfiles,
                    ext = bids_ext
                ),
                name = "sub_grad_files2",
            )
            self.mrconvert1 = Node(
                ppt.Convert(out_file='raw_dwi1.mif', export_grad='raw_dwi1.b', nthreads=mrtrix_nthreads),
                name='mrtrix_image1',
            )
            self.mrconvert2 = Node(
                ppt.Convert(out_file='raw_dwi2.mif', export_grad='raw_dwi2.b', nthreads=mrtrix_nthreads),
                name='mrtrix_image2',
            )
            # concatenate the two images and their gradient files.
            self.mrconcat = Node(
                ppt.MRCat(out_file = 'raw_dwi.mif'),
                name='concat_dwi',
            )
            self.gradcat = Node(
                ppt.GradCat(out_file = 'raw_dwi.b'),
                name='concat_grad',
            )
        self.select_files = Node(
            SelectFiles(bids_path_template, base_directory=bids_dir),
            name='select_files'
        )
        self.get_metadata = Node(
            Function(
                input_names=['path', 'bids_dir'],
                output_names=['ReadoutTime', 'PE_DIR'],
                function=ppt.BIDS_metadata,
            ),
            name='get_metadata',
        )
        self.get_metadata.inputs.bids_dir=bids_dir
        self.createMask = Node(
            BrainMask(out_file='b0_brain_mask.mif', nthreads=mrtrix_nthreads),
            name='raw_dwi2mask',
        )
        self.GradCheck = Node(
            ppt.GradCheck(export_grad='corrected.b', nthreads=mrtrix_nthreads),
            name='dwigradcheck',
        )
        self.NewGradMR = Node(
            ppt.Convert(out_file='corrected_dwi.mif', nthreads=mrtrix_nthreads),
            name='mrconvert',
        )
        self.denoise = Node(
            ppt.dwidenoise(out_file='denoised.mif', noise = 'noise_map.mif', nthreads=mrtrix_nthreads),
            name='denoise',
        )
        self.degibbs = Node(
            MRDeGibbs(out_file='unring.mif', nthreads = mrtrix_nthreads),
            name='ringing_removal',
        )
        self.fslpreproc = Node(
            ppt.dwipreproc(out_file='preproc.mif', rpe_options=rpe_design, eddy_options='"--slm=linear --repol "', nthreads=mrtrix_nthreads, export_grad='eddy_dwi.b'),
            name = "dwifslpreproc",
        )
        self.GradUpdate = Node(
            ppt.GradCheck(export_grad='tmp.b'),
            name = 'alter_gradient'
        )
        self.ModGrad = Node(
            ppt.MRInfo(export_grad='modified.b'),
            name = 'modify_gradient'
        )
        self.UpdateMif = Node(
            ppt.Convert(),
            name =  'update_image'
        )
        self.NewMask =  Node(
                BrainMask(),
                name='recreate_mask'
        )
        self.biascorrect = Node(
            ppt.BiasCorrect(use_ants=True, out_file='dwi_bias.mif', bias='biasfield.mif', nthreads = mrtrix_nthreads),
            name = 'dwibiascorrect',
        )
        self.grad_info = Node(
            ppt.MRInfo(export_grad='rician_tmp.b', nthreads = mrtrix_nthreads),
            name = 'NewGradient',
        )
        self.low_noise_map = Node(
            ppt.CheckNIZ(out_file = 'lownoisemap.mif', nthreads = mrtrix_nthreads),
            name = 'LowNoiseMap',
        )
        self.rician_noise = Node(
            ppt.RicianNoise(power = 2, denoise = 2, out_file = 'rician_removed_dwi.mif', nthreads=mrtrix_nthreads),
            name = 'RicianNoise',
        )
        self.check_rician = Node(
            ppt.CheckNIZ(out_file = 'rician_tmp.mif', nthreads = mrtrix_nthreads),
            name = 'NoiseComparison',
        )
        self.convert_rician = Node(
            ppt.Convert(out_file = 'rician_corrected_dwi.mif', nthreads = mrtrix_nthreads),
            name = "ConvertRician",
        )
        self.dwi_mask = Node(
            BrainMask(out_file = 'dwi_mask.mif'),
            name='dwi2mask',
        )
        self.fit_tensor = Node(
            FitTensor(out_file = 'dti.mif'),
            name='dwi2tensor',
        )
        self.tensor_FA = Node(
            TensorMetrics(out_fa = 'fa.mif'),
            name='tensor2metrics',
        )
        self.wm_mask = Node(
            ppt.MRThreshold(opt_abs = 0.5, out_file = 'wm.mif', nthreads = mrtrix_nthreads),
            name = 'mrthreshold',
        )
        self.norm_intensity = Node(
            ppt.DWINormalize(opt_intensity = 1000, out_file = 'dwi_norm_intensity.mif', nthreads = mrtrix_nthreads),
            name='dwinormalise',
        )
        self.sub_b0extract = Node(
            DWIExtract(bzero = True, out_file = 'b0_volume.mif', nthreads = mrtrix_nthreads),
            name='sub_b0extract',
        )
        self.sub_b0mean = Node(
            MRMath(operation = 'mean', axis = 3, out_file = 'b0_dwi.mif', nthreads = mrtrix_nthreads),
            name='sub_mrmath_mean',
        )
        self.sub_b0mask = Node(
            BrainMask(out_file = 'dwi_norm_mask.mif', nthreads = mrtrix_nthreads),
            name='sub_dwi2mask',
        )
        self.sub_convert_dwi = Node(
            ppt.Convert(out_file = 'b0_dwi.nii.gz'),
            name="sub_dwi2nii",
        )
        self.sub_convert_mask = Node(
            ppt.Convert(out_file = 'dwi_norm_mask.nii.gz'),
            name="sub_mask2nii",
        )
        self.sub_apply_mask = Node(
            fsl.ApplyMask(out_file = 'b0_dwi_brain.nii.gz'),
            name='sub_ApplyMask',
        )
        self.mni_b0extract = Node(
            DWIExtract(bzero = True, out_file = 'dwi_space-acpc_res-{}_b0.mif'.format(self.img_resol), nthreads = mrtrix_nthreads),
            name='mni_b0extract',
        )
        self.mni_b0mean = Node(
            MRMath(operation = 'mean', axis = 3, out_file = 'dwi_space-acpc_res-{}_b0mean.mif'.format(self.img_resol), nthreads = mrtrix_nthreads),
            name='mni_mrmath_mean',
        )
        self.mni_b0mask = Node(
            BrainMask(out_file = 'dwi_space-acpc_res-{}_mask.mif'.format(self.img_resol), nthreads = mrtrix_nthreads),
            name='mni_dwi2mask',
        )
        self.mni_convert_dwi = Node(
            ppt.Convert(out_file = 'dwi_space-acpc_res-{}_b0mean.nii.gz'.format(self.img_resol)),
            name='mni_dwi2nii',
        )
        self.mni_convert_mask  = Node(
            ppt.Convert(out_file = 'dwi_space-acpc_res-{}_seg-brain_mask.nii.gz'.format(self.img_resol)),
            name='mni_mask2nii',
        )
        self.mni_apply_mask = Node(
            fsl.ApplyMask(out_file = 'dwi_space-acpc_res-{}_seg-brain.nii.gz'.format(self.img_resol)),
            name='mni_ApplyMask',
        )
        self.mni_dwi = Node(
            ppt.Convert(out_file = 'dwi_space-acpc_res-{}.nii.gz'.format(self.img_resol),
                        export_grad = 'dwi_space-acpc_res-{}.b'.format(self.img_resol),
                        export_fslgrad = ('dwi_space-acpc_res-{}.bvecs'.format(self.img_resol), 'dwi_space-acpc_res-{}.bvals'.format(self.img_resol)),
                        export_json = True,
                        nthreads = mrtrix_nthreads,
                        out_json = 'dwi_space-acpc_res-{}.json'.format(self.img_resol)),
            name='MNI_Outputs',
        )

        self.datasink = Node(
            DataSink(
                base_directory=os.path.join(bids_dir, 'derivatives', 'pipetography')
            ),
            name="datasink"
        )
        substitutions = [('_subject_id_', 'sub-'),
                         ('_session_id_', 'ses-')]
        substitutions.extend(BIDSFolders)
        self.datasink.inputs.substitutions = substitutions
        print('Data sink (output folder) is set to {}'.format(os.path.join(bids_dir, 'derivatives', 'pipetography')))

# Cell
class ACPCNodes:
    """
    T1 anatomy image related nodes. Mainly ACPC alignment of T1 and DWI and extraction of white matter mask.
    Inputs:
        - MNI_template: path to MNI template provided by FSL. By default uses the environment variable FSLDIR to locate the reference templates for ACPC alignment.
    """
    def __init__(self, MNI_template):
        self.reduceFOV = Node(
            fsl.utils.RobustFOV(out_transform='roi2full.mat',
                                out_roi='robustfov.nii.gz'),
            name="reduce_FOV",
        )
        self.xfminverse = Node(
            fsl.utils.ConvertXFM(out_file='full2roi.mat', invert_xfm=True),
            name="transform_inverse",
        )
        self.flirt = Node(
            fsl.preprocess.FLIRT(reference=MNI_template, interp='spline', out_matrix_file='roi2std.mat', out_file='acpc_mni.nii.gz'),
            name="FLIRT",
        )
        self.concatxfm = Node(
            fsl.utils.ConvertXFM(concat_xfm=True, out_file='full2std.mat'),
            name="concat_transform",
        )
        self.alignxfm = Node(
            ppt.fslaff2rigid(out_file='outputmatrix'),
            name='aff2rigid',
        )
        self.ACPC_warp = Node(
            fsl.preprocess.ApplyWarp(out_file='T1w_space-acpc.nii.gz', relwarp=True, output_type='NIFTI', interp='spline', ref_file=MNI_template),
            name='apply_warp',
        )
        ## removed reconall
        self.t1_bet = Node(
            fsl.preprocess.BET(mask = True, robust = True, out_file = 'acpc_t1_brain.nii.gz'),
            name='fsl_bet',
        )
        self.epi_reg = Node(
            fsl.epi.EpiReg(out_base = 'dwi2acpc'),
            name='fsl_epireg',
        )
        self.acpc_xfm = Node(
            ppt.TransConvert(flirt = True, out_file = 'dwi2acpc_xfm.mat', force = True),
            name='transformconvert',
        )
        self.apply_xfm = Node(
            ppt.MRTransform(out_file = 'dwi_acpc.mif'),
            name='mrtransform',
        )
        self.regrid = Node(
            ppt.MRRegrid(out_file = 'dwi_space-acpc_res-{}.mif'.format(self.img_resol), regrid = MNI_template),
            name = 'mrgrid',
        )
        self.gen_5tt = Node(
            Generate5tt(algorithm = 'fsl', out_file = 'T1w_space-acpc_seg-5tt.mif'),
            name='mrtrix_5ttgen',
        )
        self.gmwmi = Node(
            ppt.gmwmi(out_file = 'gmwmi.nii.gz'),
            name='5tt2gmwmi'
        )
        self.binarize_gmwmi = Node(
            ppt.MRThreshold(opt_abs = 0.05, out_file = 'T1w_space-acpc_seg-gmwmi_mask.nii.gz'),
            name='binarize_gmwmi'
        )
        self.convert2wm = Node(
            ppt.Convert(coord = [3, 2], axes = [0, 1, 2], out_file = 'T1w_space-acpc_seg-wm_mask.nii.gz'),
            name='5tt2wm',
        )

# Cell

class PostProcNodes:
    """
    Inputs:
        BIDS_dir (str): Path to BIDS directory
        subj_template (dict): template directory for tck, dwi, T1, mask files
        skip_tuples (tuple): [('subject', 'session')] string pair to skip
    """

    def __init__(self, BIDS_dir, subj_template, skip_tuples):
        sub_list, ses_list, layout = ppt.get_subs(BIDS_dir)                  # BIDS directory for layout and iterables
        # Create BIDS output folder list
        BIDSFolders = [('connectomes/ses-%ssub-%s' % (session, subject), 'sub-%s/ses-%s/connectomes' % (subject,  session))
                                 for session in ses_list
                                 for subject in sub_list]
        preproc_dir = os.path.join(BIDS_dir, 'derivatives', 'pipetography')  # BIDS derivatives directory containing preprocessed outputs and streamline outputs
        all_sub_ses_combos = set(product(sub_list, ses_list))
        filtered_combos = list(all_sub_ses_combos - set(skip_tuples))
        sub_iter = [tup[0] for tup in filtered_combos]
        ses_iter = [tup[1] for tup in filtered_combos]
        # DWI input:
        self.subject_source = Node(
            IdentityInterface(fields=["subject_id", "session_id"]),
            iterables=[('subject_id', sub_iter), ('session_id', ses_iter)],
            synchronize=True,
            name = 'subj_source'
        )
        self.select_files = Node(
            SelectFiles(subj_template),
            base_directory = BIDS_dir,
            name = 'select_subjects'
        )
        self.linear_reg = Node(
            ants.Registration(output_transform_prefix = 'atlas_in_dwi_affine',
                              dimension = 3,
                              collapse_output_transforms = True,
                              transforms = ['Affine'],
                              transform_parameters = [(0.1,)],
                              metric = ['MI'],
                              metric_weight = [1],
                              radius_or_number_of_bins = [64],
                              number_of_iterations = [[500, 200, 200, 100]],
                              convergence_threshold = [1e-6],
                              convergence_window_size = [10],
                              smoothing_sigmas = [[4,2,1,0]],
                              sigma_units = ['vox'],
                              shrink_factors = [[8,4,2,1]],
                              use_histogram_matching = [True],
                              output_warped_image = 'atlas_in_dwi_affine.nii.gz'
                             ),
            name = 'linear_registration'
        )
        self.nonlinear_reg = Node(
            ants.Registration(output_transform_prefix = 'atlas_in_dwi_syn',
                              dimension = 3,
                              collapse_output_transforms = True,
                              transforms = ['SyN'],
                              transform_parameters=[(0.1,)],
                              metric = ['MI'],
                              metric_weight = [1],
                              radius_or_number_of_bins = [64],
                              number_of_iterations = [[500,200,200,100]],
                              convergence_threshold = [1e-06],
                              convergence_window_size = [10],
                              smoothing_sigmas = [[4,2,1,0]],
                              sigma_units = ['vox'],
                              shrink_factors = [[8,4,2,1]],
                              use_histogram_matching = [True],
                              output_warped_image = 'atlas_in_dwi_syn.nii.gz'
            ),
            name = 'nonlinear_registration'
        )
        self.round_atlas = Node(
            ppt.CheckNIZ(args = '-round', out_file = 'nodes.mif'),
            name = 'round_parcellation'
        )
        self.response = Node(
            ResponseSD(algorithm = 'dhollander',
                       wm_file = 'wm.txt',
                       gm_file = 'gm.txt',
                       csf_file = 'csf.txt'),
            name = 'SDResponse'
        )
        self.fod = Node(
            ConstrainedSphericalDeconvolution(algorithm = 'msmt_csd',
                                              wm_txt = 'wm.txt',
                                              gm_txt = 'gm.txt',
                                              gm_odf = 'gm.mif',
                                              csf_txt = 'csf.txt',
                                              csf_odf = 'csf.mif'),
            name = 'dwiFOD'
        )
        self.sift2 = Node(
            ppt.tckSIFT2(fd_scale_gm = True, out_file = 'sift2.txt'),
            name = 'sift2_filtering'
        )
        self.connectome = Node(
            ppt.MakeConnectome(out_file = 'connectome.csv', symmetric = True, zero_diag = True),
            name = 'weight_connectome'
        )
        self.distance = Node(
            ppt.MakeConnectome(scale_length = True,
                               stat_edge = 'mean',
                               symmetric = True,
                               zero_diag = True,
                               out_file = 'distances.csv'),
            name = 'weight_distance'
        )
        self.datasink = Node(
            DataSink(base_directory = preproc_dir),
            name="datasink"
        )
        substitutions = [('_subject_id_', 'sub-'),
                         ('_session_id_', 'ses-')]
        substitutions.extend(BIDSFolders)
        self.datasink.inputs.substitutions = substitutions
        self.datasink.inputs.regexp_substitutions = [(r'(_moving_image_.*\.\.)', ''),
                                                     (r'(\.nii|\.gz)', '')]
        print('Data sink (output folder) is set to {}'.format(preproc_dir))