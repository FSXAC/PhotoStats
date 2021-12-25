#!/usr/local/bin/python3

# Read the apple photos library and write GPS as csv

import osxphotos
from pathlib import Path
from datetime import datetime, timedelta
import sys
import json
from functools import cmp_to_key

# Score analysis attributes
SCORE_ATTRIBUTES = [
    'behavioral',
    'curation',
    'failure',
    'harmonious_color',
    'highlight_visibility',
    'immersiveness',
    'interaction',
    'interesting_subject',
    'intrusive_object_presence',
    'lively_color',
    'low_light',
    'noise',
    'overall',
    'pleasant_camera_tilt',
    'pleasant_composition',
    'pleasant_lighting',
    'pleasant_pattern',
    'pleasant_perspective',
    'pleasant_post_processing',
    'pleasant_reflection',
    'pleasant_symmetry',
    'promotion',
    'sharply_focused_subject',
    'tastefully_blurred',
    'well_chosen_subject',
    'well_framed_subject',
    'well_timed_shot',
]

def sortByScoreAttribute(
    ps: list[osxphotos.PhotoInfo],
    attr: str
):
    # Check that the attribute is valid
    if attr not in SCORE_ATTRIBUTES:
        print(f"Error: no attribute {attr}")
        return None

    return sorted(ps, key=lambda photo: getattr(photo.score, attr))

def sortByDate(ps: list[osxphotos.PhotoInfo]):
    """
    This function returns a dictionary where the key is the
    date, and the object is a list of PhotoInfos
    """

    calendarDict = {}
    for photo in ps:
        key = photo.date.strftime('%Y-%m-%d')

        if key not in calendarDict:
            calendarDict[key] = [photo]
        else:
            calendarDict[key].append(photo)

    return calendarDict

def extractGPStoCSV(ps: list[osxphotos.PhotoInfo]):
    """
    Outputs gps.csv which contains a list of all GPS coordinates and
    a gps_coarse.csv which groups the photos to gps coordinates within
    5 decimal places (1.1 m precision)
    """
    with open('gps.csv', 'w') as outfile, open('gps_coarse.csv', 'w') as outfile_coarse:
        outfile.write('latitude,longitude,n\n')
        outfile_coarse.write('latitude,longitude,n\n')
        coarse_group = dict()
        for p in ps:
            loc = p.location
            if loc[0] is not None:
                outfile.write(f'{loc[0]},{loc[1]},1\n')
                coarse_key = f'{round(loc[0], 5)},{round(loc[1], 5)}'
                if coarse_key in coarse_group:
                    coarse_group[coarse_key] += 1
                else:
                    coarse_group[coarse_key] = 1
        for coord, count in coarse_group.items():
            outfile_coarse.write(f'{coord},{count}\n')

    print('Done writing to gps.csv')
    print('Done writing to gps_coarse.csv')

def generateCalendarStats(dated: dict, file = 'heatmap.csv', verbose=True):
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


# This sorts the photos (with tagged faces) into a dictionary of dictionaries:
# {name1: { date1: [photos], date2: [photos]}, name2: ... }
def sortByNameAndDate(ps: list[osxphotos.PhotoInfo]):
    # first we should have a dict of lists
    named = dict()
    
    print('Going through people in photos')
    for photo in ps:
        names = photo.persons
        if len(names) > 0:
            for n in names:
                if n.startswith('_'):
                    continue

                datekey = photo.date.strftime('%Y-%m-%d')
                if n in named:
                    if datekey in named[n]:
                        named[n][datekey].append(photo)
                    else:
                        named[n][datekey] = [photo]
                else:
                    named[n] = {datekey : [photo]}
    return named

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


def exportScoreInfo(ps: list[osxphotos.PhotoInfo], attr: str, truncate=9,
    filter_pics=False, filter_zero_values=False):
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
        sorted_ps = filter(
            lambda photo: photo.original_filename.split('.')[-1].lower() not in video_ext,
            sorted_ps)
    
    if (filter_zero_values):
        sorted_ps = filter(lambda photo: getattr(photo.score, attr) != 0.0, sorted_ps)

    with open(f'score_{attr}.csv', 'w') as outfile:
        outfile.write('photo_file,score\n')

        # Export without truncating
        if 2 * truncate > len(sorted_ps) or truncate == -1:
            out_ps = sorted_ps
        else:
            out_ps = sorted_ps[:truncate] + sorted_ps[len(sorted_ps) - truncate:]
        
        # Write to file
        for p in out_ps:
            outfile.write(f'{p.original_filename},{getattr(p.score, attr)}\n')

def exportAllScoreInfo(ps: list[osxphotos.PhotoInfo], truncate: int, filter_pics: bool, filter_zero_values: bool):
    for scoreAttr in SCORE_ATTRIBUTES:
        print(f'Exporting sorted score attribute {scoreAttr}, truncate={truncate}')
        exportScoreInfo(ps, scoreAttr, truncate)

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
    exportAllScoreInfo(ps, 16, True, True)
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
