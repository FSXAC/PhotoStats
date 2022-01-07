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
EXPORT_TYPE_PEOPLE_REL = 'people_relationship'
EXPORT_TYPE_BEST_DAILY = 'best_daily'
EXPORT_TYPE_INTERESTING_STATS = 'stats'

EXPORT_TYPES = [
    EXPORT_TYPE_GPS_COORDS,
    EXPORT_TYPE_CALENDAR_HEATMAP,
    EXPORT_TYPE_CALENDAR_BEST,
    EXPORT_TYPE_PEOPLE,
    EXPORT_TYPE_PEOPLE_REL,
    EXPORT_TYPE_BEST_DAILY,
    EXPORT_TYPE_INTERESTING_STATS,
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

def exportInterestingData(pd:osxphotos.PhotosDB, outdir:str):
    """
    Export all kinds of statistical data, useful for creating things
    similar to Spotify-wrapped
    """

    data = dict()

    # Get a new list of photos
    ps = pd.photos()
    data['num_photos'] = len(ps)
    data["total_size_mbyte"] = round(sum([p.original_filesize for p in ps]) / 1e6, 1)

    # Persons stats (pd.persons_as_dict should be sorted already)
    data['num_persons'] = len(pd.persons) - 1
    persons_dict = pd.persons_as_dict
    persons_dict.pop('_UNKNOWN_')
    data['num_faces_tagged'] = sum([persons_dict[n] for n in persons_dict])
    persons_names = list(persons_dict.keys())
    top_nums = min(len(persons_names), 5)
    top_5_persons = persons_names[:top_nums]
    data['top_5_persons'] = top_5_persons
    data['top_5_persons_count'] = [persons_dict[n] for n in top_5_persons]

    # Movies stats
    movies = list(filter(lambda p: p.ismovie, ps))
    data['num_movies'] = len(movies)
    movies_duration = [m.exif_info.duration if m.exif_info.duration else 0 for m in movies]
    data['total_movies_size_mbyte'] = sum([m.original_filesize for m in movies]) / 1e6
    data["total_movies_duration_seconds"] = round(sum(movies_duration))
    data["max_movie_duration_seconds"] = round(max(movies_duration))
    

    # Hidden stats
    hiddens = list(filter(lambda p: p.hidden, ps))
    data['num_hidden'] = len(hiddens)
    data["total_size_hidden_mbyte"] = round(sum([p.original_filesize for p in hiddens]) / 1e6, 1)

    # Selfies
    selfies = list(filter(lambda p: p.selfie, ps))
    data['num_selfies'] = len(selfies)

    # Screenshots
    screenshots = list(filter(lambda p: p.screenshot, ps))
    data['num_screenshots'] = len(screenshots)

    # Object detection labels
    labels = pd.labels_as_dict
    data['labels'] = list(labels.keys())

    # Break photos down by month
    ps_dated_by_month = groupByDate(ps, date_format='%m')
    num_photos_by_month = dict()
    for month in ps_dated_by_month:
        num_photos_by_month[month] = len(ps_dated_by_month[month])
    data['num_photos_by_month'] = num_photos_by_month

    # Output
    outfile_path = os.path.join(outdir, 'stats.json')
    with open(outfile_path, 'w') as outfile:
        json.dump(data, outfile)


def exportGPS(ps:list[osxphotos.PhotoInfo], outdir:str, precision:int=5):
    """
    Exports gps.csv which contains a list of all GPS coordinates and
    with a precision of 5-decimal places by default -- which is about
    1.1 meters
    """

    if checkSkippable(outdir, EXPORT_TYPE_GPS_COORDS):
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

    if checkSkippable(outdir, EXPORT_TYPE_CALENDAR_HEATMAP):
        print('Photos library did not change; skipping calendar heatmap data export')
        return

    outfile_path = os.path.join(outdir, 'calendar_heatmap.csv')
    print(f'Exporting calendar heatmap data to {outfile_path}')

    with open(outfile_path, 'w') as outfile:
        outfile.write('date,num\n')
        for key in sorted(ps_dated.keys()):
            outfile.write(f'{key},{len(ps_dated[key])}\n')

    print(f'Done writing calendar heatmap data')


def exportPeopleData(ps:list[osxphotos.PhotoInfo], outdir:str):
    if checkSkippable(outdir, EXPORT_TYPE_PEOPLE):
        print('Photos library did not change; skipping people data export')
        return

    grouped = groupByNameAndDate(ps)

    ds = sorted(list(set([date for named_list in grouped.values() for date in named_list])))
    start = datetime.strptime(ds[0], '%Y-%m-%d')
    end = datetime.strptime(ds[-1], '%Y-%m-%d')
    timeline = [(start + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0, (end - start).days + 1)]
    outdata = {
        'timeline': timeline,
        'series': list()
    }
    
    for name in grouped:
        counts = [len(grouped[name][t]) if t in grouped[name] else 0 for t in timeline]
        print(counts)
        outdata['series'].append({
            'name': name,
            'counts': counts,
            'total': sum(counts)
        })

    # Write to file
    outfile_path = os.path.join(outdir, 'people.json')
    print(f'Exporting people data to {outfile_path}')
    with open(outfile_path, 'w') as outfile:
        json.dump(outdata, outfile)
    
    print("Done exporting people data.")

def exportPeopleRelationshipData(ps:list[osxphotos.PhotoInfo], names:list[str], outdir:str):
    """
    Export people-people group photo data
    Where data is a MxM matirx where M is the number of people

    First argument is a list of photos
    Second argument is a list sorted names
        this can be acquierd from the pd object
    """

    # if checkSkippable(outdir, EXPORT_TYPE_PEOPLE_REL):
    #     print('Photos library did not change; skipping people relationship data export')
    #     return

    # Filter names
    unknown_name = '_UNKNOWN_'
    names = list(filter(lambda name: name != unknown_name, names))

    # Set output
    outfile_path = os.path.join(outdir, 'people_rel.json')
    print(f'Exporting people-relationship data to {outfile_path}')
    
    # Filter out all photos that doesn't have face AND not '_UNKNOWN_'
    ps_filtered = list(filter(lambda photo: len(photo.persons) > 1 or (len(photo.persons) == 1 and unknown_name not in photo.persons), ps))
    print(f'There are {len(ps_filtered)}/{len(ps)} photos that have >= 1 known person in it')

    # Build 2D data matrix
    n = len(names)
    data = [[0] * n for i in range(n)]

    # Go through all the photos and populate the data matrix
    for p in ps:
        persons = list(filter(lambda name: name != unknown_name, p.persons))
        for i, person in enumerate(persons):
            index1 = names.index(person)
            for j in range(i, len(persons)):
                index2 = names.index(persons[j])
                data[index1][index2] += 1

    # Consolidate and fix the matrix to make sure it's symmetrical diagonally
    for i in range(n):
        for j in range(i, n):
            if i == j:
                continue
            data[j][i] = data[i][j] = data[j][i] + data[i][j]

    outdata = {
        'names': names,
        'data': data
    }

    with open(outfile_path, 'w') as outfile:
        json.dump(outdata, outfile)


def exportBestDailyPhoto(ps_dated:dict[str,list[osxphotos.PhotoInfo]], outdir:str, export_photos:bool, export_score_threshold:float):

    if checkSkippable(outdir, EXPORT_TYPE_BEST_DAILY):
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
                use_photos_export=True
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
