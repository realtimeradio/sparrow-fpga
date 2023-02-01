#! /bin/bash

SPARROW_FPGA_PATH=/home/casper/src/sparrow-fpga
SIFILE=Si5332-GM1-RevD-SPRW1-XtalIn-25MHzOut.txt
PYTHON=/home/casper/python3-venv/bin/python

cd $SPARROW_FPGA_PATH
cd adc_tests

echo "Programming Si5332 with $SIFILE"
$PYTHON program_i2c.py $SIFILE > /dev/null

# The following requires that the FPGA be programmed
#echo "Programming LMX"
#python pll_config.py > /dev/null
