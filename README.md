# Sparrow-FPGA

This is the Sparrow-FPGA repository, containing code for building and running firmware on a Sparrow board using the CASPER toolflow.

For more information about the Sparrow platform, including schematics, and OS image, see the [Sparrow website](https://realtimeradio.co.uk/hardware).

## Software Versions

This repository was designed to use the following software versions:

 - Ubuntu 20.04.6 LTS
 - Python 3.8.10
 - Matlab / Simulink 2021a
 - Vivado 2021.2
 - Petalinux 2021.2 (only required if building a new Linux OS)

## Cloning This Repository

This repository has git submodules tracking necessary CASPER (and other) libraries.

Clone with:

```bash
git clone https://github.com/realtimeradio/sparrow-fpga
cd sparrow-fpga
git submodule init
git submodule update
```

## Repository Layout

  1. `docs/`: Basic Sparrow documentation. See, also, [the Sparrow website](https://realtimeradio.co.uk/hardware).
  2. `firmware/`: Directory containing simulink firmware source and related libraries and control scripts.
  3. `petalinux/`: Directory containing Petalinux build configurations and instructions.
  4. `zynq_scripts/`: Directory containing scripts intended to be run on the Sparrow Zynq ARM CPU.

## Building Firmware

### Local configuration

  1. Navigate to the `firmware/` directory.
  2. Copy the local environment configuration file `startsg.local.rtr-dev3` and modify to reflect the installation paths of your software tools.

### Starting Simulink

Start Simulink with

```bash
./startsg startsg.local.rtr-dev3 #replace with the name of your new startsg.local file
```

### Compiling Firmware

This repository contains two simple models.

  1. `adc_tests/sparrow_adc2tge.slx`: A model which digitizes two analog inputs and outputs data over 10GbE.
  2. `tge_tests/sfp4x_test.slx`: A model which tests 10GbE interfaces by transmitting data over loopback interfaces.

These models can be opened in Simulink and built using the usual CASPER MATLAB build script, `jasper`.
See the [CASPER documentation](https://casper-toolflow.readthedocs.io) and the [CASPER website](https://casper.berkeley.edu) for more information about using the CASPER tools.

Altenatively, a build script is provided which tweak the target FPGA and build an fpg file.

To build the ADC design for FPGA model `xc7z030`, in the MATLAB prompt:

```matlab
filename = 'adc_tests/sparrow_adc2tge.slx';
fpga = 'xc7z030';

build_model(filename, fpga);
```

Allowed options for `filename` are:

  - `'adc_tests/sparrow_adc2tge.slx'`
  - `'tge_tests/sfp4x_test.slx'`

Allowed options for `fpga` are:

  - `'xc7z030'`
  - `'xc7z035'`
  - `'xc7z045'`

The build script will create a new model, with `_<fpga>` appended to the input model's filename, and build this using the CASPER flow.

A similar MATLAB script, `generate_model`, is also provided. This will simply create the fpga-specific model, but not compile it.
