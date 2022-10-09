#!/usr/bin/env python

import logging
import argparse
import casperfpga
from sparrow_adc2tge import SparrowAdc2Tge
                                                                                                                                                                                         
def main(host, fpgfile, nsnapshot, outfile):
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.INFO)
    #handler = logging.StreamHandler(sys.stdout)
    #handler.setLevel(logging.INFO)
    #logger.addHandler(handler)
    
    logger.info("Connecting to board with hostname %s" % host)
    cfpga = casperfpga.CasperFpga(host, transport=casperfpga.KatcpTransport)
    
    logger.info("Instantiating control object with fpgfile %s" % fpgfile)
    sparrow = SparrowAdc2Tge(cfpga, fpgfile=fpgfile)
    
    if outfile is not None:
        logger.info("Opening data files %s.[x|y].data" % outfile)
        fhx = open("%s.x.data" % outfile, "w")
        fhy = open("%s.y.data" % outfile, "w")
    else:
        logger.error("Please specify an output file with --outfile")
        exit()
    
    for i in range(nsnapshot):
        if i % 10 == 0:
            logger.info("Capturing snapshot %d of %d" % (i+1, nsnapshot))
        x, y = sparrow.get_adc_snapshot()
        fhx.write("%s\n" % (",".join(["%d" % v for v in x])))
        fhy.write("%s\n" % (",".join(["%d" % v for v in y])))
    
    fhx.close()
    fhy.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dump ADC samples to file',
                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('host', type=str,
                            help = 'Hostname / IP of Sparrow board')
    parser.add_argument('fpgfile', type=str, 
                            help = '.fpgfile to program or /read')
    parser.add_argument('-n', '--nsnapshot', type=int, default=256,
                        help='Number of snapshots to write to disk')
    parser.add_argument('--outfile', type=str, default=None,
                        help='Record data to file <outfile>.x.data and <outfile>.y.data')
    args = parser.parse_args()

    main(args.host, args.fpgfile, args.nsnapshot, args.outfile)
