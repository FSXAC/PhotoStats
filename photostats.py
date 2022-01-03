#!/usr/local/bin/python3

# Read the apple photos library and write GPS as csv

import argparse
import http.server
import json
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
parser.add_argument('--include-hidden', help='Include photos that are hidden (in the hidden album)', action='store_true')
parser.add_argument('--only-hidden', help='Only process photos that are hidden (in the hidden album)', action='store_true')
parser.add_argument('--include-videos', help='Include videos and gifs', action='store_true')
parser.add_argument('--only-videos', help='Onlly process videos and gifs', action='store_true')
parser.add_argument('--serve', help='After exporting, serve the webpages using http.server', action='store_true')
parser.add_argument('--force-export', help='Override skipping export certain data', action='store_true')

# Export-specific arguments
parser.add_argument('--gps-precision', help='Precision of GPS coordinates in export', type=int, choices=range(2, 7), default=5)
parser.add_argument('--best-photo-score-thres', help='Threshold score for export of best daily photos', type=float, default=0.8)

# Parse the arguments
args = parser.parse_args()

def checkArgs(args):
    def failIf(cond:bool, msg:str):
        if cond:
            print(msg)
            parser.print_usage()
            sys.exit(1)

    failIf(args.include_hidden and args.only_hidden, 'Error: --include-hidden and --only-hidden cannot be used at the same time')
    failIf(args.include_videos and args.only_videos, 'Error: --include-videos and --only-videos cannot be used at the same time')

def main():
    # Check the path is correct
    if not os.path.exists(args.library):
        parser.print_help()
        print(f'Cannot open Photos library at {args.library}, please specify the absolute ' \
            'path to the Photos library using the --library argument')
        sys.exit(1)

    # Check if arguments make sense
    checkArgs(args)

    print(f"Opening photo library at {args.library}, this may take a while.")

    # Create a metadata file to speedthings up by not duplicating exports
    metadata_filepath = os.path.join(args.outdir, 'metadata.json')
    metadata = {}

    if os.path.exists(metadata_filepath) and not args.force_export:
        print('Metadata file detected, modified timestamp will be compared to reduce redundant export; use --force-export to override')
        with open(metadata_filepath, 'r') as metadata_file:
            metadata = json.load(metadata_file)
    else:
        metadata = {'library_last_modified': os.path.getmtime(args.library)}

    with open(metadata_filepath, 'w') as metadata_outfile:
        json.dump(metadata, metadata_outfile)

    # TEMP
    # return

    pd = osxphotos.PhotosDB(args.library)
    ps = pd.photos()

    video_exts = ['mov', 'mp4', 'avi', 'mpg', 'mpeg', 'gif']

    if args.only_videos:
        len_prev = len(ps)
        ps = list(filter(lambda photo: photo.original_filename.split('.')[-1].lower() in video_exts, ps))
        print(f'Filtering for only videos; number of items went from {len_prev} to {len(ps)}')
    elif not args.include_videos:
        len_prev = len(ps)
        ps = list(filter(lambda photo: photo.original_filename.split('.')[-1].lower() not in video_exts, ps))
        print(f'Filtering videos; number of items went from {len_prev} to {len(ps)}')


    # Filter hidden photos from the list of photos
    if args.only_hidden:
        len_prev = len(ps)
        ps = list(filter(lambda photo: photo.hidden, ps))
        print(f'Filtering for only hidden content; number of items went from {len_prev} to {len(ps)}')
    elif not args.include_hidden:
        len_prev = len(ps)
        ps = list(filter(lambda photo: not photo.hidden, ps))
        print(f'Filtering hidden content; number of items went from {len_prev} to {len(ps)}')
    
    # Create date-grouped photo lists
    ps_dated = groupByDate(ps)

    if args.export in ['all', EXPORT_TYPE_GPS_COORDS]:
        exportGPS(ps, args.outdir, args.gps_precision)

    if args.export in ['all', EXPORT_TYPE_CALENDAR_HEATMAP]:
        exportCalendarHeatmap(ps_dated, args.outdir)

    if args.export in ['all', EXPORT_TYPE_PEOPLE]:
        exportPeopleData(ps, args.outdir);

    if args.export in ['all', EXPORT_TYPE_BEST_DAILY]:
        exportBestDailyPhoto(ps_dated, args.outdir, export_photos=False, export_score_threshold=args.best_photo_score_thres)

    if args.serve:
        with socketserver.TCPServer(('', 8000), http.server.SimpleHTTPRequestHandler) as httpd:
            print('Serving at http://localhost:8000')
            httpd.serve_forever()

if __name__ == '__main__':
    main()
