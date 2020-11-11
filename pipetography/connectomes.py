# AUTOGENERATED! DO NOT EDIT! File to edit: 03_connectomes.ipynb (unless otherwise specified).

__all__ = ['connectome']

# Internal Cell
import os
from pathlib import Path
from nipype import IdentityInterface
from nipype.pipeline import Node, Workflow
from nipype.interfaces.io import SelectFiles, DataSink

import pipetography.nodes as nodes

# Cell

class connectome:
    """
    Create a workflow that produces connectomes based on input atlases and streamlines

    Inputs:
    atlas_dir (str): base directory of folder containing atlases
    BIDS_dir (str): base BIDS directory path
    atlas_list (List of strings): names of atlases: aal, brainnectome, desikan-killiany, default is set to brainnectome for now.
    """

    def __init__(self, BIDS_dir, atlas_list, skip_tuples=[()]):
        """
        Initialize workflow nodes
        """
        self.BIDS = BIDS_dir
        self.atlas_list = atlas_list
        data_dir = os.path.join(Path(BIDS_dir).parent)
        self.skip_combos = skip_tuples
        self.subject_template = {
            'tck': os.path.join(data_dir, 'cuda_tracking', '_session_id_{session_id}_subject_id_{subject_id}',  'sub-{subject_id}_ses-{session_id}_gmwmi2wm.tck'),
            'brain': os.path.join(data_dir, 'derivatives', 'preproc_mni', '_session_id_{session_id}_subject_id_{subject_id}', 'dwi_acpc_1mm_brain.nii.gz'),
            'dwi_mif': os.path.join(data_dir, 'derivatives', 'dwi_acpc_aligned_1mm', '_session_id_{session_id}_subject_id_{subject_id}', 'dwi_acpc_1mm.mif'),
            'T1A': os.path.join(data_dir, 'derivatives', 't1_acpc_aligned', '_session_id_{session_id}_subject_id_{subject_id}', 'acpc_t1.nii'),
            'mask': os.path.join(data_dir, 'derivatives', 'preproc_mni', '_session_id_{session_id}_subject_id_{subject_id}', 'dwi_acpc_1mm_mask.nii.gz'),
            'mrtrix5tt': os.path.join(data_dir, 'derivatives', 'wm_mask', '_session_id_{session_id}_subject_id_{subject_id}', 'mrtrix3_5tt.mif')
        }


    def create_nodes(self):
        """
        Create postprocessing nodes
        """
        self.PostProcNodes = nodes.PostProcNodes(BIDS_dir=self.BIDS, subj_template = self.subject_template, skip_tuples = self.skip_combos)
        self.PostProcNodes.linear_reg.iterables = [('moving_image', self.atlas_list)]
        self.PostProcNodes.datasink.inputs.regexp_substitutions = [(r'(_moving_image_.*\.\.)', ''),
                                                                   (r'(\.nii|\.gz)', '')]
        self.workflow = None


    def connect_nodes(self, wf_name="connectomes"):
        """
        Connect postprocessing nodes into workflow
        """
        self.workflow = Workflow(name=wf_name, base_dir=os.path.join(Path(self.BIDS).parent, 'derivatives'))
        self.workflow.connect(
            [
                (self.PostProcNodes.subject_source, self.PostProcNodes.select_files, [('subject_id', 'subject_id'),
                                                                                      ('session_id', 'session_id')]),
                (self.PostProcNodes.select_files, self.PostProcNodes.linear_reg, [('brain', 'fixed_image')]),
                (self.PostProcNodes.linear_reg, self.PostProcNodes.nonlinear_reg, [('warped_image', 'moving_image')]),
                (self.PostProcNodes.select_files, self.PostProcNodes.nonlinear_reg, [('brain', 'fixed_image')]),
                (self.PostProcNodes.nonlinear_reg, self.PostProcNodes.round_atlas, [('warped_image', 'in_file')]),
                (self.PostProcNodes.round_atlas, self.PostProcNodes.connectome, [('out_file', 'in_parc')]),
                (self.PostProcNodes.round_atlas, self.PostProcNodes.distance, [('out_file', 'in_parc')]),
                (self.PostProcNodes.select_files, self.PostProcNodes.response, [('dwi_mif', 'in_file')]),
                (self.PostProcNodes.select_files, self.PostProcNodes.fod, [('dwi_mif', 'in_file')]),
                (self.PostProcNodes.select_files, self.PostProcNodes.fod, [('mask', 'mask_file')]),
                (self.PostProcNodes.response, self.PostProcNodes.fod, [('wm_file', 'wm_txt')]),
                (self.PostProcNodes.response, self.PostProcNodes.fod, [('gm_file', 'gm_txt')]),
                (self.PostProcNodes.response, self.PostProcNodes.fod, [('csf_file', 'csf_txt')]),
                (self.PostProcNodes.select_files, self.PostProcNodes.sift2, [('mrtrix5tt', 'act')]),
                (self.PostProcNodes.select_files, self.PostProcNodes.sift2, [('tck', 'in_file')]),
                (self.PostProcNodes.fod, self.PostProcNodes.sift2, [('wm_odf', 'in_fod')]),
                (self.PostProcNodes.sift2, self.PostProcNodes.connectome, [('out_file', 'in_weights')]),
                (self.PostProcNodes.select_files, self.PostProcNodes.connectome, [('tck', 'in_file')]),
                (self.PostProcNodes.select_files, self.PostProcNodes.distance, [('tck', 'in_file')]),
                (self.PostProcNodes.connectome, self.PostProcNodes.datasink, [('out_file', 'matrices.@connectome')]),
                (self.PostProcNodes.distance, self.PostProcNodes.datasink, [('out_file', 'matrices.@distance')])
            ])
        self.workflow.config['execution'] = {
                                            'use_relative_paths':'False',
                                            'hash_method': 'content',
                                            'stop_on_first_crash': 'True',
                                            }

    def draw_pipeline(self, graph_type='orig'):
        """
        Visualize workflow
        """
        self.workflow.write_graph(graph2use=graph_type, dotfilename='postprocess.dot')

    def run_pipeline(self, parallel=None):
        """
        Run nipype workflow
        """
        if type(parallel) == int:
            print("Running workflow with {} parallel processes".format(parallel))
            self.workflow.run('MultiProc', plugin_args = {'n_procs': parallel})
        elif parallel is None:
            print("Parallel processing disabled, running workflow serially")
            self.workflow.run()