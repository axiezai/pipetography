# Pipetography
> Nipype and mrtrix3 based pre-/post- processing pipeline for brain diffusion-MRI and generation of structural connectomes of the brain.


This file will become your README and also the index of your documentation.

## Install

This pip install function doesn't work yet! Don't do it! It will work with the first release!
`pip install pipetography`

Since `pipetography` is a `Nipype` wrapper around `mrtrix3`, `ANTs`, and `FSL`, you have to follow their installation instructions:    
 - [mrtrix3](https://mrtrix.readthedocs.io/en/latest/installation/before_install.html)
 
 - [ANTs](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS)
     
 - [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)

## How to use

#### Use as connected Nipype nodes for DWI preprocessing
We will wrap all of our tasks in `Nipype`'s `Nodes`

Nipype wraps the tasks into Nodes and connects them into an automated workflow that can run parallel tasks, the preprocessing workflow includes several functions, some of which require user inputs. We will go over them here, first we need to provide where our subject files are, we recommend using BIDS format subject directories, from which we can create a `layout` with `PyBIDS`:

```
import os, sys

data_dir = 'data'
sub_list = get_subs(data_dir) # this gets all subjects in BIDS directory. For each subject, we need to iterate over all available sessions.
print(sub_list)
# we only have 1 subject for the sample dataset
```

    Creating layout of data directory, might take a while if there are a lot of subjects
    ['11048']


#### Subject data I/O:

We need to use `Nipype`'s `IdentityInterface` and `SelectFiles` functionalities to iterable over subjects. The `iterables` function in `Nipype` can expand your workflow to each subject:

```
from nipype import IdentityInterface
from nipype.pipeline import Node
from nipype.interfaces.io import SelectFiles

# IdentityInterface allows us to work with strings as input parameters
sub_source = Node(IdentityInterface(fields = ['subject_id']), name = 'infosource')
sub_source.iterables = [('subject_id', sub_list)]

# Node for selecting files, we need to create a template to tell it what the file paths look like:
dwi_file = os.path.join('sub-{subject_id}', 'ses-*', 'dwi', 'sub-{subject_id}_ses-*_dwi.nii.gz')
bv_files = os.path.join('sub-{subject_id}', 'ses-1', 'dwi', 'sub-{subject_id}_ses-1_dwi.bv*')
templates = {'dwi': dwi_file, 'bvs': bv_files}
# then create Node:
selectfiles = Node(SelectFiles(templates, base_directory = data_dir), name ='selectfiles')
```

We need to also build `Nodes` that grabs `bvec` and `bval` files for our inputs:

```
from nipype import Function

bvspath_getter = Node(Function(input_names=['in_List'],output_names=['out_path'], function = bfiles2tuple), name = 'BV_Getter')
```

Lastly, we need to create an input `Node` for atlases! We use atlases to identify regions of interests (ROIs) after co-registering them onto our DWI images. For this example, we will use the Desikan-Killiany and Brainnectome atlases:

```
atlas_dir = 'atlases'

atlas_template = {'atlas': atlas_dir + '{file_name}'}
atlas_list = ['BN_Atlas_246_2mm.nii','DK_atlas86_1mm.nii'] # list of atlases you want to use
atlas_file = Node(SelectFiles(atlas_template), name = 'select_atlas')
atlas_file.base_directory = atlas_dir
```

#### Preprocessing of DWI:

Now we can finally start our first step: denoise!

We will do this with `mrtrix3`'s `dwidenoise` function after wrapping it in a `MapNode`, these are Nodes that can handle several inputs/outputs with iterables:

```
denoise = MapNode(dwidenoise(), name = "denoise", iterfield = 'in_file')
denoise.inputs.out_file = "denoised.nii.gz"
denoise.inputs.noise = "noise.nii.gz"
denoise.inputs.force = "-force" # in case there's previous outputs, we want to overwrite
```
