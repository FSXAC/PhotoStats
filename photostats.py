#!/usr/local/bin/python3

# Read the apple photos library and write GPS as csv

import argparse
from logging import error
import os
import osxphotos
import sys

# Import our modules
from score import *
from sort import *
from export import *

# Set up arguments
parser = argparse.ArgumentParser(description='PhotoStats by Muchen He -- '\
    'Using OSXPhotos and your macOS Photos library to generate visualizations')

parser.add_argument('--library', help='Absolute path to the .photoslibrary \Photos Library',
default=os.path.join(os.environ['HOME'], 'Photos Library.photoslibrary'))

parser.add_argument('--outdir', help='Output directory for the exported data', default='outdata')
parser.add_argument('--export', help='Specify what kind of data to export', choices=EXPORT_TYPES, default='all')

# Parse the arguments
try:
    args = parser.parse_args()
except:
    parser.print_help()
    sys.exit(1)

def main():
    # Check the path is correct
    if not os.path.exists(args.library):
        parser.print_help()
        print(f'Cannot open Photos library at {args.library}, please specify the absolute ' \
            'path to the Photos library using the --library argument')
        sys.exit(1)

    print(f"Opening photo library at {args.library}, this may take a while.")

    # TEMP
    return

    pd = osxphotos.PhotosDB(args.library)
    ps = pd.photos()

    # Sort by date
    # dated = sortByDate(ps)

    # Write stats
    exportAllScoreInfo(
        ps=ps,
        truncate=16,
        export_photos=True,
        filter_pics=False,
        filter_zero_values=False)
    # extractGPStoCSV(ps)
    # generateCalendarStats(dated)
    # generateDayBestPhotoStats(dated)

    # Todo use the dict like in calendar and sort PhotoInfo by days

    # Todo generate top pictures of the year by looking at their ScoreInfo

    # Todo like heatmap, but also assign the max ScoreInfo.overall to each day

    # ---

    # exportNamedHeatmap(sortByNameAndDate(ps), '2020-01-01', False)



if __name__ == '__main__':
    main()
