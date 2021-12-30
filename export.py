import os
import osxphotos

from datetime import datetime, timedelta
from pathlib import Path

from score import *
from sort import *

# Specify the type of exports
EXPORT_TYPE_GPS_COORDS = 'gps'
EXPORT_TYPE_CALENDAR_HEATMAP = 'calendar'
EXPORT_TYPE_CALENDAR_BEST = 'calendar_best'
EXPORT_TYPE_PEOPLE = 'people'

EXPORT_TYPES = [
    EXPORT_TYPE_GPS_COORDS,
    EXPORT_TYPE_CALENDAR_HEATMAP,
    EXPORT_TYPE_CALENDAR_BEST,
    EXPORT_TYPE_PEOPLE,
    'all'
]

def exportGPS(ps: list[osxphotos.PhotoInfo], outdir: str, precision=5):
    """
    Exports gps.csv which contains a list of all GPS coordinates and
    with a precision of 5-decimal places by default -- which is about
    1.1 meters
    """

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

        for coordinate, count in grouping:
            outfile.write(f'{coordinate},{count}\n')
    
    print(f'Done writing GPS coordinates data')


def generateCalendarStats(dated: dict, file='heatmap.csv', verbose=True):
    """
    Writes to a csv file where the first column is date, 
    and the second column is the number of photos taken
    on that date
    """

    with open(file, 'w') as outfile:
        outfile.write('date,num\n')
        for key in sorted(dated.keys()):
            outfile.write(f'{key},{len(dated[key])}\n')

    if verbose: print('Done writing to heatmap.csv')


def exportNamedHeatmap(named: dict, setmindate = None, skipZeroDays=False):

    # Generate name-index map and write to file
    names = sorted(named.keys())
    with open('people_index.csv', 'w') as outfile:
        outfile.write('index,name\n')
        for idx, name in enumerate(names):
            outfile.write(f'{idx},{name}\n')

    # Combine all dates
    dates = set()
    for _, ps in named.items():
        dates |= set(ps.keys())

    dates = sorted(dates)
    if setmindate:
        mindate = setmindate
    else:
        mindate = dates[0]
    maxdate = dates[-1]

    alldates = dict()
    if skipZeroDays:
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

    print(f'mindate: {mindate}, maxdate: {maxdate}, number of days in between: {len(alldates.keys())}')

    # Populate the alldates dict
    for name, dated in named.items():
        # find name index
        index = names.index(name)
        for datekey, photos in dated.items():
            try:
                alldates[datekey][index] = len(photos)
            except KeyError:
                continue
    
    # write to file (2d csv)
    with open('people_data.csv', 'w') as f:

        # Write headers
        f.write(f'date,{",".join([str(i) for i in range(len(names))])}\n')

        # Write data
        for key in sorted(alldates.keys()):
            day_data = alldates[key]
            out_people_data = ['0' if i not in day_data else str(day_data[i]) for i in range(len(names))]
            f.write(f'{key},{",".join(out_people_data)}\n')

def exportScoreInfo(ps: list[osxphotos.PhotoInfo], attr: str, truncate: int,
    export_photos: bool, filter_pics: bool, filter_zero_values: bool):
    """
    Use -1 for truncate to export the entire list and don't truncate the
    sorted results
    """
    # Check that the attribute is valid
    if attr not in SCORE_ATTRIBUTES:
        print(f"Error: no attribute {attr}")
        return None

    sorted_ps = sortByScoreAttribute(ps=ps, attr=attr)

    if (filter_pics):
        video_ext = ['mov', 'mp4', 'avi', 'mpg']
        sorted_ps = list(filter(
            lambda photo: photo.original_filename.split('.')[-1].lower() not in video_ext,
            sorted_ps))
    
    if (filter_zero_values):
        epsilon = 1e-2
        sorted_ps = list(filter(lambda photo: getattr(photo.score, attr) > epsilon, sorted_ps))

    # Make directory
    outdir = f'outdata/score_{attr}'
    outdir_path = Path(outdir)
    try:
        outdir_path.rmdir()
    except OSError as e:
        pass
    Path(outdir).mkdir(parents=True, exist_ok=True)

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

def exportAllScoreInfo(ps: list[osxphotos.PhotoInfo], truncate: int, export_photos: bool, filter_pics: bool, filter_zero_values: bool):
    for scoreAttr in SCORE_ATTRIBUTES.keys():
        print(f'Exporting sorted score attribute {scoreAttr}, truncate={truncate}')
        exportScoreInfo(ps, scoreAttr, truncate, export_photos, filter_pics, filter_zero_values)

def generateDayBestPhotoStats(dated: dict):
    with open('best.csv', 'w') as outfile:
        outfile.write('date,best_score,avg_score,filename\n')
        for key in sorted(dated.keys()):
            if dated[key]:
                avg_score = sum([p.score.overall for p in dated[key]]) / len(dated[key])
                max_score = 0
                filename = ''
                for p in dated[key]:
                    if p.score.overall > max_score:
                        max_score = p.score.overall
                        filename = p.original_filename
                outfile.write(f'{key},{max_score},{avg_score},{filename}\n')
            else:
                outfile.write(f'{key},0,0,\n')
    
    print('Done writing to best.csv')
