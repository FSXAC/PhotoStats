import json
import os
import osxphotos
import sys

from datetime import datetime, timedelta

from score import *
from sort import *
from util import *

# Specify the type of exports
EXPORT_TYPE_GPS_COORDS = 'gps'
EXPORT_TYPE_CALENDAR_HEATMAP = 'calendar'
EXPORT_TYPE_CALENDAR_BEST = 'calendar_best'
EXPORT_TYPE_PEOPLE = 'people'
EXPORT_TYPE_BEST_DAILY = 'best_daily'

EXPORT_TYPES = [
    EXPORT_TYPE_GPS_COORDS,
    EXPORT_TYPE_CALENDAR_HEATMAP,
    EXPORT_TYPE_CALENDAR_BEST,
    EXPORT_TYPE_PEOPLE,
    EXPORT_TYPE_BEST_DAILY,
    'all'
]

def checkSkippable(outdir:str, type:str):
    """
    Checks the metadata for timestamp to see if this type of export
    can be skipped; if not, also update the new timestamp
    """
    metadata_filepath = os.path.join(outdir, 'metadata.json')
    if os.path.exists(metadata_filepath):

        metadata = {}
        with open(metadata_filepath, 'r') as metadata_file:
            metadata = json.load(metadata_file)
        
        if metadata:
            library_timestamp = metadata['library_last_modified']

            if type in metadata and metadata[type] == library_timestamp:
                # Skip
                return True
            else:

                # Update new timestamp and don't skip
                metadata[type] = library_timestamp
                with open(metadata_filepath, 'w') as metadata_outfile:
                    json.dump(metadata, metadata_outfile)

                return False
        else:
            print("Error: metadata not available")
            sys.exit(1)
    else:
        # This shouldn't happen because a metadata file should've been populated at init time
        print("Error: missing metadata file")
        sys.exit(1)

def exportGPS(ps:list[osxphotos.PhotoInfo], outdir:str, precision:int=5):
    """
    Exports gps.csv which contains a list of all GPS coordinates and
    with a precision of 5-decimal places by default -- which is about
    1.1 meters
    """

    if checkSkippable(outdir, 'gps'):
        print('Photos library did not change; skipping GPS data export')
        return

    outfile_path = os.path.join(outdir, 'gps.csv')
    print(f'Exporting GPS data to {outfile_path} with {5} decimal places for coordinates precision')

    with open(outfile_path, 'w') as outfile:
        outfile.write('latitude,longitude,n\n')
        grouping = dict()

        for photo in ps:
            photo_location = photo.location

            # Ignore all photos that don't have location
            # TODO: profile to see if "filter" the array beforehand is faster?
            if photo_location[0] is not None:
                grouping_key = f'{round(photo_location[0], precision)},{round(photo_location[1], precision)}'
                if grouping_key in grouping:
                    grouping[grouping_key] += 1
                else:
                    grouping[grouping_key] = 1

        for coordinate, count in grouping.items():
            outfile.write(f'{coordinate},{count}\n')
    
    print(f'Done writing GPS coordinates data')


def exportCalendarHeatmap(ps_dated:dict[str,list[osxphotos.PhotoInfo]], outdir:str):
    """
    Exports calendar_heatmap.csv where each row contains a data and number of
    photos taken on that day, this csv file will be used in the web view
    """

    if checkSkippable(outdir, 'calendar_heatmap'):
        print('Photos library did not change; skipping calendar heatmap data export')
        return

    outfile_path = os.path.join(outdir, 'calendar_heatmap.csv')
    print(f'Exporting calendar heatmap data to {outfile_path}')

    with open(outfile_path, 'w') as outfile:
        outfile.write('date,num\n')
        for key in sorted(ps_dated.keys()):
            outfile.write(f'{key},{len(ps_dated[key])}\n')

    print(f'Done writing calendar heatmap data')


def exportPeopleData(ps:list[osxphotos.PhotoInfo], outdir:str, startdate=None, skipzerodays=False):
    """
    Export a csv file with occurances of people throughout the dates
    """

    if checkSkippable(outdir, 'people'):
        print('Photos library did not change; skipping people data export')
        return

    # Group by name and then date
    grouped = groupByNameAndDate(ps)

    # Get all names
    names = sorted(grouped.keys())

    # Combine all dates
    dates_set = set()
    for _, photos in grouped.items():
        dates_set |= set(photos.keys())
    dates = sorted(list(dates_set))

    # Truncate to starting date
    if startdate:
        mindate = startdate
    else:
        mindate = dates[0]
    maxdate = dates[-1]

    # Skip days where no one shows up; otherwise, add dates
    alldates = dict()
    if skipzerodays:
        for d in dates:
            alldates[d] = {}
    else:
        start = datetime.strptime(mindate, '%Y-%m-%d')
        end = datetime.strptime(maxdate, '%Y-%m-%d')
        delta = timedelta(days=1)

        # Set up a dict with all the days
        while start <= end:
            alldates[start.strftime('%Y-%m-%d')] = {}
            start += delta

    # Populate the alldates dict
    for name, dated in grouped.items():
        # find name index
        index = names.index(name)
        for datekey, photos in dated.items():
            try:
                alldates[datekey][index] = len(photos)
            except KeyError:
                continue

    # Write to file
    outfile_path = os.path.join(outdir, 'people_data.csv')
    print(f'Exporting people data to {outfile_path}')

    with open(outfile_path, 'w') as outfile:

        # Write headers
        outfile.write(f'date,{",".join(names)}\n')

        # Write data
        for key in sorted(alldates.keys()):
            day_data = alldates[key]
            out_people_data = ['0' if i not in day_data else str(day_data[i]) for i in range(len(names))]
            outfile.write(f'{key},{",".join(out_people_data)}\n')

    print("Done exporting people data.")


def exportBestDailyPhoto(ps_dated:dict[str,list[osxphotos.PhotoInfo]], outdir:str, export_photos:bool, export_score_threshold:float):

    if checkSkippable(outdir, 'best_daily'):
        print('Photos library did not change; skipping best daily photo export')
        return

    outfile_path = os.path.join(outdir, 'best_daily.csv')
    print(f'Exporting best photos data to {outfile_path}')

    if export_photos:
        outfile_photos_path = os.path.join(outdir, 'best_daily')
        createFolder(outfile_photos_path)
        print(f'Will export best photos to {outfile_photos_path}')

        export_list: list[osxphotos.PhotoInfo] = list()

    # Export csv file
    with open(outfile_path, 'w') as outfile:

        # Write header
        outfile.write('date,best_score,avg_score,filename\n')

        # Write data
        for key in sorted(ps_dated.keys()):
            if ps_dated[key]:
                avg_score = sum([p.score.overall for p in ps_dated[key]]) / len(ps_dated[key])
                max_score = 0
                filename = ''
                best_p = None

                for p in ps_dated[key]:
                    if p.score.overall > max_score:
                        max_score = p.score.overall
                        filename = p.original_filename
                        best_p = p

                # There is a case where none of the photos has score > 0
                # in which case, just skip the day
                if not filename:
                    continue

                outfile.write(f'{key},{max_score},{avg_score},{filename}\n')

                # Also save photo to file (if enabled)
                if export_photos and best_p and max_score > export_score_threshold:
                    export_list.append(best_p)
    
    print('Done writing to best.csv')

    if (export_photos):
        print(f'Exporting {len(export_list)} items with scores over {export_score_threshold * 100}%')
        for p in export_list:
            p.export2(
                outfile_photos_path,
                p.original_filename,
            )
        print('Done exporting best photos')


def exportScoreInfo(ps: list[osxphotos.PhotoInfo], attr: str, truncate: int,
    export_photos: bool, filter_zero_values: bool):
    """
    Use -1 for truncate to export the entire list and don't truncate the
    sorted results
    """
    # Check that the attribute is valid
    if attr not in SCORE_ATTRIBUTES:
        print(f"Error: no attribute {attr}")
        return None

    sorted_ps = sortByScoreAttribute(ps=ps, attr=attr)
    
    if (filter_zero_values):
        epsilon = 1e-2
        sorted_ps = list(filter(lambda photo: getattr(photo.score, attr) > epsilon, sorted_ps))

    # Make directory
    createFolder(f'outdata/score_{attr}')

    with open(f'{outdir}/data.csv', 'w') as outfile:
        outfile.write('photo_file,score\n')

        # Export without truncating
        if SCORE_ATTRIBUTES[attr] == ScoreAttrType.Max:
            out_ps = sorted_ps[:truncate]
        elif SCORE_ATTRIBUTES[attr] == ScoreAttrType.Min:
            out_ps = sorted_ps[len(sorted_ps) - truncate:]
        else:
            out_ps = sorted_ps[:truncate] + sorted_ps[len(sorted_ps) - truncate:]
        
        # Write to file
        for p in out_ps:
            outfile.write(f'{p.original_filename},{getattr(p.score, attr)}\n')

        # Export photos
        if export_photos:
            if truncate != -1:
                counter = 1
                for p in out_ps:
                    p.export(outdir, f'{counter}-{p.original_filename}', use_photos_export=True)
                    counter += 1
            else:
                print('Photo libray too big, did not export')

def exportAllScoreInfo(ps: list[osxphotos.PhotoInfo], truncate: int, export_photos: bool, filter_zero_values: bool):
    for scoreAttr in SCORE_ATTRIBUTES.keys():
        print(f'Exporting sorted score attribute {scoreAttr}, truncate={truncate}')
        exportScoreInfo(ps, scoreAttr, truncate, export_photos, filter_zero_values)
