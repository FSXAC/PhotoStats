#!/usr/local/bin/python3

# Read the apple photos library and write GPS as csv

import argparse
import http.server
import os
import osxphotos
import socketserver
import sys

# Import our modules
from score import *
from sort import *
from export import *

# Set up arguments
parser = argparse.ArgumentParser(description='PhotoStats by Muchen He -- '\
    'Using OSXPhotos and your macOS Photos library to generate visualizations')

default_library_path = os.path.sep.join([os.environ['HOME'], 'Pictures', 'Photos Library.photoslibrary'])
parser.add_argument('--library', help='Absolute path to the .photoslibrary Photos Library',
default=default_library_path)

# Optional arguments
parser.add_argument('--outdir', help='Output directory for the exported data', default='outdata')
parser.add_argument('--export', help='Specify what kind of data to export', choices=EXPORT_TYPES, default='all')
parser.add_argument('--ignore-hidden', help='Ignore photos that are hidden (in the hidden album)', action='store_true')
parser.add_argument('--serve', help='After exporting, serve the webpages using http.server', action='store_true')

# Export-specific arguments
parser.add_argument('--gps-precision', help='Precision of GPS coordinates in export', type=int, choices=range(2, 7), default=5)

# Parse the arguments
args = parser.parse_args()

def main():
    # Check the path is correct
    if not os.path.exists(args.library):
        parser.print_help()
        print(f'Cannot open Photos library at {args.library}, please specify the absolute ' \
            'path to the Photos library using the --library argument')
        sys.exit(1)

    print(f"Opening photo library at {args.library}, this may take a while.")

    # TEMP

    pd = osxphotos.PhotosDB(args.library)
    ps = pd.photos()
    ps_dated = groupByDate(ps)

    # Filter hidden photos from the list of photos
    if args.ignore_hidden:
        ps = list(filter(lambda photo: not photo.hidden, ps))

    if args.export in ['all', EXPORT_TYPE_GPS_COORDS]:
        exportGPS(ps, args.outdir, args.gps_precision)

    if args.export in ['all', EXPORT_TYPE_CALENDAR_HEATMAP]:
        exportCalendarHeatmap(ps_dated, args.outdir)

    if args.export in ['all', EXPORT_TYPE_PEOPLE]:
        exportPeopleData(ps, args.outdir);

    if args.serve:
        with socketserver.TCPServer(('', 8000), http.server.SimpleHTTPRequestHandler) as httpd:
            print('Serving at http://localhost:8000')
            httpd.serve_forever()


    # Group by date
    # ps_dated = groupByDate(ps)

    # Write stats
    # exportAllScoreInfo(
    #     ps=ps,
    #     truncate=16,
    #     export_photos=True,
    #     filter_pics=False,
    #     filter_zero_values=False)
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
