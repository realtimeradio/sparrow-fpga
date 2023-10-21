import time
import adf435x

OUT_FREQ = 400. # MHz
REF_FREQ = 25   # MHz

class Adf4351():
    _ctrl_reg = 'sparrow_pll_ctrl'
    def __init__(self, cfpga, ref_freq=REF_FREQ, out_freq=OUT_FREQ):
        self.cfpga = cfpga
        self.ref_freq = ref_freq
        self.out_freq = out_freq

    def configure(self):
        regs = self.get_regs()
        for reg in regs[::-1]: # Program registers in order 5,4,3,2,1,0
            self.write_reg(reg)

    def get_regs(self):
        INT, MOD, FRAC, output_divider, band_select_clock_divider = \
                adf435x.calculate_regs(freq=self.out_freq, ref_freq=self.ref_freq)
        regs = adf435x.make_regs(INT=INT, MOD=MOD, FRAC=FRAC,
                output_divider=output_divider,
                aux_output_select=adf435x.AuxOutputSelect.Fundamental,
                aux_output_enable=False,
                band_select_clock_divider=band_select_clock_divider)
        return regs

    def write_reg(self, x):
        self.cfpga.write_int(self._ctrl_reg, x, word_offset=1) # data
        active_cs = 0
        inactive_cs = 1
        self.cfpga.write_int(self._ctrl_reg,
                (inactive_cs<<8) + (active_cs<<0), word_offset=0)
