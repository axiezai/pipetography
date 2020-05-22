# Pipetography
> Nipype and mrtrix3 based pre-/post- processing pipeline for brain diffusion-MRI and generation of structural connectomes of the brain.


![CI](https://github.com/axiezai/pipetography/workflows/CI/badge.svg)
![docker](https://img.shields.io/docker/v/axiezai/pipetography)

This repo currently only has pre-processing capabilities! More will be added in the near future.

The pre-processing workflow has been updated to reflect what's seen in the optimal [DESIGNER pipeline](http://www.sciencedirect.com/science/article/pii/S1053811918306827) and on [mrtrix3 cloud apps on brainlife.io](https://brainlife.io). 

## Install

Since most usages will be on HPC resources, I highly recommend that you use the `Singularity` or `Docker` recipe in the repository instead of installing the Python module.

Install version `0.2.0` as a Python module:

`pip install pipetography`

Since `pipetography` is a `Nipype` wrapper around `mrtrix3`, `ANTs`, and `FSL`, you have to follow their installation instructions and set them up appropriately on your machine as well:    
 - [mrtrix3 v3.0.0](https://mrtrix.readthedocs.io/en/latest/installation/before_install.html)
 
 - [ANTs](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS)
     
 - [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
 
 - [Freesurfer v6.0](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)
 
 - [Matlab Run Time Compiler for freesurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/MatlabRuntime)
 

## How to use

#### Use as connected Nipype nodes for DWI preprocessing
We will wrap all of our tasks in `Nipype`'s `Nodes`

Nipype wraps the tasks into Nodes and connects them into an automated workflow that can run parallel tasks, the preprocessing workflow includes several functions, some of which require user inputs. We will go over them here.

```
%%capture
from pipetography.pipeline import pipeline
from pipetography.core import *

preproc_dwi = pipeline()
```

```
#example
preproc_dwi.check_environment()
```

    FSLOUTPUTTYPE is valid
    FSLDIR is valid
    ANTS is valid
    mrtrix3 is valid


```
#example
#set output destination:
preproc_dwi.set_datasink()
```

    Please indicate an output directory:  'output'


Take a look at what's in the `pipeline`:

```
#example
preproc_dwi.__dict__
```




    {'data_dir': 'data',
     'sub_list': ['11048'],
     'layout': BIDS Layout: ...ers/xxie/lab/pipetography/data | Subjects: 1 | Sessions: 1 | Runs: 0,
     'dwi_file': 'sub-{subject_id}/ses-*/dwi/sub-{subject_id}_ses-*_dwi.nii.gz',
     'b_files': 'sub-{subject_id}/ses-1/dwi/sub-{subject_id}_ses-1_dwi.bv*',
     'sub_template': {'dwi': 'sub-{subject_id}/ses-*/dwi/sub-{subject_id}_ses-*_dwi.nii.gz',
      'b_files': 'sub-{subject_id}/ses-1/dwi/sub-{subject_id}_ses-1_dwi.bv*'},
     'sub_source': data_source,
     'select_files': select_files,
     'bfiles_input': select_bfiles,
     'denoise': denoise,
     'ringing': ringing_removal,
     'ants_bfc': ants_bias_correct,
     'mrt_preproc': mrtrix3_preproc,
     'atlas_dir': None,
     'atlas_names': None,
     'atlas_source': None,
     'select_atlas': None,
     'b0extract': dwiextract,
     'b0mean': mrmath,
     'fsl_bet': brain_extraction,
     'linear_coreg': linear_registration,
     'nonlinear_coreg': nonlinear_registration,
     'datasink': datasink,
     'workflow': None}



We can set up preprocessing pipeline with default parameters:

```
#example
preproc_dwi.default_setup()
```

    Please indicate directory with atlas volumes:  '/Users/xxie/lab/atlases'
    Please indicate list of selected atlas names:  ['BN_Atlas_246_2mm.nii','DK_atlas86_1mm.nii']


    {'data_dir': 'data', 'sub_list': ['11048'], 'layout': BIDS Layout: ...ers/xxie/lab/pipetography/data | Subjects: 1 | Sessions: 1 | Runs: 0, 'dwi_file': 'sub-{subject_id}/ses-*/dwi/sub-{subject_id}_ses-*_dwi.nii.gz', 'b_files': 'sub-{subject_id}/ses-1/dwi/sub-{subject_id}_ses-1_dwi.bv*', 'sub_template': {'dwi': 'sub-{subject_id}/ses-*/dwi/sub-{subject_id}_ses-*_dwi.nii.gz', 'b_files': 'sub-{subject_id}/ses-1/dwi/sub-{subject_id}_ses-1_dwi.bv*'}, 'sub_source': default_workflow.data_source, 'select_files': default_workflow.select_files, 'bfiles_input': default_workflow.select_bfiles, 'denoise': default_workflow.denoise, 'ringing': default_workflow.ringing_removal, 'ants_bfc': default_workflow.ants_bias_correct, 'mrt_preproc': default_workflow.mrtrix3_preproc, 'atlas_dir': "'/Users/xxie/lab/atlases'", 'atlas_names': ['[', "'", 'B', 'N', '_', 'A', 't', 'l', 'a', 's', '_', '2', '4', '6', '_', '2', 'm', 'm', '.', 'n', 'i', 'i', "'", ',', "'", 'D', 'K', '_', 'a', 't', 'l', 'a', 's', '8', '6', '_', '1', 'm', 'm', '.', 'n', 'i', 'i', "'", ']'], 'atlas_source': default_workflow.atlas_source, 'select_atlas': default_workflow.select_atlases, 'b0extract': default_workflow.dwiextract, 'b0mean': default_workflow.mrmath, 'fsl_bet': default_workflow.brain_extraction, 'linear_coreg': default_workflow.linear_registration, 'nonlinear_coreg': default_workflow.nonlinear_registration, 'datasink': default_workflow.datasink, 'workflow': default_workflow}


Then you can simply connect the pipeline and call `preproc_dwi.draw_pipeline()` to visualize the workflow as a PNG image, or `preproc_dwi.run_pipeline()` to run the default pipeline.

All the default settings may not be optimal for your dataset, run the processing for a test image and see the intermediate results and then tweak the available inputs to improve the output image quality.

Now that our pre-processing Nodes are properly setup, we can connect and create a workflow:

```
#example
preproc_dwi.connect_nodes(wf_name = 'pipetography_workflow')
preproc_dwi.draw_pipeline()
```

Let's take a look at the final workflow we created:

```
#example
from IPython.display import Image
Image('data/derivatives/test_run/pipetography_detailed.png')
```




![png](docs/images/output_17_0.png)



Finally, to run the entire pipeline with our inputs. When we declare `parallel = True`, we are telling Nipype to run parallel pipelines for each iterable input, the pipeline will prompt an input for the number of processes. If you enter `4`, there will be 4 processes taking up your available computing resources:

```
#example
preproc_dwi.run_pipeline(parallel = True)
```
