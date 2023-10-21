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
    _reg_power = 'sparrow_adc_en'
    def __init__(self, cfpga):
        self.cfpga = cfpga

    def _get_regname(self, reg):
        return reg

    def power_enable(self):
        self.cfpga.write_int(self._get_regname(self._reg_power), 1)
        sleep(0.1)

    def power_disable(self):
        self.cfpga.write_int(self._get_regname(self._reg_power), 0)

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

    def chip_reset(self):
        self.cfpga.write_int(self._get_regname(self._reg_rst), 0)
        sleep(0.001)
        self.cfpga.write_int(self._get_regname(self._reg_rst), 2)
        sleep(0.001)
        self.cfpga.write_int(self._get_regname(self._reg_rst), 0)

    def init(self):
        self.write_spi(0x00, 0x8000) # 4 bit SPI
        self.write_spi(0x3A, 0x0E1B) # Internal 100 ohm LVDS termination
        self.write_spi(0x66, 0x2FFF) # Disable output buffers on unused chan A pins and connected syncout
        self.write_spi(0x67, 0x2FFF) # Disable output buffers on unused chan B pins and N/C syncout
        self.write_spi(0x01, 0x8202) # Corr enable; HP; 2's complement
        self.write_spi(0x03, 0x4B18) # clear core cal chan A
        self.write_spi(0x1A, 0x4B18) # clear core cal chan B
        self.write_spi(0x03, 0x0B18) # enable core cal chan A
        self.write_spi(0x1A, 0x0B18) # enable core cal chan B

    def get_temp(self):
        return self.read_spi(0x2B)

    def toggle_mode(self, pattern_type=0, pattern=[0x0, 0x1, 0x2]):
        assert pattern_type in [0, 1, 2]
        self.write_spi(0x01, 0x0)
        if pattern_type == 0:
            self.write_spi(0x3C, 0x9554)
            self.write_spi(0x3D, 0x2AA8)
            self.write_spi(0x3E, 0x1554)
        elif pattern_type == 1:
            self.write_spi(0x3C, 0xBFFC)
            self.write_spi(0x3D, 0x0)
            self.write_spi(0x3E, 0x3FFC)
        elif pattern_type == 2:
            self.write_spi(0x3C, (1<<15) + (pattern[0]<<2))
            self.write_spi(0x3D, (0<<15) + (pattern[1]<<2))
            self.write_spi(0x3E, (0<<15) + (pattern[2]<<2))
        

    def data_mode(self):
        self.write_spi(0x01, 0x2)
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
        return self.cfpga.read_int(self._get_regname(self._reg_pll_lock)) & 1

    def get_adc_clock_rates(self):
        dt = 0.1
        raw0 = self.cfpga.read_int(self._get_regname(self._reg_pll_lock))
        sleep(dt)
        raw1 = self.cfpga.read_int(self._get_regname(self._reg_pll_lock))
        raw0 = raw0 >> 1
        raw1 = raw1 >> 1
        t0b = raw0 & (2**15 - 1)
        t1b = raw1 & (2**15 - 1)
        t0a = (raw0 >> 15) & (2**15 - 1)
        t1a = (raw1 >> 15) & (2**15 - 1)
        if t0a > t1a:
            t1a += 2**15
        if t0b > t1b:
            t1b += 2**15
        # Firmware counts in increments of 1024 clocks
        fa_mhz = (t1a - t0a) / dt / 1e6 * 1024
        fb_mhz = (t1b - t0b) / dt / 1e6 * 1024
        return fa_mhz, fb_mhz


def get_data(r, signed=True):
    if signed:
        fmt = 'h'
    else:
        fmt = 'H'
    r.snapshots.snapshot0.arm() # Arms both
    x, _ = r.snapshots.snapshot0.read_raw(arm=False)
    d0 = np.array(unpack('>%d%s' % (x['length']//2, fmt), x['data'])) // 2**4
    x, _ = r.snapshots.snapshot1.read_raw(arm=False)
    d1 = np.array(unpack('>%d%s' % (x['length']//2, fmt), x['data'])) // 2**4
    return d0, d1

def scan_delays(a):
    a.toggle_mode()
    for i in range(32):
        a.set_delay(i)
        d0, d1 = get_data(a.cfpga, signed=False)
        err0 = a.test_strobe(d0, bitwise=True)
        err1 = a.test_strobe(d1, bitwise=True)
        print(i, err0, err1)
