#!/usr/bin/env python
import argparse
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description='Plot received snapshot files',
             formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('filename', type=str, default=None,
                    help='Plot snapshots from filename.x.data and filename.y.data')
parser.add_argument('-n', '--nsnapshot', type=int, default=1,
                    help='Number of snapshots to plot')
args = parser.parse_args()

fhx = open("%s.x.data" % args.filename, "r")
fhy = open("%s.y.data" % args.filename, "r")

for line in range(args.nsnapshot):
    xd = list(map(int, fhx.readline().split(',')))
    yd = list(map(int, fhy.readline().split(',')))
    plt.plot(xd, '-o', label="X%d" % line)
    plt.plot(yd, '-o', label="Y%d" % line)
plt.legend()
plt.show()
