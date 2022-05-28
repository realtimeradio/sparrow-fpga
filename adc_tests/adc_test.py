from time import sleep
from struct import unpack
import numpy as np


class Ads5404():
    nbits = 12
    _reg_delay_ctrl = 'ads5404_delay_ctrl'
    _reg_delay_val = 'ads5404_delay_val'
    _reg_rst = 'ads5404_hardware_rst'
    _reg_pll_lock = 'ads5404_pll_lock'
    _reg_spi = 'ads5404_spi_controller'
    def __init__(self, cfpga):
        self.cfpga = cfpga

    def _get_regname(self, reg):
        return reg

    def enable_readback(self):
        self.write_spi(0, 1<<15)

    def _send_spi(self, addr, data, rnw=1):
        payload = 0
        payload += ((rnw & 0x1) << 23)
        payload += ((addr & 0x7f) << 16)
        payload += ((data & 0xffff))
        spi_reg = self._get_regname(self._reg_spi)
        cs = 0xff00
        self.cfpga.write_int(spi_reg, payload, word_offset=1)
        self.cfpga.write_int(spi_reg, cs, word_offset=0) # triggers transaction
        return self.cfpga.read_uint(spi_reg, word_offset=2)

    def write_spi(self, addr, data):
        self._send_spi(addr, data, rnw=0)

    def read_spi(self, addr):
        return self._send_spi(addr, 0, rnw=1) & 0xffff

    def hw_reset(self):
        self.cfpga.write_int(self._get_regname(self._reg_rst), 0)
        sleep(0.001)
        self.cfpga.write_int(self._get_regname(self._reg_rst), 1)
        sleep(0.001)
        self.cfpga.write_int(self._get_regname(self._reg_rst), 0)

    def chip_rst(self):
        self.cfpga.write_int(self._get_regname(self._reg_rst), 0)
        sleep(0.001)
        self.cfpga.write_int(self._get_regname(self._reg_rst), 2)
        sleep(0.001)
        self.cfpga.write_int(self._get_regname(self._reg_rst), 0)

    def strobe_mode(self):
        self.write_spi(0x01, 0x0)
        self.write_spi(0x3C, 0x9554)
        self.write_spi(0x3D, 0x2AA8)
        self.write_spi(0x3E, 0x1554)

    def data_mode(self):
        self.write_spi(0x01, 0x01)
        self.write_spi(0x3C, 0x0)
        self.write_spi(0x3D, 0x0)
        self.write_spi(0x3E, 0x0)

    def increment_delay(self, n):
        self.cfpga.write_int(self._get_regname(self._reg_delay_val), 0xffff)
        for i in range(n):
            self.cfpga.write_int(self._get_regname(self._reg_delay_ctrl), 0)
            self.cfpga.write_int(self._get_regname(self._reg_delay_ctrl), 0xffff)

    def decrement_delay(self, n):
        self.cfpga.write_int(self._get_regname(self._reg_delay_val), 0x0)
        for i in range(n):
            self.cfpga.write_int(self._get_regname(self._reg_delay_ctrl), 0)
            self.cfpga.write_int(self._get_regname(self._reg_delay_ctrl), 0xffffffff)

    def set_delay(self, n):
        self.cfpga.write_int(self._get_regname(self._reg_delay_val), n)
        self.cfpga.write_int(self._get_regname(self._reg_delay_ctrl), 0)
        self.cfpga.write_int(self._get_regname(self._reg_delay_ctrl), 0xffffffff)
        self.cfpga.write_int(self._get_regname(self._reg_delay_ctrl), 0)

    def test_strobe(self, d, bitwise=False):
        A = 0xfaaa
        B = 0x0555
        if not bitwise:
            errcnt = 0
            for i in range(len(d)-1):
                if d[i] == A:
                    if d[i+1] != B:
                        errcnt += 1
                elif d[i] == B:
                    if d[i+1] != A:
                        errcnt += 1
                else:
                    errcnt += 1
            return errcnt == 0
        else:
            errcnt = [0 for _ in range(self.nbits)]
            for b in range(self.nbits):
                for i in range(len(d)-1):
                    if (((d[i] >> b) & 1) + ((d[i+1] >> b) & 1)) != 1:
                        errcnt[b] += 1
            return errcnt

    def get_pll_lock(self):
        return self.cfpga.read_int(self._get_regname(self._reg_pll_lock))


def get_data(r, signed=True):
    if signed:
        fmt = 'h'
    else:
        fmt = 'H'
    x, _ = r.snapshots.snapshot0.read_raw(man_trig=True)
    d0 = np.array(unpack('>%d%s' % (x['length']//2, fmt), x['data']))
    x, _ = r.snapshots.snapshot1.read_raw(man_trig=True)
    d1 = np.array(unpack('>%d%s' % (x['length']//2, fmt), x['data']))
    return d0, d1

def scan_delays(a):
    a.strobe_mode()
    for i in range(64):
        a.set_delay(i)
        d0, d1 = get_data(a.cfpga, signed=False)
        err0 = a.test_strobe(d0)
        err1 = a.test_strobe(d1)
        print(i, err0, err1)
