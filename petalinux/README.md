# Building Linux with petalinux

## Software Versions

These steps were tested using petalinux 2021.2

## Build Process

1. Create petalinux project
```
petalinux-create --type project --template zynq --name sparrow-linux
```

2. Configure project based on `.xsa` file exported by Vivado
```
petalinux-config --get-hw-description=</PATH/TO/XSA/DIRECTORY>
```

3. Set some custom options
```
DTG Settings --> template --> zedboard
AUTO Hardware Settings -> Ethernet Settings --> MAC Address [make blank]
AUTO Hardware Settings -> Serial Settings --> FSBL/DTG Serial --> [ps7_uart_0]
Image Packaging Configuration --> Root filesystem type --> EXT4
FPGA Manager --> [Enable]
```

4. Copy custom device tree
```
cp system-user.dtsi sparrow-linux/project-spec/meta-user/recipes-bsp/device-tree/files/system-user.dtsi
```

5. Build
```
petalinux-build
```

6. Package binaries
```
petalinux-package --boot --fsbl images/linux/zynq_fsbl.elf --fpga images/linux/system.bit --u-boot
```

7. Copy to SD card
```
cp images/linux/BOOT.BIN </path/to/SD/boot/partition>
cp images/linux/images.ub </path/to/SD/boot/partition>
cp images/linux/boot.scr </path/to/SD/boot/partition>
```

## Notes / TODOs

 - To start the fan at maximum speed, use the u-boot commands `i2c dev 0 && i2c mw 0x74 0x0.0 0x3f 0x1`
