# Pipetography
> Nipype and mrtrix3 based pre-/post- processing pipeline for brain diffusion-MRI and generation of structural connectomes of the brain.


![CI](https://github.com/axiezai/pipetography/workflows/CI/badge.svg)
![docker](https://img.shields.io/docker/v/axiezai/pipetography)

This repo currently only has pre-processing capabilities! More will be added in the near future.

The pre-processing workflow has been updated to reflect what's seen in the optimal [DESIGNER pipeline](http://www.sciencedirect.com/science/article/pii/S1053811918306827) and on [mrtrix3 cloud apps on brainlife.io](https://brainlife.io). 

## Install

Since most usages will be on HPC resources, I <em>highly recommend</em> that you use the `Singularity` or `Docker` recipe in the repository instead of installing the Python module.

 - To build singularity image: `singularity build -s pipetography.simg singularity.def`

 - Run singularity image with: `singularity run pipetography.simg` (You will have to bind your data directories in addition to just `singularity run`)

#### Creating your own environment and install `pipetography` as a Python module:

`pip install pipetography`

Since `pipetography` is a `Nipype` wrapper around `mrtrix3`, `ANTs`, and `FSL`, you have to follow their installation instructions and set them up appropriately on your machine as well:    
 - [mrtrix3 v3.0.0](https://mrtrix.readthedocs.io/en/latest/installation/before_install.html)
 
 - [ANTs](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS)
     
 - [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
 
 - [Freesurfer v6.0](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)
 
 - [Matlab Run Time Compiler for freesurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/MatlabRuntime)
 

The pipeline visualized:
---

The following pipeline is produced by running the default set up in [pipeline](https://axiezai.github.io/pipetography/pipeline/). And each individual node in the workflow is shown in [core](https://axiezai.github.io/pipetography/core/).

```python
#example
from IPython.display import Image
Image('/Users/xxie/sample_data/derivatives/pipetography/pipetography_detailed.png')
```




![png](docs/images/output_5_0.png)


