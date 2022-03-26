import time

import casperfpga

HOST = '10.0.0.53'

SPI_REG = 'sparrow_pll_ctrl'
PSU_REG = 'sparrow_adc_en'

r = casperfpga.CasperFpga(HOST, transport=casperfpga.KatcpTransport)
r.write_int(PSU_REG, 0)
time.sleep(1)
r.write_int(PSU_REG, 1)

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
    return send_spi(addr, 0, rnw=1)

def write_spi(addr, data):
    send_spi(addr, data, rnw=0)

def dump_regs():
    for i in range(0x14):
        print("0x%.2x, 0x%.6x" % (i, read_spi(i)))

def reset():
    write_spi(0x0, 1<<5)
    write_spi(0x0, 0)

def configure(fref=50., refdiv=1, fout=400,):
    # Theory of operation.
    # Output is integer divisor of fvco
    # fout = fvco / k
    # fvco is determined by divided input reference and Nint Nfrac dividers
    # fvco = (fref / refdiv) * (Nint + Nfrac)

    # Constraints
    # k = 1..62
    # Nint 20..524284 (written to reg 0x03)
    # Nfrac 0.0 ... 0.9999... (register value 0x04 / 2**24)
    
    # TODO: find out best fvco freqs
    # For now, target 2GHz
    k = int(2000 / fout)
    assert k >= 1
    assert k <= 62
    fvco_target = fout * k
    print('k: %f' % k)
    print('fout: %f' % fout)
    print('fvco target: %f' % fvco_target)
    n = int(fvco_target * refdiv / fref) # Use integer only mode for now
    print('n: %f' % n)
    assert n >= 20
    assert n <= 524284
    fvco_actual = fref / refdiv * n
    fout_actual = fvco_actual / k
    df = fout - fout_actual
    print('Actual freq output: %f (%.3f MHz from commanded)' % (fout_actual, df))
    # Now actually configure
    # defaults which the data sheet says aren't appropriate for the HMC830
    write_spi(0x0b, 0xfc061)
    # 1. Set reference divider
    assert refdiv == 1 # else we need to mess with (at least) bit3 of Reg 0x08
    write_spi(0x02, refdiv)
    # 2. Configure the delta-sigma modulator (reg 0x06)
    v = 0
    v += 0xC0 # Use integer mode
    v += (0x07 << 8) # integer mode + defaults
    v += (0x23 << 16) # defaults
    write_spi(0x06, v)
    # 3. Charge Pump register (reg 0x09)
    v = 0x0bcf3c # From example
    write_spi(0x09, v)
    # 4. VCO configuration (indirect via reg 0x05)
    # copy from example
    write_spi(0x05, 0xe80d)
    write_spi(0x05, 0x8b95)
    write_spi(0x05, 0xd11d)
    write_spi(0x05, 0x5)
    # 5. Frequency dividers
    write_spi(0x03, n)
    # write_spi(0x04, ...) # for fractional mode

def test_50_in_450_out():
    write_spi(0x02, 1) #refdiv
    write_spi(0x06, 0x2003ca)
    write_spi(0x07, 0xccd)
    write_spi(0x0A, 0x2046)
    write_spi(0x0B, 0x7c061)
    write_spi(0x0F, 0x81)

    cp = 127
    cp += (127 << 7)
    cp += (103 << 14)
    cp += (0 << 21)
    cp += (0 << 22)
    cp += (0 << 22)
    write_spi(0x09, cp)

    write_spi(0x05, 0x1628)
    write_spi(0x05, 0x60A0)
    v = 6
    v += (3 << 6)
    v += (0 << 8)
    
    w = 0
    w += (2 << 3)
    w += (v << 7)
    write_spi(0x05, w)
    write_spi(0x05, 0x0)


reset()
dump_regs()
#configure()
test_50_in_450_out()
dump_regs()
