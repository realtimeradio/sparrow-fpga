# 10GbE Loopback tests

This model loops back multple SFP+ interfaces and transmits and receives packets with checksums.
Lost or corrupted packets are counted.

To test:

 1. Connect 10GbE cables between SFP+ ports 0 <--> 2, and 1 <--> 3
 2. Execute the test script, configured for 4 SFP ports

  ```
  python sfp_test.py -f sfp4x_test_xc7z035/outputs/sfp4x_test_xc7z035_2023-10-22_1349.fpg -n 4 --noct -P 128 -T 135 10.10.10.12
  ```

  Be sure to provide an `fpg` file targetting the correct FPGA.
  Data rate can be varied with the `-P` and `-T` parameters.
  The former sets the payload size, in multiples of 8 bytes.
  The latter sets how often a packet is transmitted in 100 MHz clock ticks.
  The example above will yield a data rate of ~6 Gb/s on each interface.

 3. Monitor the link for error stats. If things are working, the CRC error count should remain at 0, and the "missing" packet count,
    `tx-rx` should hover around zero. It may not always be exactly zero since sometimes packets may be in transit when the counters are polled.
    A set of working links will yield results like:

    ```
    (py3-venv) jackh@rtr-dev3:~/src/sparrow-fpga/firmware/tge_tests$ python sfp_test.py -f sfp4x_test_xc7z035/outputs/sfp4x_test_xc7z035_2023-10-22_1419.fpg -n 4 --noct -P 128 -T 135 10.10.10.124
    Connecting to server 10.10.10.124...  ok
    
    ------------------------
    Programming FPGA... ok
    ---------------------------
    Disabling output... done
    Resetting cores and counters... done
    ---------------------------
    Configuring core gbe0
    Configuring core gbe1
    Configuring core gbe2
    Configuring core gbe3
    ---------------------------
    Setting-up packet source... done
    Enable corner turn? False
    Setting-up destination addresses... done
    Enabling output... done
    fpga clock rate: 100.16
    Packet rate: 741962 packets/sec
    Bit rate: 6125645243 bits/sec (6.13Gb/s)
    Bit rate (with overhead): 6446173192 bits/sec (6.45Gb/s)
    Core 0, sent 1486223, received 1486988, errors 0, bad crcs 0, tx-rx 1, (txof=0, rxof=0)
    Core 1, sent 1491383, received 1492047, errors 0, bad crcs 0, tx-rx 1, (txof=0, rxof=0)
    Core 2, sent 1496240, received 1496945, errors 0, bad crcs 0, tx-rx 0, (txof=0, rxof=0)
    Core 3, sent 1500819, received 1501456, errors 0, bad crcs 0, tx-rx 0, (txof=0, rxof=0)
    ###############################
    Core 0, sent 2246431, received 2247269, errors 0, bad crcs 0, tx-rx 0, (txof=0, rxof=0)
    Core 1, sent 2251369, received 2252018, errors 0, bad crcs 0, tx-rx 1, (txof=0, rxof=0)
    Core 2, sent 2255927, received 2256625, errors 0, bad crcs 0, tx-rx 1, (txof=0, rxof=0)
    Core 3, sent 2260665, received 2261298, errors 0, bad crcs 0, tx-rx 0, (txof=0, rxof=0)
    ###############################
    Core 0, sent 3006390, received 3007253, errors 0, bad crcs 0, tx-rx 0, (txof=0, rxof=0)
    Core 1, sent 3011548, received 3012185, errors 0, bad crcs 0, tx-rx 1, (txof=0, rxof=0)
    Core 2, sent 3016137, received 3016770, errors 0, bad crcs 0, tx-rx 1, (txof=0, rxof=0)
    Core 3, sent 3020562, received 3021207, errors 0, bad crcs 0, tx-rx 0, (txof=0, rxof=0)
    ###############################
    Core 0, sent 3766836, received 3767806, errors 0, bad crcs 0, tx-rx 1, (txof=0, rxof=0)
    Core 1, sent 3771988, received 3772865, errors 0, bad crcs 0, tx-rx 1, (txof=0, rxof=0)
    Core 2, sent 3777275, received 3777905, errors 0, bad crcs 0, tx-rx 1, (txof=0, rxof=0)
    Core 3, sent 3782205, received 3782864, errors 0, bad crcs 0, tx-rx 0, (txof=0, rxof=0)
    ###############################

    ```
  
