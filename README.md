# Pipetography
> Nipype and mrtrix3 based pre-/post- processing pipeline for brain diffusion-MRI and generation of structural connectomes of the brain.


This file will become your README and also the index of your documentation.

## Install

`pip install pipetography`

Since `pipetography` is a `Nipype` wrapper around `mrtrix3`, `ANTs`, and `FSL`, you have to follow their installation instructions:    
 - [mrtrix3](https://mrtrix.readthedocs.io/en/latest/installation/before_install.html)
 
 - [ANTs](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS)
     
 - [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)

## How to use

#### Use as connected Nipype nodes for DWI preprocessing
Nipype wraps the tasks into Nodes and connects them into an automated workflow that can run parallel tasks, the preprocessing workflow includes several functions, some of which require user inputs. We will go over them here, first we need to provide where our subject files are, we recommend using BIDS format subject directories, from which we can create a `layout` with `PyBIDS`:

```
import os, sys


data_dir = 'data'
sub_list = get_subs(data_dir) # this gets all subjects in BIDS directory. For each subject, we need to iterate over all available sessions.

# we only have 1 subject for the sample dataset
```
