# AUTOGENERATED! DO NOT EDIT! File to edit: 03_postprocessing.ipynb (unless otherwise specified).

__all__ = []

# Internal Cell

import os

from nipype import IdentityInterface
from nipype.pipeline import Node, Workflow
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.interfaces.base import CommandLine, CommandLineInputSpec, File, TraitedSpec, traits
from nipype.interfaces.mrtrix3.connectivity import LabelConvert
from nipype.interfaces.mrtrix3.utils import Generate5tt
from nipype.interfaces.mrtrix3.preprocess import ResponseSD
from nipype.interfaces.mrtrix3.reconst import EstimateFOD, ConstrainedSphericalDeconvolution
from nipype.interfaces import ants

# Internal Cell
class tckSIFT2InputSpec(CommandLineInputSpec):
    in_file = File(
        exists=True,
        mandatory=True,
        argstr="%s",
        position=-3,
        desc="input track file"
    )
    in_fod = File(
        exists=True,
        mandatory=True,
        argstr="%s",
        position=-2,
        desc="input image containing the spherical harmonics of the fiber orientation distributions"
    )
    out_file = File(
        mandatory=True,
        argstr="%s",
        desc="output weighting factor for each streamline",
        position=-1
    )
    proc_mask = File(
        exists=True,
        argstr="-proc_mask %s",
        desc="provide an image containing the processing mask weights for the model; image spatial dimensions must match the fixel image"
    )
    act = File(
        exists=True,
        argstr="-act %s",
        desc="use an ACT five-tissue-type segmented anatomical image to derive the processing mask"
    )
    fd_scale_gm = traits.Bool(
        argstr="-fd_scale_gm",
        desc="in conjunction with -act to heuristically downsize the fibre density estimates based on the presence of GM in the voxel. This can assist in reducing tissue interface effects when using a single-tissue deconvolution algorithm"
    )
    nthreads = traits.Int(
        argstr="-nthreads %d",
        desc="number of threads. if zero, the number" " of available cpus will be used",
        nohash=True,
    )
    force = traits.Bool(
        argstr="-force",
        desc="overwrite existing output file"
    )

class tckSIFT2OutputSpec(TraitedSpec):
    out_file=File(argstr="%s", desc="output text file containing the weighting factor for each streamline")

class tckSIFT2(CommandLine):
    """
    Interface with mrtrix3 package
    Spherical-deconvolution informed filtering of tractograms - sift2
    Optimise per-streamline cross-section multipliers to match a whole-brain tractogram to fixel-wise fibre densities
    """
    _cmd="tcksift2"
    input_spec=tckSIFT2InputSpec
    output_spec=tckSIFT2OutputSpec

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs["out_file"] = os.path.abspath(self.inputs.out_file)
        return outputs

# Internal Cell
class MakeConnectomeInputSpec(CommandLineInputSpec):
    """
    Specifying inputs to mrtrix3's tck2connectome
    """
    in_file = File(
        exists=True, mandatory=True, argstr="%s", position=-3, desc="input tck file"
    )
    in_parc = File(
        exists=True, argstr="%s", position=-2, desc="parcellation file"
    )
    out_file = File(
        argstr="%s",
        mandatory=True,
        position=-1,
        desc="output file connectivity csv file",
    )
    nthreads = traits.Int(
        argstr="-nthreads %d",
        desc="number of threads. if zero, the number" " of available cpus will be used",
        nohash=True,
    )
    in_weights = File(
        exists=True,
        argstr="-tck_weights_in %s",
        desc="specify a text scalar file containing the streamline weights",
    )
    scale_length=traits.Bool(
        argstr="-scale_length",
        desc="scale each contribution to the connectome edge by the length of the streamline"
    )
    stat_edge=traits.Enum(
        "sum",
        "mean",
        "min",
        "max",
        argstr="-stat_edge %s",
        desc="statistic for combining the values from all streamlines in an edge into a single scale value for that edge (options are: sum,mean,min,max;default=sum)"
    )
    symmetric=traits.Bool(
        argstr='-symmetric',
        desc='make matrices symmetric'
    )
    zero_diag=traits.Bool(
        argstr='-zero_diagonal',
        desc='set matrix diagonal to zero on output'
    )
    force = traits.Bool(
        argstr='-force',
        desc='overwrite existing output file'
    )

class MakeConnectomeOutputSpec(TraitedSpec):
    out_file = File(argstr="%s", desc="output connectome csv file")

class MakeConnectome(CommandLine):
    """
    mrtrix3's tck2connectome interface, defaults to zero diagonal and symmetric outputs.
    """
    _cmd="tck2connectome"
    input_spec = MakeConnectomeInputSpec
    output_spec = MakeConnectomeOutputSpec

    def _list_outputs(self):
        outputs=self.output_spec().get()
        outputs["out_file"] = os.path.abspath(self.inputs.out_file)
        return outputs