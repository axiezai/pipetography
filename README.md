# Pipetography
> Nipype and mrtrix3 based pre-/post- processing pipeline for brain diffusion-MRI and generation of structural connectomes of the brain.


![CI](https://github.com/axiezai/pipetography/workflows/CI/badge.svg)
![docker](https://img.shields.io/docker/v/axiezai/pipetography)

This repo currently only has pre-processing capabilities! More will be added in the near future.

The pre-processing workflow has been updated to reflect what's seen in the optimal [DESIGNER pipeline](http://www.sciencedirect.com/science/article/pii/S1053811918306827) and on [mrtrix3 cloud apps on brainlife.io](https://brainlife.io). 

## Install

Since most usages will be on HPC resources, I <em>highly recommend</em> that you use the `Singularity` definition file in the repository instead of installing the Python module.

#### Singularity:
 
 - This is a large image, you will need to set the following environment variables to somewhere other than `/tmp` if you want to avoid memory errors:
     - `export SINGULARITY_TMPDIR={YOUR DESTINATION DIR}`
     - `export SINGULARITY_LOCALCACHEDIR={YOUR DESTINATION DIR}`
     - `export SINGULARITY_CACHEDIR={YOUR DESTINATION DIR}`
     - `export SINGULARITY_PULLFOLDER={YOUR DESTINATION DIR}`
     
 - Build the singularity image with the `singularity.def` file provided in Github, you will need to have sudo permissions to perform singularity build. If you run into memory problems, consider building as a sandbox at first with the `-s` flag. 
     - `sudo singularity build {image_file_name}.sif singularity.def`
     
 - OR pull the built singularity image from cloud library:
    - `singularity pull --arch amd64 library://axiezai/pipetography/pipetography:0.3.4`
 
 - To run interactively or as a job execution, you will need a few flags:
     - `-e` for a clean environnment
     - `-B` to bind your freesurfer license file to the image, as well as data/code directories.
     - `singularity shell -e -B <freesurfer_license_path>:/license.txt -B <BIDS_DIR>:<SINGULARITY_BIDS_DIR> {Path to singularity .sif}`
     - Once inside the singularity shell, confirm the license file is recognized as a environment variable. Or declare it with:
         - `export FS_LICENSE="/license.txt"`
     - Sometimes Freesurfer set-up doesn't run as container entry-point. 
         - Fix with `source /opt/freesurfer-7.1.0/SetUpFreeSurfer.sh`
      
#### Creating your own environment and install `pipetography` as a Python module:

`pip install pipetography`

Since `pipetography` is a `Nipype` wrapper around `mrtrix3`, `ANTs`, and `FSL`, you have to follow their installation instructions and set them up appropriately on your machine as well:    
 - [mrtrix3 v3.0.0](https://mrtrix.readthedocs.io/en/latest/installation/before_install.html)
 
 - [ANTs](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS)
     
 - [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
 
 - [Freesurfer v7.1.0](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)
 
 - [Matlab Run Time Compiler for freesurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/MatlabRuntime)
 
Everything listed in this section is included in the singularity container.

## The pipeline:

Currently supports acquisitions with no reverse phase encoding (`-rpe_none`)  and reverse phase encoding in all DWI directions (`-rpe_all`) options.
