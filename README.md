# Sparrow-FPGA

This is the Sparrow-FPGA repository, containing code for building and running firmware on a Sparrow board using the CASPER toolflow.

## Software Versions

This repository was designed to use the following software versions:

 - Ubuntu 20.04.6 LTS
 - Python 3.8.10
 - Matlab / Simulink 2021a
 - Vivado / Petalinux 2021.2

## Cloning This Repository

This repository has git submodules tracking necessary CASPER (and other) libraries.

Clone with:

```bash
git clone https://github.com/realtimeradio/sparrow-fpga
cd sparrow-fpga
git submodule init
git submodule update
```

## Building Firmware

### Local configuration

First, copy the local environment configuration file `startsg.local.rtr-dev3` and modify to reflect the installation paths of your software tools.

### Starting Simulink

Start Simulink with

```bash
./startsg startsg.local.rtr-dev3 #replace with the name of your new startsg.local file
```

### Building Firmware

Build firmware using the usual CASPER MATLAB build script, `jasper`.
See the [CASPER documentation](https://casper-toolflow.readthedocs.io) and the [CASPER website](https://casper.berkeley.edu) for more information about using the CASPER tools.
