#!/bin/env python

'''
This script demonstrates programming an FPGA, configuring 10GbE cores and checking transmitted and received data.

Author: Jason Manley, August 2009.
Modified: Jack Hickish, 2023
'''
import casperfpga, time, struct, sys, logging, socket

#Decide where we're going to send the data, and from which addresses:
base_ip  = 10*(2**24) + 0*(2**16) + 1*(2**8)
mac_base=(2<<40) + (2<<32)

def ip2str(ip):
    a = []
    for i in range(4):
        a += [str((ip >> (8*(3-i))) & 0xff)]
    return '.'.join(a)


pkt_period = 16384  #how often to send another packet in FPGA clocks (100MHz)
payload_len = 128   #how big to make each packet in 64bit words

fabric_port=10000

fpgfile = 'sfp4x_test.fpg'
fpga=[]

if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(
        description = __doc__,
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )

    p.add_argument('-p', '--noprogram', dest='noprogram', action='store_true',
        help='Don\'t reprogram the fpga.')
    p.add_argument('-c', '--noct', action='store_true',
        help='Disable corner turn -- just send packets between pairs of ports.')
    p.add_argument('-n', '--ncores', type=int, default=8,
        help='Number of ethernet cores')  
    p.add_argument('-T', '--period', type=int, default=16384,
        help='How often to send packets (in 100 MHz FPGA clocks)')  
    p.add_argument('-P', '--payload', type=int, default=128,
        help='Payload of each packet (in 64 bit words)')  
    p.add_argument('-a', '--arp', action='store_true',
        help='Print the ARP table and other interesting bits.')  
    p.add_argument('-f', '--fpgfile', type=str, default=fpgfile,
        help='Specify the fpgfile file to load')  
    p.add_argument('host', type=str,
        help='IP of hostname of FPGA board')
    args = p.parse_args()

    print(('Connecting to server %s... '%(args.host)), end=' ')
    fpga = casperfpga.CasperFpga(args.host, transport=casperfpga.KatcpTransport)

    if fpga.is_connected():
        print('ok\n')
    else:
        print('ERROR connecting to server %s.\n'%(args.host))
        exit()

    if not args.noprogram:
        
        print('------------------------')
        print('Programming FPGA...', end=' ')
        sys.stdout.flush()
        fpga.upload_to_ram_and_program(args.fpgfile)
        print('ok')

    # Seemingly we have to call get_system_information
    # here even if we have programmed (which should call it internally).
    # Unclear why this is.
    fpga.get_system_information(args.fpgfile)

    print('---------------------------')    
    print('Disabling output...', end=' ')
    sys.stdout.flush()
    for i in range(args.ncores):
       fpga.write_int('pkt_sim%d_enable'%i, 0)
    print('done')

    print('Resetting cores and counters...', end=' ')
    sys.stdout.flush()
    fpga.write_int('rst', 3)
    fpga.write_int('rst', 0)
    print('done')
    print('---------------------------')    

    sys.stdout.flush()
    for i in range(args.ncores):
        print('Configuring core gbe%d'%i)
        gbe = fpga.gbes['gbe%d' % i]
        gbe.configure_core(mac_base+i,ip2str(base_ip+i),fabric_port)
        for j in range(args.ncores):
            gbe.set_single_arp_entry(ip2str(base_ip+j), mac_base+j)

    print('---------------------------')

    print('Setting-up packet source...', end=' ')
    sys.stdout.flush()
    fpga.write_int('period',args.period)
    fpga.write_int('payload_len',args.payload)
    print('done')
    print('Enable corner turn?', not args.noct)
    fpga.write_int('ct_en', int(not args.noct))

    print('Setting-up destination addresses...', end=' ')
    sys.stdout.flush()
    #fpga.write_int('dest_ip_base',(base_ip>>8)<<5)
    fpga.write_int('dest_ip_base',base_ip)
    fpga.write_int('dest_port',fabric_port)
    print('done')

    print('Enabling output...', end=' ')
    for i in range(args.ncores):
        sys.stdout.flush()
        fpga.write_int('pkt_sim%d_enable'%i, 1)
    print('done')

    fpga.write_int('rst', 4) # resets off, tx enable on
    fpga.write_int('rst', 5) # reset counters again (to get rid of the first rogue crc fail)
    fpga.write_int('rst', 4) # resets off, tx enable on

    fpga_rate = fpga.estimate_fpga_clock()
    print('fpga clock rate: %.2f'%fpga_rate)
    packet_rate = fpga_rate*1e6/args.period
    bit_rate = packet_rate * 64 * (args.payload+1) #plus one because crc is added to the end
    total_bit_rate = packet_rate * (64*(args.payload+1) + 54*8)
    print('Packet rate: %d packets/sec'%packet_rate)
    print('Bit rate: %d bits/sec (%.2fGb/s)'%(bit_rate, bit_rate/1e9))
    print('Bit rate (with overhead): %d bits/sec (%.2fGb/s)'%(total_bit_rate, total_bit_rate/1e9))

    while(True):
        try:
            for i in range(args.ncores):
                sent = fpga.read_int('tx_frame_cnt%d'%i)
                received = fpga.read_int('rx_frame_cnt%d'%i)
                errors = fpga.read_int('rx_frame_err%d'%i)
                txof = fpga.read_int('tx_of%d'%i)
                rxof = fpga.read_int('tx_of%d'%i)
                bad_crc_cnt = fpga.read_int('crc_check%d_bad_cnt'%i)
                tx_minus_rx = fpga.read_int('tx_minus_rx%d'%i)
                print('Core %d, sent %d, received %d, errors %d, bad crcs %d, tx-rx %d, (txof=%d, rxof=%d)'%(i,sent,received,errors,bad_crc_cnt,tx_minus_rx,txof,rxof))
            print('###############################')
            time.sleep(1)

        except KeyboardInterrupt:
            exit()
