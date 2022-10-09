import os
import struct
import numpy as np
import ads5404

# Design register names
ETH_NAMES = ["tge0", "tge1"]
PACKETIZER_NAMES = ["packetize0", "packetize1"]
SS_NAME = "ss_adc"

def str2ip(ip):
	iplist = list(map(int, ip.split('.')))
	ipint = 0
	for i in range(4):
		ipint += (iplist[i] << (8*(3-i)))
	return ipint

class SparrowAdc2Tge():
	def __init__(self, cfpga, fpgfile=None):
		"""
		Constuctor for SparrowAdc2Tge control instance.

		:param cfpga: CasperFpga instance for Sparrow board connection
		:type cfpga: casperfpga.Casperfpga

		:param fpgfile: .fpg file to associate with running firmware. If
			none is provided, certain methods will be unavailable until
			either `program_fpga` or `read_fpgfile` are called.
		:type fpgfile: str
		"""
		self.cfpga = cfpga
		self.adc = ads5404.Ads5404(cfpga)
		self.fpgfile = None
		if fpgfile is not None:
			self.read_fpgfile(fpgfile)

	def initialize_adc(self):
		"""
		Initialize ADC interface.
		"""
		self.adc.chip_reset()
		self.adc.hw_reset()
		self.adc.enable_readback()
		self.adc.init()
		self.sync_adc()

	def sync_adc(self):
		"""
		Send a sync pulse to the ADC
		"""
		self.cfpga.write_int("sync", 0)
		self.cfpga.write_int("sync", 1)
		self.cfpga.write_int("sync", 0)

	def get_adc_temp(self):
		"""
		Get ADC temperature.

		:return: temerature in degrees C
		:rtype: int
		"""
		return self.adc.get_temp()

	def read_fpgfile(self, fpgfile):
		"""
		Associate running firmware with give .fpg file.
		This does _not_ program the FPGA. For that, use `program_fpga()`.
		This is a shortcut to casperfpga's get_system_information.

		:param fpgfile: .fpg file to read
		:type fpgfile: str
		"""
		if not os.path.isfile(fpgfile):
				raise RuntimeError("%s is not a file" % fpgfile)
		self.fpgfile = fpgfile
		try:
			self.cfpga.get_system_information(fpgfile)
		except:
			print("Could not process fpgfile %s. Maybe the FPGA is not programmed yet?" % fpgfile)

	def get_build_time(self):
		"""
		Get Unix time of firmware build.

		:return: UNIX time in seconds since UNIX epoch.
		:rtype: int
		"""
		return self.cfpga.read_uint("build_time")

	def get_firmware_version(self):
		"""
		Get firmware version.

		:return: Firmware version number
		:rtype: int
		"""
		return self.cfpga.read_uint("version")

	def program_fpga(self, fpgfile=None):
		"""
		Program the FPGA with the provided fpgfile,
		or self.fpgfile if none is provided.

		:param fpgfile: .fpg file to program. If None, the fpgfile
			provided at instantiation time will be programmed.
		:type fpgfile: str
		"""
		self.fpgfile = fpgfile or self.fpgfile
		if self.fpgfile is None:
			raise RuntimeError("Don't know what .fpg file to program!")
		self.cfpga.upload_to_ram_and_program(self.fpgfile)

	def arm_timestamp_reset(self):
		"""
		Reset timestamp counters on next PPS.
		"""
		self.cfpga.write_int("arm_time_reset", 0) # posedge sensitive
		self.cfpga.write_int("arm_time_reset", 1)
		self.cfpga.write_int("arm_time_reset", 0)

	def get_wr_pps_count(self):
		"""
		Get the number of White Rabbit PPS ticks
		since board programming.

		:return: PPS count
		:rtype: int
		"""
		return self.cfpga.read_uint("pps_wr_cnt")

	def get_sw_pps_count(self):
		"""
		Get the number of Software PPS ticks
		since board programming.

		:return: PPS count
		:rtype: int
		"""
		return self.cfpga.read_uint("pps_sw_cnt")

	def get_pps_count(self):
		"""
		Get the number of PPS ticks registered by the
		DSP pipeline since board programming. These may
		be White Rabbit or software PPS ticks, as defined
		by `set_pps_source()`

		:return: PPS count
		:rtype: int
		"""
		return self.cfpga.read_uint("pps_cnt")

	def set_pps_source(self, source="sw"):
		"""
		Set the DSP pipeline PPS source to either
		"sw" (use software generated PPS ticks, issued with
		`issue_sw_pps()`) or "wr" (use White Rabbit generated
		PPS ticks.

		:param source: "wr" for White Rabbit PPS, or "sw" for
			software PPS.
		:type source: str
		"""
		if not source in ["sw", "wr"]:
			raise ValueError("`source` argument should be 'sw' or 'wr'")
		if source == "sw":
			self.cfpga.write_int("pps_use_wr", 0)
		elif source == "wr":
			self.cfpga.write_int("pps_use_wr", 1)
		else:
			raise ValueError

	def issue_sw_pps(self):
		"""
		Issue a software PPS trigger. This will only
		be fed into the DSP pipeline if `set_pps_source` is
		set to "sw"
		"""
		self.cfpga.write_int("sw_pps", 0) # signal responds to posedge
		self.cfpga.write_int("sw_pps", 1)
		self.cfpga.write_int("sw_pps", 0)

	def get_adc_snapshot(self, use_pps_trigger=False):
		"""
		Get a snapshot of ADC samples simultaneously captured from
		both ADC channels.

		:param use_pps_trigger: If True, use the DSP pipeline's PPS trigger to
			start capture. Otherwise, capture immediately.
		:type use_pps_trigger: bool

		:return: x, y; a pair of numpy arrays containing a snapshot of ADC
			samples from ADC channel 0 and 1, respectively.
		:rtype: (numpy.ndarray, numpy.ndarray)
		"""
		if not SS_NAME in self.cfpga.snapshots.keys():
			raise RuntimeError("%s not found in design. Have you provided an appropriate .fpg file?" % SS_NAME)
		ss = self.cfpga.snapshots[SS_NAME]
		d, t = ss.read_raw(man_trig=not use_pps_trigger)	
		v = np.array(struct.unpack(">%dh" % (d["length"]//2), d["data"]))
		x = v[0::2]
		y = v[1::2]
		return x, y

	def get_spectra(self, nacc):
		"""
		Get an accumulated power spectrum based on ADC snapshots.

		:param nacc: Number of snapshots to accumulate
		:type nacc: int

		:return: X, Y; pair of numpy arrays containing accumulated power spectra
			for ADC channels 0 and 1, respectively.
		:rtype: (numpy.ndarray, numpy.ndarray)
		"""
		Xacc = None
		Yacc = None
		for i in range(nacc):
			x, y = self.get_adc_snapshot(use_pps_trigger=False)
			X = np.fft.rfft(x)
			Y = np.fft.rfft(y)
			if Xacc is None:
				Xacc = X
			else:
				Xacc += X
			if Yacc is None:
				Yacc = Y
			else:
				Yacc += Y
		return X, Y

	def reset_adc_overflow(self):
		"""
		Reset ADC overflow counters.
		"""
		self.write_int("ovr_rst", 1)
		self.write_int("ovr_rst", 0)

	def get_adc_overflow_count(self, adc_id):
		"""
		Get the number of ADC overflow events since
		programming (or last call of `reset_adc_overflow`)

		:param adc_id: ADC ID (0 or 1)
		:type adc_id: int

		:return: Overflow count
		:rtype: int
		"""
		if not adc_id in [0, 1]:
			raise ValueError("adc_id must be 0 or 1")
		return self.read_uint("overrange%d" % adc_id)

	def set_packet_dest(self, ip, mac, port=10000):
		"""
		Set destination IP/port/MAC for UDP packets.

		:param ip: Destination IP in dotted-quad notation (e.g. "10.0.0.1")
		:type ip: str

		:param mac: Destination MAC address
		:type mac: int

		:param port: Destination UDP port
		:type port: int
		"""
		try:
			ipint = str2ip(ip)
		except:
			raise ValueError("Failed to convert %s to IP integer" % ip)

		for eth_name in ETH_NAMES:
			core = eth_name + "_eth"
			if not core in self.cfpga.gbes.keys():
				raise RuntimeError("%s not found in design. Have you provided an appropriate .fpg file?" % core)

			eth = self.cfpga.gbes[core]	
			eth.set_single_arp_entry(ip, mac) # must be IP _string_ here

			self.cfpga.write_int("%s_dest_ip" % eth_name, ipint)
			self.cfpga.write_int("%s_dest_port" % eth_name, port)
		

	def eth_reset(self):
		"""
		Reset the 10G Ethernet core. Requires running `eth_enable` to
		re-enable transmission after reset.
		"""
		self.eth_disable()
		for eth_name in ETH_NAMES:
				self.cfpga.write_int("%s_rst" % eth_name, 1)
				self.cfpga.write_int("%s_rst" % eth_name, 0)

	def eth_enable(self):
		"""
		Enable 10GbE transmission.
		"""
		for eth_name in ETH_NAMES:
				self.cfpga.write_int("%s_en" % eth_name, 1)

	def eth_disable(self):
		"""
		Disable 10GbE transmission.
		"""
		for eth_name in ETH_NAMES:
				self.cfpga.write_int("%s_en" % eth_name, 0)

	def eth_configure(self, ip, port=10000):
		"""
		Configure source IP of the 10GbE port.
		Should be on the same /24 subnet as the intended destination.
		MAC address of the source is automatically set to
		02:02:<IP ADDRESS>.
		If there are multiple ethernet cores in the design, they
		will be given sequential IP addresses, starting at `ip`.

		:param ip: Source IP in dotted-quad notation (e.g. "10.0.0.1")
		:type ip: str

		:param port: Source UDP port
		:type port: int
		"""
		try:
			ipint = str2ip(ip)
		except:
			raise ValueError("Failed to convert %s to IP integer" % ip)
		macint = 0x020200000000 + ipint

		for en, eth_name in enumerate(ETH_NAMES):
				core = eth_name + "_eth"
				if not core in self.cfpga.gbes.keys():
					raise RuntimeError("%s not found in design. Have you provided an appropriate .fpg file?" % core)
				
				eth = self.cfpga.gbes[core]	
				eth.configure_core(macint + en, ipint + en, port)

	def set_header_field(self, v):
		"""
		Set the 16-bit software-defined packet header field to `v`.

		:param v: Value to which header field should be set.
		:type v: int
		"""
		assert v >= 0, "Header value must be >= 0"
		assert v < 2**16, "Header value must be < 2^16"
		for packetizer_name in PACKETIZER_NAMES:
			self.cfpga.write_int("%s_header" % packetizer_name, v)
