# Sparrow ADC -> 10G Example Design

The Simulink design `sparrow_adc2tge.slx` contains an example firmware design
which captures dual-channel ADC samples, and packages them as a stream of
UDP/IP packets.

## Output format

UDP packet payloads are network- (big-) endian, and comprise a 48-bit timestamp,
which counts samples since the last board synchronisation event (see the
control software's `arm_timestamp_reset()` method), followed by a 16-bit
runtime-configurable header field, followed by 4096 ADC samples.
These samples alternate between the two ADC channels.
ADC data are presented as 16-bit integers, MSB-aligned with the native ADC
samples. I.e., For a 12-bit ADC, the lower 4 bits of the 16-bit values are
always zero.

A simple method to read a packet of data in python is:

```python
import struct
def decode_packet(raw_udp_payload, nsamples):
    """
    parameters:
        raw_udp_payload: The raw UDP payload binary string, obtained from socket.recv()
        nsamples: The number of samples (for each of the two ADC channels) in a packet

    returns:
        t: Packet timestamp (int)
        h: Packet user-defined 16-bit header (int)
        d0: List of samples from ADC channel 0, running from timestamp t to
            timestamp t+n-1
	d1: List of samples from ADC channel 1, running from timestamp t to
            timestamp t+n-1
    """

    # Unpack the header word   
    HEADER_SIZE = 8 # Number of bytes in timestamp
    HEADER_FORMAT = "Q" # Python struct format code (unsigned 64-bit)
    x = struct.unpack(">%s" % HEADER_FORMAT, raw_udp_payload[0:HEADER_SIZE])
    t = (x >> 16) & (2**48 - 1)
    h = x & (2**16 - 1)
    # Unpack the rest of the data as ADC samples
    DATA_FORMAT = "h" # Python struct format code (signed 16-bit)
    # Unpack two ADC channels at once
    data_payload = struct.unpack(">%d%s" % (2*nsamples, DATA_FORMAT), raw_udp_payload[HEADER_SIZE:])
    # De-interleave the two ADC channels
    d0 = data_payload[0::2]
    d1 = data_payload[1::2]

    return t, h, d0, d1
```

## Configuring the design

The Simulink design `sparrow_adc2tge.slx` may be compiled using the tool versions
and `mlib_devel` specified in the top-level README file of this repository.

A pre-compiled binary can be found at `spattow_adc2tge/outputs/`.

## Software

Software in this repository was tested with Python 3.6.9

### Control Library

A control class for the firmware design, `SparrowAdc2Tge` is provided in
`sparrow_adc2tge.py`. This class provides functionality to program, and
configure an ADC->10GbE design on a Sparrow board.

Example usage can be found in the provided initialization script,
`sparrow_adc2tge_init.py`. Also see class docstrings for more infomation.

### Initialization Software

The script `sparrow_adc2tge_init.py` is provided to enable command-line
programming, and configuration, of a Sparrow board.

Usage information can be obtained by running the script with the `-h` or `--help`
flags:

```
(py3-venv) jackh@rtr-dev2:~/src/cfa_digitizer/adc_test$ ./sparrow_adc2tge_init.py -h
usage: sparrow_adc2tge_init.py [-h] [--use_wr_pps] [-s] [--dest_port DEST_PORT]
                             [--dest_ip DEST_IP] [--dest_mac DEST_MAC]
                             [--skipprog] [--source_ip SOURCE_IP]
                             host fpgfile

Program and initialize a Sparrow ADC->10GbE design

positional arguments:
  host                  Hostname / IP of Sparrow board
  fpgfile               .fpgfile to program or /read

optional arguments:
  -h, --help            show this help message and exit
  --use_wr_pps          Use this flag to sync the design from WR PPS pulses
                        (default: False)
  -s                    Use this flag to re-arm the design's sync logic
                        (default: True)
  --dest_port DEST_PORT
                        10GBe destination port (default: 10000)
  --dest_ip DEST_IP     10GBe destination IP address, in dotted-quad notation
                        (default: 10.100.100.1)
  --dest_mac DEST_MAC   10GBe destination IP address, in xx:xx:xx:xx:xx:xx
                        notation (default: a0:48:1c:e0:41:98)
  --skipprog            Skip programming .fpg file (default: False)
  --source_ip SOURCE_IP
                        10GBe Source IP address, in dotted-quad notation
                        (default: 10.100.100.100)
  --header HEADER       16-bit header value to place in 10GbE packets
                        (default: 0)
```

### Grabbing ADC Snapshots

The `sparrow_adc2tge_get_samples.py` script dumps snapshots of 8192 ADC samples
to csv files. Usage is:

```
usage: sparrow_adc2tge_get_samples.py [-h] [-n NSNAPSHOT] [--outfile OUTFILE]
                                      host fpgfile

Dump ADC samples to file

positional arguments:
  host                  Hostname / IP of Sparrow board
  fpgfile               .fpgfile to program or /read

optional arguments:
  -h, --help            show this help message and exit
  -n NSNAPSHOT, --nsnapshot NSNAPSHOT
                        Number of snapshots to write to disk (default: 256)
  --outfile OUTFILE     Record data to file <outfile>.x.data and
                        <outfile>.y.data (default: None)

```

Example: `sparrow_adc2tge_get_samples.py <host> <fpgfile> -n 32 --outfile foo


This will record ADC channel 0 snapshots to a file named `foo.x.data`
and ADC channel 1 snapshots to a file named `foo.y.data`.

The file format is comma-separated integer values, with one line per snapshot.

Generated data files can be plotted with the example script, `plot_data_file.py`.

Usage, as described by the `-h` flag, is:

```
(py3-venv) jackh@rtr-dev2:~/src/cfa_digitizer/adc_test$ ./plot_data_file.py -h
usage: plot_data_file.py [-h] [-n NPACKET] filename

Plot received snapshot files

positional arguments:
  filename              Plot snapshots from filename.x.data and filename.y.data

optional arguments:
  -h, --help            show this help message and exit
  -n NSNAPSHOT, --nsnapshot NPACKET
                        Number of snapshots to plot (default: 1)
```

For example, to plot the first snapshot written to disk from the example
`sparrow_adc2tge_get_samples.py` command:

```
./plot_data_file.py foo -n 1
```

Multiple snapshots can be plotted, though
lines in the data file do not represent contiguous samples.

### Simple Plotting

The script `sparrow_adc2tge_plot_adc.py` provides basic ADC plotting capabilities.
It is assumed the design has been properly initialized prior to running this script.

Usage, as described by the `-h` flag:

```
(casper-python3-venv) jackh@rtr-dev1:~/src/cfa_digitizer/adc_test$ ./sparrow_adc2tge_plot_adc.py -h
usage: sparrow_adc2tge_plot_adc.py [-h] [--skipprog] [-n PLOT_SAMPLES] [--pps]
                                 host fpgfile

Program and initialize a Sparrow ADC->10GbE design

positional arguments:
  host             Hostname / IP of Sparrow board
  fpgfile          .fpgfile to program or /read

optional arguments:
  -h, --help       show this help message and exit
  -n PLOT_SAMPLES  If specified, plot only this number of samples (default:
                   None)
  --pps            Use this flag to capture samples starting at a PPS edge
                   (default: False)

```

The maximum number of time samples which may be plotted is 8192. This is set
by the size of the ADC snapshot buffers in the firmware design.
