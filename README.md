# Pipetography
> Nipype and mrtrix3 based pre-/post- processing pipeline for brain diffusion-MRI and generation of structural connectomes of the brain.


![CI](https://github.com/axiezai/pipetography/workflows/CI/badge.svg)
![docker](https://img.shields.io/docker/v/axiezai/pipetography)

This repo currently only has pre-processing capabilities! More will be added in the near future.

The pre-processing workflow has been updated to reflect what's seen in the optimal [DESIGNER pipeline](http://www.sciencedirect.com/science/article/pii/S1053811918306827) and on [mrtrix3 cloud apps on brainlife.io](https://brainlife.io). 

## Install

Since most usages will be on HPC resources, I <em>highly recommend</em> that you use the `Singularity` or `Docker` recipe in the repository instead of installing the Python module.

#### Singularity:

 - Currently has pathing issues as seen in the singularity issues page: https://github.com/hpcng/singularity/issues/5040, the 3.6 release candidate should fix this... For now, use docker image if you can. If not, the singularity container will not be able to execute freesurfer `recon-all` step of the workflow. All DWI preprocessing steps will work though.
 
 - Obtain the singularity image with `singularity pull docker://axiezai/pipetography:0.2.9a` or `singularity build --remote pipetography.sif docker://axiezai/pipetography:0.2.9a`. The second option allows you to build remotely via Syslabs Cloud, this will require a remote log tokeen in which you can obtain after registering at https://cloud.sylabs.io/builder. 
 
#### Docker:

 - Pull the docker image: `docker pull axiezai/pipetography:0.2.9a`
 
 - Run with BIDS directory and interactive bash terminal: `docker run -v <BIDS_DIR>:<Docker_BIDS_DIR> -it axiezai/pipetography:0.2.8 bash`

Known container issues:
 - Singularity image missing freesurfer path to `nu_correct` as part of `$PATH`. 

 - If `singularity build` fails with `apt-get install` error complaining about unauthenticated packages, add `--allow-unauthenticated` to every `apt-get` line in the `sinngularity.def` file.
 
#### Creating your own environment and install `pipetography` as a Python module:

`pip install pipetography`

Since `pipetography` is a `Nipype` wrapper around `mrtrix3`, `ANTs`, and `FSL`, you have to follow their installation instructions and set them up appropriately on your machine as well:    
 - [mrtrix3 v3.0.0](https://mrtrix.readthedocs.io/en/latest/installation/before_install.html)
 
 - [ANTs](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS)
     
 - [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
 
 - [Freesurfer v6.0](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)
 
 - [Matlab Run Time Compiler for freesurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/MatlabRuntime)
 

## The pipeline:

Currently supports acquisitions with no reverse phase encoding (`-rpe_none`)  and reverse phase encoding in all DWI directions (`-rpe_all`) options.
