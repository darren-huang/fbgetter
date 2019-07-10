from datetime import datetime, timedelta
from calendar import timegm
from pytz import timezone


def dateToEpoch(dateTimeG, tzStr):
    """dateTime is given as YEAR-MONTH-DAY HOUR:MIN:SEC"""
    pattern = '%Y-%m-%d %H:%M:%S'

    try:
        offsetDateTime = timezone(tzStr).localize(datetime.strptime(dateTimeG, pattern))
    except ValueError as _:
        epoch = int(timegm(offsetDateTime.utctimetuple()))
    return epoch


def epochToDate(epoch, tzStr, reprBool=True):
    """takes epoch and changes it to a string date format"""
    if not epoch:
        return "never"
    gTzTime = datetime.fromtimestamp(epoch, timezone(tzStr))
    if reprBool:
        return gTzTime.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return gTzTime.strftime('%a, %B %d, %Y  %H:%M:%S')


def epochToCSV(epoch, tzStr):
    """takes epoch and changes it to preset comma separated values"""
    gTzTime = datetime.fromtimestamp(epoch, timezone(tzStr))
    # %j represents day of the year
    # currently set to:  dayOfMonth, dayOfWeek, Hour, Min
    s = gTzTime.strftime('%d,%w,%H,%M')
    return s


def epochToDateTimeObj(epoch, tzStr):
    return datetime.fromtimestamp(epoch, tz=timezone(tzStr))
