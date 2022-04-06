SENSOR_PATH = '/sys/bus/iio/devices/iio:device0/'

sensors = [
        'temp0',
        'voltage0_vccint',
        'voltage1_vccaux',
        'voltage2_vccbram',
        'voltage3_vccpint',
        'voltage4_vccpaux',
        'voltage5_vccoddr',
        'voltage6_vrefp',
        'voltage7_vrefn',
        ]

def read_int(fname):
    with open(fname, 'r') as fh:
        s = fh.read()
    return float(s)

for sensor in sensors:
    raw = read_int(SENSOR_PATH + 'in_' + sensor + '_raw')
    scale = read_int(SENSOR_PATH + 'in_' + sensor + '_scale')
    if sensor.startswith('temp'):
        offset = read_int(SENSOR_PATH + 'in_' + sensor + '_offset')
    else:
        offset = 0
    v = scale * (raw + offset) / 1000.
    if sensor.startswith('voltage'):
        name = sensor.split('_', 1)[1]
    else:
        name = sensor
    print('%10s: %.3f' % (name, v))
