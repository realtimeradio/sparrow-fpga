# Quick-Start Guide

## Creating a Sparrow OS

  1. Obtain a Sparrow SD card image from [the Sparrow website](https://realtimeradio.co.uk/hardware).
  2. Unzip the image and copy to a micro-SD card using a tool such as `dd`.
  **Take care to ensure you select the appropriate SD card device**, since whatever you choose will be overwritten with the provided image.
  The `lsblk`, and `dmesg | tail` commands (after inserting the SD card into your computer) will help identify your SD card.
  If in doubt, stop and seek assistance!

  An example `dd` command on an Ubuntu OS:

  ```
  SDCARD_DEVICE=/dev/mmcblk0 # Be careful! Whatever device you choose will be wiped!
  IMAGE_FILE = /path/to/sparrow/image.img # Replace with the path to your downlaoded image

  dd if=$IMAGE_FILE of=$SDCARD_DEVICE status=progress
  ```
  3. Eject the micro-SD card from your computer, and plug it into the Sparrow board

## Powering on a Sparrow

  1. Provide DC power to the Sparrow via the barrel jack connector.
  2. Positive voltage should be on the center pin of the connector.

  NB:

    - Acceptable voltage levels are **10V to 25V**
    - Typical power consumption is <20W for large designs, and <10W for small designs.
      Size your power supply appropriately!
    - If a fan is connected, it should start a few seconds after power is applied to Sparrow.
    If it does not, there may be a software boot problem.
    Solve this before using the Sparrow to avoid the potential for overheating!

## Connecting to a Sparrow

  1. Connect the Sparrow's RJ45 port to an Ethernet network, preferably one with a DHCP server.
  2. Apply power to Sparrow and wait ~a minute for the Sparrow to boot.
  3. Connect to the Sparrow using either `casperfpga`, or `ssh`.
  The Sparrow has a default IP address `10.10.11.99/24` and will also obtain a dynamic IP address using DHCP, if provided by a server on the network. The Sparrow's MAC address used for DHCP is indicated on the board/chassis information label.
  The username/password required for an `ssh` connection is `casper`/`casper`.

# How To

## Obtain a Serial Interface

In the event of networking or boot issues, it may be useful to connect to a Sparrow board using a serial UART interface.

  1. Connect a computer to Sparrow's micro-USB-B port.
  2. When your computer detects the two serial interfaces associated with this new connection, connect to the second of these (typically `/dev/ttyUSB1` if using a Linux computer with no other serial devices attached). UART configuration is 115200 baud in `8N1` mode (one start bit, eight data bits, no parity bit, one stop bit).

## Use an external frequency reference 

On boot, a Sparrow will execute the boot script `/home/casper/onboot.sh`.
This script programs the board's Si5332 synthesizer chip.
Modifying the boot script allows the synthesizer to be provided with different configuration files.

Two files are currently provided:

  1. `Si5332-GM1-RevD-SPRW1-XtalIn-25MHzOut.txt` -- Uses the Sparrow's on-board 25 MHz reference. This reference may be disciplined by a White Rabbit network, with appropriate firmware and hardware.
  2. `Si5332-GM1-RevD-SPRW1-10MIn-25MHzOut.txt` -- Uses a 10 MHz reference provided on the Sparrow's `REF_IN` MMCX input.

