#! /usr/bin/env python
import sys
import time
import argparse
import logging
import casperfpga
from sparrow_adc2tge import SparrowAdc2Tge
from matplotlib import pyplot as plt

def run(host, fpgfile,
        plot_samples = None,
        use_pps_trigger=False,
        ):

    logger = logging.getLogger(__file__)
    logger.setLevel(logging.INFO)
    #handler = logging.StreamHandler(sys.stdout)
    #handler.setLevel(logging.INFO)
    #logger.addHandler(handler)

    logger.info("Connecting to board with hostname %s" % host)
    cfpga = casperfpga.CasperFpga(host, transport=casperfpga.KatcpTransport)

    logger.info("Instantiating control object with fpgfile %s" % fpgfile)
    sparrow = SparrowAdc2Tge(cfpga, fpgfile=fpgfile)

    logger.info("Firmware version is %d" % sparrow.get_firmware_version())
    logger.info("Firmware build time: %s" % time.ctime(sparrow.get_build_time()))
    fpga_clock_mhz = sparrow.cfpga.estimate_fpga_clock()
    logger.info("Estimated FPGA clock is %.2f MHz" % fpga_clock_mhz)

    if fpga_clock_mhz < 1:
        raise RuntimeError("FPGA doesn't seem to be clocking correctly")

    c0, c1 = sparrow.get_adc_snapshot(use_pps_trigger=use_pps_trigger)
    plt.plot(c0[0:plot_samples], '-o', label='0')
    plt.plot(c1[0:plot_samples], '-o', label='1')
    plt.xlabel('Sample Number')
    plt.ylabel('ADC value')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Program and initialize a Sparrow ADC->10GbE design',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('host', type=str,
                        help = 'Hostname / IP of Sparrow board')
    parser.add_argument('fpgfile', type=str, 
                        help = '.fpgfile to program or /read')
    parser.add_argument('-n', dest='plot_samples', type=int, default=None,
                        help ='If specified, plot only this number of samples')
    parser.add_argument('--pps', action='store_true',
                        help ='Use this flag to capture samples starting at a PPS edge')

    args = parser.parse_args()
    run(args.host, args.fpgfile,
        plot_samples=args.plot_samples,
        use_pps_trigger=args.pps,
        )
