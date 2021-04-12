#!/usr/local/bin/python3

# Read the apple photos library and write GPS as csv

import osxphotos
import sys

if len(sys.argv) <= 1:
    print('Please enter the path to the .photoslibrary as an argument')
    exit(1)

libpath = sys.argv[1]

print(f"Opening photo library at {libpath}, this may take a while.")
pd = osxphotos.PhotosDB(libpath)

with open('gps.csv', 'w') as outfile:
    outfile.write('lon,lat,x\n')
    for p in pd.photos():
        loc = p.location
        if loc[0] is not None:
            outfile.write(f'{loc[0]},{loc[1]},1\n')

print('done')
