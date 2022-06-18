import time

import casperfpga

HOST = 'localhost'

SPI_REG = 'sparrow_pll_ctrl'
PSU_REG = 'sparrow_adc_en'

r = casperfpga.CasperFpga(HOST, transport=casperfpga.KatcpTransport)
r.write_int(PSU_REG, 0)
time.sleep(0.1)
r.write_int(PSU_REG, 1)
time.sleep(0.1)

def send_spi(addr, data, rnw=1):
    payload = 0
    payload += ((rnw  & 1) << 31)
    payload += ((addr & (2**6  - 1)) << 25)
    payload += ((data & (2**24 - 1)) << 1)

    r.write_int(SPI_REG, payload, word_offset=1)
    r.write_int(SPI_REG, (0<<8) + (1<<0), word_offset=0) # triggers transaction
    readback = r.read_uint(SPI_REG, word_offset=2) & 0xffffff
    return readback

def read_spi(addr):
    """
    Read value held in register at `address`
    """
    return send_spi(addr, 0, rnw=1)

def write_spi(addr, data):
    """
    Write value `data` to register at `address`
    """
    send_spi(addr, data, rnw=0)

def dump_regs():
    for i in range(0x14):
        print("0x%.2x, 0x%.6x" % (i, read_spi(i)))


def configure():
    print('')
    write_spi(0x00, 0x20)    # RESET command.
    #time.sleep(1)
    write_spi(0x01, 0x02)     # Default = 2.  This value assigns PLL Chip Enable control to the SPI Reg 1[1], 1 enabled, 0 disabled.  To assign PLL CE control to CE pin, write Reg 1[0]=1.
    write_spi(0x02, 0x02)     # Ref Divider Register-Default value = 1h (Rdiv=1). Program as needed.
    
    write_spi(0x05, 0x1628)  # VCO configuration Register. Program this value.    
    write_spi(0x05, 0x60A0)  # VCO configuration Register. Program this value.
    write_spi(0x05, 0xE210)  # VCO output divider = 2 (E110) or = 1 (E090)
    write_spi(0x05, 0x2818)  # Differential output.  For single-ended output, write 2898h;
    #write_spi(0x05, 0x2898)  # Differential output.  For single-ended output, write 2898h;
    #write_spi(0x05, 0xF88)   # magic word enable PLL output
    write_spi(0x05, 0x00)     # Close out VCO register programming by writing Reg 5 = 0.
    
    write_spi(0x06, 0x303CA) # Delta-Sigma Modulator Configuration Register. Int Mode=303CA, Frac Mode=30F4A
      
    write_spi(0x07, 0x14D)   # 14Dh is the default value for LD programming. For different configurations, especially higher PFD rates, this may need to change.
    #write_spi(0x08, 0xC1BEFF)# Default value =C1BEFFh. No need to program.
    #write_spi(0x09, 0x573FFF)# CP Register-Program as needed. 5CBFFFh = 2.54mA CP current with 570uA down CP Offset current.
    write_spi(0x0A, 0x2046) # VCO Tuning Configuration Register-Program this value.
    write_spi(0x0B, 0x7C061)# PFD/CP Control Register-Program this value. 7c061
    write_spi(0x0F, 0x81)   # Default vaue =1. 81h configures LD/SDO pin to output LD status always, except during SPI reads when the pin is automatically mux'ed to output the serial data.
    # Fxtal = 50MHz, Nint = Reg03, Nfrac = Reg04/2^24, R = Reg02, k = 1 here.  Fout = Fxtal*(Nint+Nfrac)/(R*k)
    #time.sleep(1)
    write_spi(0x03, 0x50)    # Integer VCO Divider Register-Program as needed to set frequency. If VCO is div4 and Ref is div2, then Fout = Reg3*50/8 MHz 
    #write_spi(0x04, 0x00)# Fractional VCO Divider Register-Program as needed to set frequency. When this register is written, a VCO auto-cal is initiated.
    
    print('')

dump_regs()
configure()
dump_regs()
