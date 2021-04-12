#!/usr/local/bin/python3

# Read the apple photos library and write GPS as csv

import osxphotos
import sys

def extractGPStoCSV(ps: list[osxphotos.PhotoInfo]):
    with open('gps.csv', 'w') as outfile:
        outfile.write('lon,lat,x\n')
        for p in ps:
            loc = p.location
            if loc[0] is not None:
                outfile.write(f'{loc[0]},{loc[1]},1\n')

    print('Done writing to gps.csv')

def generateCalendarStats(ps: list[osxphotos.PhotoInfo]):
    """
    Writes to a csv file where the first column is date, 
    and the second column is the number of photos taken
    on that date
    """

    print('Reading all dates...')
    calendar = {}
    for p in ps:
        key = p.date.strftime('%Y-%m-%d')
        if key in calendar:
            calendar[key] += 1
        else:
            calendar[key] = 1

    print('Done reading')

    with open('heatmap.csv', 'w') as outfile:
        outfile.write('date, num\n')
        for key in sorted(calendar.keys()):
            outfile.write(f'{key},{calendar[key]}\n')

    print('Done writing to heatmap.csv')

def main():
    if len(sys.argv) <= 1:
        print('Please enter the path to the .photoslibrary as an argument')
        exit(1)

    libpath = sys.argv[1]

    print(f"Opening photo library at {libpath}, this may take a while.")
    pd = osxphotos.PhotosDB(libpath)
    ps = pd.photos()

    # Write stats
    # extractGPStoCSV(ps)
    generateCalendarStats(ps)

    # Todo use the dict like in calendar and sort PhotoInfo by days

    # Todo generate top pictures of the year by looking at their ScoreInfo

    # Todo like heatmap, but also assign the max ScoreInfo.overall to each day


if __name__ == '__main__':
    main()
