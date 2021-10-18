import datetime as dt
import jdatetime as jt

from pandas import to_datetime
import requests

from pandas_datareader.compat import is_number


class SymbolWarning(UserWarning):
    pass


class RemoteDataError(IOError):
    pass


def _sanitize_dates(start, end):
    """
    Return (timestamp_start, timestamp_end) tuple
    if start is None - default is 5 years before the current date
    if end is None - default is today

    Parameters
    ----------
    start : str, int, date, datetime, Timestamp
        Desired start date
    end : str, int, date, datetime, Timestamp
        Desired end date
    """
    if is_number(start):
        if start <= 1600:
            # jalali year
            start = jt.datetime(start, 1, 1).togregorian()
        elif start <= 9999:
            # regard int as year
            start = dt.datetime(start, 1, 1)
        elif start <= 16001230:
            # jalali date as int ex: 14001020
            start = jt.datetime.strptime(str(start), '%Y%m%d').togregorian()
        else:
            # date as int ex: 20210925
            start = dt.datetime.strptime(str(start), "%Y%m%d")

    if is_number(end):
        if end <= 1600:
            # jalali year
            end = jt.datetime(end, 1, 1).togregorian()
        elif end <= 9999:
            # regard int as year
            end = dt.datetime(end, 1, 1)
        elif end <= 16001230:
            # jalali date as int ex: 14001020
            end = jt.datetime.strptime(str(end), '%Y%m%d').togregorian()
        else:
            # date as int ex: 20210925
            end = dt.datetime.strptime(str(end), "%Y%m%d")

    if start is None:
        # default to 5 years before today
        today = dt.date.today()
        start = today - dt.timedelta(days=365 * 5)
    if end is None:
        # default to today
        end = dt.date.today()
    try:
        start = to_datetime(start)
        end = to_datetime(end)
    except (TypeError, ValueError):
        raise ValueError("Invalid date format.")
    if start > end:
        raise ValueError("start must be an earlier date than end")
    return start, end


def _init_session(session):
    if session is None:
        session = requests.Session()
        # do not set requests max_retries here to support arbitrary pause
    else:
        if not isinstance(session, requests.Session):
            raise TypeError("session must be a request.Session")
    return session
