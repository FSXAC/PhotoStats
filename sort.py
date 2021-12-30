import osxphotos
from score import *

def sortByScoreAttribute(
    ps: list[osxphotos.PhotoInfo],
    attr: str
):
    """
    Sort a list of photos based on a score attibute
    and returns a sorted list
    """
    # Check that the attribute is valid
    if attr not in SCORE_ATTRIBUTES:
        print(f"Error: no attribute {attr}")
        return None

    return sorted(ps, key=lambda photo: getattr(photo.score, attr), reverse=True)

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
