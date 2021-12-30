#!/usr/local/bin/python3

# Read the apple photos library and write GPS as csv

import osxphotos
from pathlib import Path
import sys
import json
from functools import cmp_to_key

# Import our modules
from score import *
from sort import *
from export import *

def main():
    if len(sys.argv) <= 1:
        print('Please enter the path to the .photoslibrary as an argument')
        exit(1)

    libpath = sys.argv[1]

    print(f"Opening photo library at {libpath}, this may take a while.")
    pd = osxphotos.PhotosDB(libpath)
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
