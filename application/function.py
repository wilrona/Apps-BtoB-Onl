__author__ = 'wilrona'

import re

import datetime
from datetime import date, timedelta

from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.objectid import ObjectId
from bson.errors import InvalidId

# Define the weekday mnemonics to match the date.weekday function
(MON, TUE, WED, THU, FRI, SAT, SUN) = range(7)
# Define default weekends, but allow this to be overridden at the function level
# in case someone only, for example, only has a 4-day workweek.
default_weekends=(SAT,SUN)


def networkdays(start_date, end_date, holidays=[], weekends=default_weekends):
    delta_days = (end_date - start_date).days + 1
    full_weeks, extra_days = divmod(delta_days, 7)
    # num_workdays = how many days/week you work * total # of weeks
    num_workdays = (full_weeks + 1) * (7 - len(weekends))
    # subtract out any working days that fall in the 'shortened week'
    for d in range(1, 8 - extra_days):
        if (end_date + timedelta(d)).weekday() not in weekends:
             num_workdays -= 1
    # skip holidays that fall on weekends
    holidays =  [x for x in holidays if x.weekday() not in weekends]
    # subtract out any holidays
    for d in holidays:
        if start_date <= d <= end_date:
            num_workdays -= 1
    return num_workdays


def datetime_convert(time): # Convertis time sous la forme YYYY-MM-DD HH:MM:SS
    _time = str(time)
    retime = re.compile(r'\W+')
    _list = retime.split(_time)

    if len(_list) >= 6:
        year = int(_list[0])
        mounth = int(_list[1])
        day = int(_list[2])
        hour = int(_list[3])
        minute = int(_list[4])
        second = int(_list[5])
        time = datetime.datetime(year, mounth, day, hour, minute, second)
        return time

    else:
        try:
            hour = int(_list[0])
            minute = int(_list[1])
            second = int(_list[2])
            time = datetime.datetime(2000, 1, 1, hour, minute, second)
            return time

        except IndexError:
            hour = int(_list[0])
            minute = int(_list[1])
            time = datetime.datetime(2000, 1, 1, hour, minute)
            return time


def date_convert(date):# Convertis date sous la forme YYYY-MM-DD
    _date = str(date)
    redate = re.compile(r'\W+')
    _list = redate.split(_date)
    try:
        day = int(_list[0])
        mounth = int(_list[1])
        year = int(_list[2])
        date = datetime.date(year, mounth, day)
        return date
    except ValueError:
        day = int(_list[2])
        mounth = int(_list[1])
        year = int(_list[0])
        date = datetime.date(year, mounth, day)
        return date

# jinja 2 formatage de la date
def format_date(date, format=None):
    try:
        newdate = date.strftime(format)
    except ValueError:
        dateMin = str(date.minute)
        if date.minute < 10:
            dateMin = str(date.minute)+'0'
        newdate = '0'+str(date.hour)+":"+dateMin
    return newdate

def format_date_month(date, format=None):
    newdate = date.strftime(format).lstrip("0").replace(" 0", " ")
    return newdate


def time_convert(time): # Convertis time sous la forme HH:MM:SS
    _time = str(time)
    retime = re.compile(r'\W+')
    _list = retime.split(_time)
    try:
        hour = int(_list[0])
        minute = int(_list[1])
        second = int(_list[2])
        time = datetime.time(hour, minute, second)
        return time
    except IndexError:
        hour = int(_list[0])
        minute = int(_list[1])
        time = datetime.time(hour, minute)
        return time


def convert_in_second(time):
    if time:
        _time = str(time)
        retime = re.compile(r'\W+')
        _list = retime.split(_time)
        try:
            hour = int(_list[0]) * 3600
            minute = int(_list[1]) * 60
            second = int(_list[2])
            time = hour + minute + second
            return time
        except IndexError:
            hour = int(_list[0]) * 3600
            minute = int(_list[1]) * 60
            time = hour + minute
            return time
    else:
        time = 0
        return time


# jinja 2 ajoute du temps sur le temp en cours
def add_time(time, retard):
    time = datetime_convert(time)
    if retard:
        _time = str(retard)
        retime = re.compile(r'\W+')
        _list = retime.split(_time)
        hour = int(_list[0]) * 3600
        minute = int(_list[1]) * 60
        time2 = hour + minute
        new_time = time + datetime.timedelta(0, time2)
    else:
        new_time = time
    return new_time.time()


# jinja 2 formatage du prix avec des espaces
def format_price(price):
    if price:
        return '{:,}'.format(price).replace(',', ' ')


def find(word, search):
    news = word.split(" ")
    tab = []
    tabs = []
    letter = ""

    for new in news:
        count = 0

        for n in new:
           letter += n
           tab.append(letter)
           count += 1
           if count == len(new):
               tabs.append(tab)
               count = 0
               letter = ""
               tab = []
    w = False
    for tab in tabs:
        if search in tab:
            w = True
    return w


def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds


def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return date(y+a, m+1, 1)


def get_last_day(dt):
    return get_first_day(dt, 0, 1) + timedelta(-1)


class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(base64_decode(value))
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()

    def to_url(self, value):
        return base64_encode(value.binary)


def reference(count, caractere, user=False, refuser=None):

    str_count = str(count)
    # reste = caractere - len(str(count))
    current_year = str(datetime.datetime.now().year)
    # refe = ''
    # str_count.rjust(caractere, '0')

    # for i in range(reste):
    #     refe += '0'
    #
    # refe += str(count)

    refe = str_count.rjust(caractere, '0')

    if not user:
        if refuser:
            all_ref = refuser+'/'+current_year+'/'+refe
        else:
            all_ref = current_year+'/'+refe
    else:
        all_ref = 'YO/'+refe

    return all_ref


def string(data):
    return str(data)


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def _slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    
    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)