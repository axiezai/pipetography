# AUTOGENERATED! DO NOT EDIT! File to edit: 02_nodes.ipynb (unless otherwise specified).

__all__ = ['PreProcNodes', 'ACPCNodes']

# Internal Cell
import os
from pathlib import Path

import pipetography.core as ppt

from nipype import IdentityInterface, Function
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.pipeline import Node, MapNode, Workflow
from nipype.interfaces.freesurfer.preprocess import ReconAll
from nipype.interfaces.mrtrix3.utils import BrainMask, TensorMetrics, DWIExtract, MRMath
from nipype.interfaces.mrtrix3.preprocess import MRDeGibbs, DWIBiasCorrect
from nipype.interfaces.mrtrix3.reconst import FitTensor
from nipype.interfaces import ants
from nipype.interfaces import fsl

# Cell
class PreProcNodes:
    """
    All nodes in preprocessing pipeline
    """

    def __init__(self, bids_dir, bids_path_template, sub_list, RPE_design):
        self.subject_source = Node(IdentityInterface(fields=["subject_id", "ext"]), name = "sub_source")
        self.subject_source.iterables=[("subject_id", sub_list)]
        if RPE_design == '-rpe_none':
            self.sub_grad_files = MapNode(
                Function(input_names=['sub_dwi', 'ext'],
                    output_names=["fslgrad"],
                    function=ppt.get_sub_gradfiles
                ),
                name = 'sub_grad_files',
                iterfield = 'sub_dwi'
            )
            self.mrconvert = MapNode(
                ppt.Convert(),
                name='mrtrix_image',
                iterfield=['in_file', 'grad_fsl']
            )
        elif RPE_design == '-rpe_all':
            self.sub_grad_files1 = MapNode(
                Function(
                    input_names=["sub_dwi", "ext"],
                    output_names=["fslgrad"],
                    function=ppt.get_sub_gradfiles
                ),
                name = "sub_grad_files1",
                iterfield="sub_dwi"
            )
            self.sub_grad_files2 = MapNode(
                Function(
                    input_names=["sub_dwi", "ext"],
                    output_names=["fslgrad"],
                    function=ppt.get_sub_gradfiles
                ),
                name = "sub_grad_files2",
                iterfield="sub_dwi"
            )
            self.mrconvert1 = MapNode(
                ppt.Convert(),
                name='mrtrix_image1',
                iterfield=["in_file", "grad_fsl"]
            )
            self.mrconvert2 = MapNode(
                ppt.Convert(),
                name='mrtrix_image2',
                iterfield=["in_file", "grad_fsl"]
            )
            # concatenate the two images and their gradient files.
            self.mrconcat = MapNode(
                ppt.MRCat(),
                name='concat_dwi',
                iterfield=["image1", "image2"]
            )
            self.gradcat = MapNode(
                ppt.GradCat(),
                name='concat_grad',
                iterfield=["grad1, grad2"]
            )
        self.select_files = Node(
            SelectFiles(bids_path_template, base_directory=bids_dir),
            name='select_files'
        )
        self.get_metadata = MapNode(
            Function(
                input_names=['path', 'bids_dir'],
                output_names=['ReadoutTime', 'PE_DIR'],
                function=ppt.BIDS_metadata
            ),
            name='get_metadata',
            iterfield='path'
        )
        self.createMask = MapNode(
            BrainMask(),
            name='raw_dwi2mask',
            iterfield='in_file'
        )
        self.GradCheck = MapNode(
            ppt.GradCheck(),
            name='dwigradcheck',
            iterfield=['in_file','mask_file', 'grad_file']
        )
        self.NewGradMR = MapNode(
            ppt.Convert(),
            name='mrconvert',
            iterfield = ["in_file", 'grad_file']
        )
        self.denoise = MapNode(
            ppt.dwidenoise(),
            name='denoise',
            iterfield='in_file'
        )
        self.degibbs = MapNode(
            MRDeGibbs(),
            name='ringing_removal',
            iterfield='in_file'
        )
        self.fslpreproc = MapNode(
            ppt.dwipreproc(),
            name = "dwifslpreproc",
            iterfield=["in_file", "grad_file", "RO_time", "pe_dir"]
        )
        self.biascorrect = MapNode(
            ppt.BiasCorrect(),
            name = 'dwibiascorret',
            iterfield=["in_file", "grad_file"]
        )
        self.grad_info = MapNode(
            ppt.MRInfo(),
            name = 'NewGradient',
            iterfield = ["in_file", "grad_file"]
        )
        self.low_noise_map = MapNode(
            ppt.CheckNIZ(),
            name = 'LowNoiseMap',
            iterfield=["isfinite", "cond_if"]
        )
        self.rician_noise = MapNode(
            ppt.RicianNoise(),
            name = 'RicianNoise',
            iterfield = ["in_file","lownoisemap"]
        )
        self.check_rician = MapNode(
            ppt.CheckNIZ(),
            name = 'NoiseComparison',
            iterfield = ["isfinite", "cond_if"]
        )
        self.convert_rician = MapNode(
            ppt.Convert(),
            name = "ConvnertRician",
            iterfield = ["in_file", "grad_file"]
        )
        self.dwi_mask = MapNode(
            BrainMask(),
            name='dwi2mask',
            iterfield='in_file'
        )
        self.fit_tensor = MapNode(
            FitTensor(),
            name='dwi2tensor',
            iterfield=['in_file', 'in_mask']
        )
        self.tensor_FA = MapNode(
            TensorMetrics(),
            name='tensor2metrics',
            iterfield='in_file'
        )
        self.wm_mask = MapNode(
            ppt.MRThreshold(),
            name = 'mrthreshold',
            iterfield='in_file'
        )
        self.norm_intensity = MapNode(
            ppt.DWINormalize(),
            name='dwinormalise',
            iterfield=['in_file','mask_file']
        )
        self.sub_b0extract = MapNode(
            DWIExtract(),
            name='sub_b0extract',
            iterfield='in_file'
        )
        self.sub_b0mean = MapNode(
            MRMath(),
            name='sub_mrmath_mean',
            iterfield='in_file'
        )
        self.sub_b0mask = MapNode(
            BrainMask(),
            name='sub_dwi2mask',
            iterfield='in_file'
        )
        self.sub_convert_dwi = MapNode(
            ppt.Convert(),
            name="sub_dwi2nii",
            iterfield="in_file"
        )
        self.sub_convert_mask = MapNode(
            ppt.Convert(),
            name="sub_mask2nii",
            iterfield="in_file"
        )
        self.sub_apply_mask = MapNode(
            fsl.ApplyMask(),
            name='sub_ApplyMask',
            iterfield=['in_file', 'mask_file']
        )
        self.mni_b0extract = MapNode(
            DWIExtract(),
            name='mni_b0extract',
            iterfield='in_file'
        )
        self.mni_b0mean = MapNode(
            MRMath(),
            name='mni_mrmath_mean',
            iterfield='in_file'
        )
        self.mni_b0mask = MapNode(
            BrainMask(),
            name='mni_dwi2mask',
            iterfield='in_file'
        )
        self.mni_convert_dwi = MapNode(
            ppt.Convert(),
            name='mni_dwi2nii',
            iterfield='in_file'
        )
        self.mni_convert_mask  = MapNode(
            ppt.Convert(),
            name='mni_mask2nii',
            iterfield='in_file'
        )
        self.mni_apply_mask = MapNode(
            fsl.ApplyMask(),
            name='mni_ApplyMask',
            iterfield=['in_file', 'mask_file']
        )
        self.mni_dwi = MapNode(
            ppt.Convert(),
            name='MNI_Outputs',
            iterfield='in_file')

        self.datasink = Node(
            DataSink(
                base_directory=os.path.join(Path(bids_dir).parent, 'derivatives')
            ),
            name="datasink"
        )
        print('Data sink (output folder) is set to {}'.format(os.path.join(Path(bids_dir).parent, 'derivatives')))

    def set_inputs(self, bids_dir, bids_ext, RPE_design, mrtrix_nthreads):
        self.subject_source.inputs.ext=bids_ext
        if RPE_design == '-rpe_none':
            self.sub_grad_files.inputs.ext = bids_ext
            self.mrconvert.inputs.out_file='raw_dwi.mif'
            self.mrconvert.inputs.export_grad=True
            self.mrconvert.inputs.out_bfile='raw_dwi.b'
            self.mrconvert.force=True
            self.mrconvert.quiet=True
            self.mrconvert.inputs.nthreads=mrtrix_nthreads
        elif RPE_design == '-rpe_all':
            self.sub_grad_files1.inputs.ext = bids_ext
            self.sub_grad_files2.inputs.ext = bids_ext
            self.mrconvert1.inputs.out_file='raw_dwi1.mif'
            self.mrconvert1.inputs.export_grad=True
            self.mrconvert1.inputs.out_bfile='raw_dwi1.b'
            self.mrconvert1.inputs.force=True
            self.mrconvert1.inputs.quiet=True
            self.mrconvert1.inputs.nthreads=mrtrix_nthreads
            self.mrconvert2.inputs.out_file='raw_dwi2.mif'
            self.mrconvert2.inputs.export_grad=True
            self.mrconvert2.inputs.out_bfile='raw_dwi2.b'
            self.mrconvert2.inputs.force=True
            self.mrconvert2.inputs.quiet=True
            self.mrconvert2.inputs.nthreads=mrtrix_nthreads
        self.createMask.inputs.out_file='b0_brain_mask.mif'
        self.createMask.inputs.nthreads=mrtrix_nthreads
        self.GradCheck.inputs.export_grad=True
        self.GradCheck.inputs.out_bfile='corrected.b'
        self.GradCheck.inputs.force=True
        self.GradCheck.inputs.quiet=True
        self.GradCheck.inputs.nthreads=mrtrix_nthreads
        self.NewGradMR.inputs.out_file='corrected_dwi.mif'
        self.NewGradMR.inputs.force=True
        self.NewGradMR.inputs.quiet=True
        self.NewGradMR.inputs.nthreads=mrtrix_nthreads
        self.denoise.inputs.out_file='denoised.mif'
        self.denoise.inputs.noise = 'noise_map.mif'
        self.denoise.inputs.force=True
        self.denoise.inputs.quiet=True
        self.denoise.inputs.nthreads=mrtrix_nthreads
        self.degibbs.inputs.out_file='unring.mif'
        self.get_metadata.inputs.bids_dir=bids_dir
        self.fslpreproc.inputs.out_file='preproc.mif'
        self.fslpreproc.inputs.rpe_options=RPE_design
        self.fslpreproc.inputs.eddy_options='"--slm=linear --repol "'
        self.fslpreproc.inputs.force=True
        self.fslpreproc.inputs.quiet=True
        self.fslpreproc.inputs.nthreads=mrtrix_nthreads
        self.biascorrect.inputs.use_ants=True
        self.biascorrect.inputs.out_file='dwi_bias.mif'
        self.biascorrect.inputs.bias='biasfield.mif'
        self.grad_info.inputs.export_grad=True
        self.grad_info.inputs.out_bfile = 'rician_tmp.b'
        self.grad_info.inputs.force=True
        self.grad_info.inputs.quiet=True
        self.grad_info.inputs.nthreads = mrtrix_nthreads
        self.low_noise_map.inputs.out_file = 'lownoisemap.mif'
        self.low_noise_map.inputs.force = True
        self.low_noise_map.inputs.quiet = True
        self.low_noise_map.inputs.nthreads = mrtrix_nthreads
        self.rician_noise.inputs.power = 2
        self.rician_noise.inputs.denoise = 2
        self.rician_noise.inputs.out_file = 'rician_removed_dwi.mif'
        self.rician_noise.inputs.force=True
        self.rician_noise.inputs.quiet=True
        self.rician_noise.inputs.nthreads=mrtrix_nthreads
        self.check_rician.inputs.out_file = 'rician_tmp.mif'
        self.check_rician.inputs.force = True
        self.check_rician.inputs.nthreads = mrtrix_nthreads
        self.convert_rician.inputs.out_file = 'rician_corrected_dwi.mif'
        self.convert_rician.inputs.force = True
        self.convert_rician.inputs.nthreads = mrtrix_nthreads
        self.wm_mask.inputs.opt_abs = 0.5
        self.wm_mask.inputs.force = True
        self.wm_mask.inputs.quiet = True
        self.wm_mask.inputs.out_file = 'wm.mif'
        self.wm_mask.inputs.nthreads = mrtrix_nthreads
        self.norm_intensity.inputs.opt_intensity = 1000
        self.norm_intensity.inputs.force = True
        self.norm_intensity.inputs.quiet = True
        self.norm_intensity.inputs.out_file = 'dwi_norm_intensity.mif'
        self.norm_intensity.inputs.nthreads = mrtrix_nthreads
        self.dwi_mask.inputs.out_file = 'dwi_mask.mif'
        self.fit_tensor.inputs.out_file = 'dti.mif'
        self.tensor_FA.inputs.out_fa = 'fa.mif'
        self.sub_b0extract.inputs.bzero = True
        self.sub_b0extract.inputs.out_file = 'b0_volume.mif'
        self.sub_b0extract.inputs.nthreads = mrtrix_nthreads
        self.sub_b0mean.inputs.operation = 'mean'
        self.sub_b0mean.inputs.axis = 3
        self.sub_b0mean.inputs.out_file = 'b0_dwi.mif'
        self.sub_b0mean.inputs.nthreads = mrtrix_nthreads
        self.sub_b0mask.inputs.out_file = 'dwi_norm_mask.mif'
        self.sub_convert_dwi.inputs.out_file = 'b0_dwi.nii.gz'
        self.sub_convert_dwi.inputs.force = True
        self.sub_convert_mask.inputs.force = True
        self.sub_convert_mask.inputs.out_file = 'dwi_norm_mask.nii.gz'
        self.sub_apply_mask.inputs.out_file = 'b0_dwi_brain.nii.gz'
        self.mni_b0extract.inputs.bzero = True
        self.mni_b0extract.inputs.out_file = 'dwi_acpc_1mm_b0.mif'
        self.mni_b0extract.inputs.nthreads = mrtrix_nthreads
        self.mni_b0mean.inputs.operation = 'mean'
        self.mni_b0mean.inputs.axis = 3
        self.mni_b0mean.inputs.out_file = 'dwi_acpc_1mm_b0mean.mif'
        self.mni_b0mean.inputs.nthreads = mrtrix_nthreads
        self.mni_b0mask.inputs.out_file = 'dwi_acpc_1mm_mask.mif'
        self.mni_convert_dwi.inputs.out_file = 'dwi_acpc_1mm_b0mean.nii.gz'
        self.mni_convert_mask.inputs.out_file = 'dwi_acpc_1mm_mask.nii.gz'
        self.mni_convert_dwi.inputs.force = True
        self.mni_convert_mask.inputs.force = True
        self.mni_apply_mask.inputs.out_file = 'dwi_acpc_1mm_brain.nii.gz'
        self.mni_dwi.inputs.out_file = 'dwi_acpc_1mm.nii.gz'
        self.mni_dwi.inputs.export_grad = True
        self.mni_dwi.inputs.export_fslgrad = True
        self.mni_dwi.inputs.export_json = True
        self.mni_dwi.inputs.force = True
        self.mni_dwi.inputs.nthreads = mrtrix_nthreads
        self.mni_dwi.inputs.out_bfile = 'dwi_acpc_1mm.b'
        self.mni_dwi.inputs.out_fslgrad = ('dwi_acpc.bvecs', 'dwi_acpc.bvals')
        self.mni_dwi.inputs.out_json = 'dwi_acpc_1mm.json'


# Cell
class ACPCNodes:
    """
    Freesurfer recon-all nodes
    """
    def __init__(self, MNI_template):
        self.get_fs_id = MapNode(
            Function(
                input_names=['anat_files'],
                output_names=['fs_id_list'],
                function=ppt.anat2id
            ),
            name='freesurfer_sub_id',
            iterfield='anat_files'
        )
        self.reduceFOV = MapNode(
            fsl.utils.RobustFOV(),
            name="reduce_FOV",
            iterfield="in_file"
        )
        self.xfminverse = MapNode(
            fsl.utils.ConvertXFM(),
            name="transform_inverse",
            iterfield="in_file"
        )
        self.flirt = MapNode(
            fsl.preprocess.FLIRT(),
            name="FLIRT",
            iterfield="in_file"
        )
        self.concatxfm = MapNode(
            fsl.utils.ConvertXFM(),
            name="concat_transform",
            iterfield=["in_file", "in_file2"]
        )
        self.alignxfm = MapNode(
            ppt.fslaff2rigid(),
            name='aff2rigid',
            iterfield="in_file"
        )
        self.ACPC_warp = MapNode(
            fsl.preprocess.ApplyWarp(),
            name='apply_warp',
            iterfield=["in_file", "premat"]
        )
        self.reconall = MapNode(
            ReconAll(),
            name='FSrecon',
            iterfield=["T1_files","subject_id"]
        )
        self.t1_bet = MapNode(
            fsl.preprocess.BET(),
            name='fsl_bet',
            iterfield='in_file'
        )
        self.epi_reg = MapNode(
            fsl.epi.EpiReg(),
            name='fsl_epireg',
            iterfield=['epi','t1_head', 't1_brain']
        )
        self.acpc_xfm = MapNode(
            ppt.TransConvert(),
            name='transformconvert',
            iterfield=["flirt_xfm","flirt_in","flirt_ref"]
        )
        self.apply_xfm = MapNode(
            ppt.MRTransform(),
            name='mrtransform',
            iterfield=["in_file", "linear_xfm"]
        )
        self.regrid = MapNode(
            ppt.MRRegrid(),
            name = 'mrgrid',
            iterfield = 'in_file'
        )

    def set_inputs(self, bids_dir, MNI_template):
        self.reduceFOV.inputs.out_transform='roi2full.mat'
        self.reduceFOV.inputs.out_roi='robustfov.nii.gz'
        self.flirt.inputs.reference=MNI_template
        self.flirt.inputs.interp='spline'
        self.flirt.inputs.out_matrix_file='roi2std.mat'
        self.flirt.inputs.out_file='acpc_mni.nii.gz'
        self.xfminverse.inputs.out_file='full2roi.mat'
        self.xfminverse.inputs.invert_xfm=True
        self.concatxfm.inputs.concat_xfm=True
        self.concatxfm.inputs.out_file='full2std.mat'
        self.alignxfm.inputs.out_file='outputmatrix'
        self.ACPC_warp.inputs.out_file='acpc_t1.nii'
        self.ACPC_warp.inputs.relwarp=True
        self.ACPC_warp.inputs.output_type='NIFTI'
        self.ACPC_warp.inputs.interp='spline'
        self.ACPC_warp.inputs.ref_file=MNI_template
        self.reconall.inputs.parallel=False
        self.reconall.inputs.hippocampal_subfields_T1 = True
        self.reconall.inputs.directive='all'
        if not os.path.exists(os.path.join(Path(bids_dir).parent, 'derivatives', 'freesurfer')):
            print('No freesurfer subject folder (output folder) found, creating it at {}'.format(
                os.path.join(Path(bids_dir).parent, 'derivatives', 'freesurfer'))
                 )
            os.makedirs(os.path.join(Path(bids_dir).parent, 'derivatives', 'freesurfer'))
        elif os.path.exists(os.path.join(Path(bids_dir).parent, 'derivatives', 'freesurfer')):
            print('Freesurfer output at {}'.format(os.path.join(Path(bids_dir).parent, 'derivatives', 'freesurfer')))
        self.reconall.inputs.subjects_dir = os.path.join(
            Path(bids_dir).parent, 'derivatives', 'freesurfer'
        )
        self.t1_bet.inputs.mask = True
        self.t1_bet.inputs.robust = True
        self.t1_bet.inputs.out_file = 'acpc_t1_brain.nii.gz'
        self.epi_reg.inputs.out_base = 'dwi2acpc'
        self.acpc_xfm.inputs.flirt = True
        self.acpc_xfm.inputs.out_file = 'dwi2acpc_xfm.mat'
        self.acpc_xfm.inputs.force = True
        self.apply_xfm.inputs.out_file = 'dwi_acpc.mif'
        self.regrid.inputs.out_file = 'dwi_acpc_1mm.mif'
        self.regrid.inputs.regrid = MNI_template