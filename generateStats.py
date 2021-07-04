#!/usr/local/bin/python3

# Read the apple photos library and write GPS as csv

import osxphotos
import sys

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

def generateCalendarStats(dated: dict):
    """
    Writes to a csv file where the first column is date, 
    and the second column is the number of photos taken
    on that date
    """

    with open('heatmap.csv', 'w') as outfile:
        outfile.write('date,num\n')
        for key in sorted(dated.keys()):
            outfile.write(f'{key},{len(dated[key])}\n')

    print('Done writing to heatmap.csv')

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

def main():
    if len(sys.argv) <= 1:
        print('Please enter the path to the .photoslibrary as an argument')
        exit(1)

    libpath = sys.argv[1]

    print(f"Opening photo library at {libpath}, this may take a while.")
    pd = osxphotos.PhotosDB(libpath)
    ps = pd.photos()

    # Sort by date
    dated = sortByDate(ps)

    # Write stats
    extractGPStoCSV(ps)
    generateCalendarStats(dated)
    generateDayBestPhotoStats(dated)

    # Todo use the dict like in calendar and sort PhotoInfo by days

    # Todo generate top pictures of the year by looking at their ScoreInfo

    # Todo like heatmap, but also assign the max ScoreInfo.overall to each day


if __name__ == '__main__':
    main()
