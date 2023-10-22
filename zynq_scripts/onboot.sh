#! /bin/bash

SPARROW_FPGA_PATH=/home/casper/src/sparrow-fpga
# Use this PLL configuration to clock from the on-board 25 MHz crystal
# (This can be disciplined by White Rabbit, or left free-running)
SIFILE=Si5332-GM1-RevD-SPRW1-XtalIn-25MHzOut.txt
# Use this PLL configuration to lock to an external 10 MHz on the REF IN port
#SIFILE=Si5332-GM1-RevD-SPRW1-10MIn-25MHzOut.txt
PYTHON=/home/casper/python3-venv/bin/python

echo "Enabling fan"
/usr/sbin/i2cset -y 0 0x74 0x3f

cd $SPARROW_FPGA_PATH
cd firmware/adc_tests

echo "Programming Si5332 with $SIFILE"
$PYTHON program_i2c.py $SIFILE > /dev/null

# The following requires that the FPGA be programmed
#echo "Programming LMX"
#python pll_config.py > /dev/null
