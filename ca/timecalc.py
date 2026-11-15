# -*- coding: utf-8 -*-
"""Dates and times (the `time` keyword).

    time                                  now, in every configured format, plus the timestamp
    time 1577836800                       what a Unix timestamp means
    time +15 days                         time now plus 3 days        time 3 days ago
    time today + 3 workdays               business days only
    time days until 31 december           also hours/minutes/weeks/months, and "since"
    time start of year                    time end of 2021            time end of month
    time 31 December, 2021 18:00:00       time 31/12/2021 18:00       time next friday 3pm
    time 25 December, 2021 - 31 December, 2021      the difference between two dates
    time 3pm utc                          a time given in another zone, shown in yours
    time now in tokyo                     your time shown in another zone
    time monday in 3 weeks                time in 2 hours
    time week 44 2026                     time week            ISO weeks, Monday to Sunday
    time days left in this month          also weeks, workdays, hours; month, year, week
    time days until end of month          until/since a start or end

The original handed all of this to PHP's date parser. This module is that parser's
everyday subset, written out, so it has no dependency to rot.
"""
import calendar
import datetime as dt
import re

from .core import clean_query, item, load_timezone, message, strip_accents

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
          'october', 'november', 'december']
MONTHS_SHORT = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
WEEKDAYS_SHORT = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

MONTH_NUMBER = dict((name, index + 1) for index, name in enumerate(MONTHS))
MONTH_NUMBER.update((name, index + 1) for index, name in enumerate(MONTHS_SHORT))
MONTH_NUMBER['sept'] = 9
WEEKDAY_NUMBER = dict((name, index) for index, name in enumerate(WEEKDAYS))
WEEKDAY_NUMBER.update((name, index) for index, name in enumerate(WEEKDAYS_SHORT))
WEEKDAY_NUMBER.update({'tues': 1, 'weds': 2, 'thur': 3, 'thurs': 3})

UNIT_WORDS = {
    'second': 'second', 'seconds': 'second', 'sec': 'second', 'secs': 'second',
    'minute': 'minute', 'minutes': 'minute', 'min': 'minute', 'mins': 'minute',
    'hour': 'hour', 'hours': 'hour', 'hr': 'hour', 'hrs': 'hour', 'h': 'hour',
    'day': 'day', 'days': 'day', 'd': 'day',
    'weekday': 'weekday', 'weekdays': 'weekday',
    'week': 'week', 'weeks': 'week', 'wk': 'week', 'wks': 'week', 'w': 'week',
    'fortnight': 'fortnight', 'fortnights': 'fortnight',
    'month': 'month', 'months': 'month', 'mo': 'month', 'mos': 'month',
    'year': 'year', 'years': 'year', 'yr': 'year', 'yrs': 'year', 'y': 'year',
    'decade': 'decade', 'decades': 'decade',
}

SECONDS = {'second': 1, 'minute': 60, 'hour': 3600}

_UNIT = '(?:%s)' % '|'.join(sorted(UNIT_WORDS, key=len, reverse=True))
_MONTH = '(?:%s)' % '|'.join(sorted(MONTH_NUMBER, key=len, reverse=True))
_WEEKDAY = '(?:%s)' % '|'.join(sorted(WEEKDAY_NUMBER, key=len, reverse=True))

# Abbreviations and place names people type that are not IANA city names.
ZONE_ALIASES = {
    'utc': 'UTC', 'gmt': 'UTC', 'z': 'UTC', 'zulu': 'UTC',
    'est': 'America/New_York', 'edt': 'America/New_York', 'et': 'America/New_York', 'eastern': 'America/New_York',
    'cst': 'America/Chicago', 'cdt': 'America/Chicago', 'ct': 'America/Chicago', 'central': 'America/Chicago',
    'mst': 'America/Denver', 'mdt': 'America/Denver', 'mt': 'America/Denver', 'mountain': 'America/Denver',
    'pst': 'America/Los_Angeles', 'pdt': 'America/Los_Angeles', 'pt': 'America/Los_Angeles',
    'pacific': 'America/Los_Angeles',
    'akst': 'America/Anchorage', 'akdt': 'America/Anchorage', 'hst': 'Pacific/Honolulu',
    'bst': 'Europe/London', 'uk': 'Europe/London', 'wet': 'Europe/Lisbon',
    'cet': 'Europe/Paris', 'cest': 'Europe/Paris', 'eet': 'Europe/Athens', 'eest': 'Europe/Athens',
    'msk': 'Europe/Moscow', 'ist': 'Asia/Kolkata', 'india': 'Asia/Kolkata', 'pkt': 'Asia/Karachi',
    'ict': 'Asia/Bangkok', 'thailand': 'Asia/Bangkok', 'vietnam': 'Asia/Ho_Chi_Minh',
    'wib': 'Asia/Jakarta', 'wita': 'Asia/Makassar', 'wit': 'Asia/Jayapura', 'indonesia': 'Asia/Jakarta',
    'bali': 'Asia/Makassar',
    'sgt': 'Asia/Singapore', 'myt': 'Asia/Kuala_Lumpur', 'malaysia': 'Asia/Kuala_Lumpur',
    'hkt': 'Asia/Hong_Kong', 'pht': 'Asia/Manila', 'philippines': 'Asia/Manila',
    'china': 'Asia/Shanghai', 'beijing': 'Asia/Shanghai',
    'jst': 'Asia/Tokyo', 'japan': 'Asia/Tokyo', 'kst': 'Asia/Seoul', 'korea': 'Asia/Seoul',
    'awst': 'Australia/Perth', 'acst': 'Australia/Adelaide', 'acdt': 'Australia/Adelaide',
    'aest': 'Australia/Sydney', 'aedt': 'Australia/Sydney',
    'nzst': 'Pacific/Auckland', 'nzdt': 'Pacific/Auckland', 'new zealand': 'Pacific/Auckland',
    'brt': 'America/Sao_Paulo', 'art': 'America/Argentina/Buenos_Aires',
    'sast': 'Africa/Johannesburg', 'eat': 'Africa/Nairobi', 'wat': 'Africa/Lagos',
    'gst': 'Asia/Dubai', 'uae': 'Asia/Dubai', 'germany': 'Europe/Berlin', 'france': 'Europe/Paris',
    'spain': 'Europe/Madrid', 'italy': 'Europe/Rome', 'sweden': 'Europe/Stockholm',
    'mexico': 'America/Mexico_City', 'san francisco': 'America/Los_Angeles', 'seattle': 'America/Los_Angeles',
    'washington': 'America/New_York', 'boston': 'America/New_York', 'miami': 'America/New_York',
    'dallas': 'America/Chicago', 'houston': 'America/Chicago',
}

_zone_names = None


def find_zone(name):
    """An IANA zone name for "utc", "wib", "tokyo", "new york", "+07:00"... or None."""
    global _zone_names
    name = name.strip().lower()
    if not name:
        return None
    if name in ZONE_ALIASES:
        return ZONE_ALIASES[name]
    offset = re.match(r'^(?:utc|gmt)? ?([+-])(\d{1,2})(?::?(\d{2}))?$', name)
    if offset:
        hours, minutes = int(offset.group(2)), int(offset.group(3) or 0)
        if hours <= 14 and minutes < 60:
            return 'offset:%s%02d:%02d' % (offset.group(1), hours, minutes)
        return None
    if len(name) < 3 or not re.match(r'^[a-z][a-z /_-]*$', name):
        return None
    if _zone_names is None:
        try:
            from zoneinfo import available_timezones
            _zone_names = sorted(available_timezones())
        except Exception:
            _zone_names = []
    wanted = name.replace(' ', '_')
    for zone in _zone_names:
        lowered = zone.lower()
        if lowered == wanted or ('/' in zone and lowered.rsplit('/', 1)[1] == wanted):
            return zone
    return None


def zone_info(name):
    if name.startswith('offset:'):
        sign = -1 if name[7] == '-' else 1
        hours, minutes = int(name[8:10]), int(name[11:13])
        delta = dt.timedelta(hours=hours, minutes=minutes) * sign
        return dt.timezone(delta, 'UTC' + name[7:])
    return load_timezone(name)


# --------------------------------------------------------------------------- arithmetic

def add_months(moment, months):
    """Calendar months; the 31st lands on the last day of a shorter month."""
    index = moment.year * 12 + (moment.month - 1) + months
    year, month = divmod(index, 12)
    month += 1
    if not 1 <= year <= 9999:
        raise ValueError('year out of range')
    day = min(moment.day, calendar.monthrange(year, month)[1])
    return moment.replace(year=year, month=month, day=day)


def add_weekdays(moment, count):
    step = 1 if count >= 0 else -1
    remaining = abs(int(count))
    while remaining:
        moment += dt.timedelta(days=step)
        if moment.weekday() < 5:
            remaining -= 1
    return moment


def calendar_diff(start, end):
    """(years, months, days, hours, minutes, seconds) from start to end, start <= end."""
    if start.tzinfo is not None and end.tzinfo is not None:
        end = end.astimezone(start.tzinfo)        # compare clock times in one zone
    start, end = start.replace(tzinfo=None), end.replace(tzinfo=None)
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if add_months(start, months) > end:
        months -= 1
    rest = end - add_months(start, months)
    hours, remainder = divmod(rest.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return (months // 12, months % 12, rest.days, hours, minutes, seconds)


def _count(ctx, number, singular):
    word = singular if number == 1 else singular + 's'
    return '%d %s' % (number, ctx.text('time', word, word))


def timespan(ctx, first, second):
    """"1 year, 2 months, 1 week, 3 days, 4 hours": everything between two moments."""
    start, end = (first, second) if first <= second else (second, first)
    years, months, days, hours, minutes, seconds = calendar_diff(start, end)
    parts = [(years, 'year'), (months, 'month'), (days // 7, 'week'), (days % 7, 'day'),
             (hours, 'hour'), (minutes, 'minute'), (seconds, 'second')]
    words = [_count(ctx, number, unit) for number, unit in parts if number]
    return ', '.join(words) or _count(ctx, 0, 'second')


def ago(ctx, moment, now):
    """"3 days ago": the largest whole unit only."""
    years, months, days, hours, minutes, seconds = calendar_diff(moment, now)
    for number, unit in ((years, 'year'), (months, 'month'), (days // 7, 'week'), (days, 'day'),
                         (hours, 'hour'), (minutes, 'minute'), (max(seconds, 1), 'second')):
        if number:
            return (ctx.text('time', 'ago', '%s ago')) % _count(ctx, number, unit)
    return ''


# --------------------------------------------------------------------------- formatting

def _names(ctx, key, fallback):
    names = ctx.lang.section('time').get(key)
    return names if isinstance(names, list) and len(names) == len(fallback) else fallback


def _offset(moment, colon):
    delta = moment.utcoffset() or dt.timedelta(0)
    minutes = int(delta.total_seconds() // 60)
    sign = '+' if minutes >= 0 else '-'
    minutes = abs(minutes)
    return '%s%02d%s%02d' % (sign, minutes // 60, ':' if colon else '', minutes % 60)


def php_date(fmt, moment, ctx):
    """Format with PHP's date() letters, which is what the date-format setting uses."""
    english = ctx.lang.code.startswith('en')
    months = _names(ctx, 'months', [name.capitalize() for name in MONTHS])
    months_short = _names(ctx, 'months_short', [name.capitalize() for name in MONTHS_SHORT])
    weekdays = _names(ctx, 'weekdays', [name.capitalize() for name in WEEKDAYS])
    weekdays_short = _names(ctx, 'weekdays_short', [name.capitalize() for name in WEEKDAYS_SHORT])
    iso_year, iso_week, iso_weekday = moment.isocalendar()[0], moment.isocalendar()[1], moment.isocalendar()[2]
    hour12 = moment.hour % 12 or 12
    out = []
    index = 0
    while index < len(fmt):
        ch = fmt[index]
        index += 1
        if ch == '\\':
            if index < len(fmt):
                out.append(fmt[index])
                index += 1
            continue
        if ch == 'd':
            out.append('%02d' % moment.day)
        elif ch == 'D':
            out.append(weekdays_short[moment.weekday()])
        elif ch == 'j':
            out.append(str(moment.day))
        elif ch == 'l':
            out.append(weekdays[moment.weekday()])
        elif ch == 'N':
            out.append(str(iso_weekday))
        elif ch == 'S':
            if english:
                day = moment.day
                out.append('th' if 11 <= day % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th'))
        elif ch == 'w':
            out.append(str(iso_weekday % 7))
        elif ch == 'z':
            out.append(str(moment.timetuple().tm_yday - 1))
        elif ch == 'W':
            out.append('%02d' % iso_week)
        elif ch == 'F':
            out.append(months[moment.month - 1])
        elif ch == 'm':
            out.append('%02d' % moment.month)
        elif ch == 'M':
            out.append(months_short[moment.month - 1])
        elif ch == 'n':
            out.append(str(moment.month))
        elif ch == 't':
            out.append(str(calendar.monthrange(moment.year, moment.month)[1]))
        elif ch == 'L':
            out.append('1' if calendar.isleap(moment.year) else '0')
        elif ch == 'o':
            out.append(str(iso_year))
        elif ch == 'Y':
            out.append(str(moment.year))
        elif ch == 'y':
            out.append('%02d' % (moment.year % 100))
        elif ch == 'a':
            out.append('am' if moment.hour < 12 else 'pm')
        elif ch == 'A':
            out.append('AM' if moment.hour < 12 else 'PM')
        elif ch == 'g':
            out.append(str(hour12))
        elif ch == 'G':
            out.append(str(moment.hour))
        elif ch == 'h':
            out.append('%02d' % hour12)
        elif ch == 'H':
            out.append('%02d' % moment.hour)
        elif ch == 'i':
            out.append('%02d' % moment.minute)
        elif ch == 's':
            out.append('%02d' % moment.second)
        elif ch == 'u':
            out.append('%06d' % moment.microsecond)
        elif ch == 'v':
            out.append('%03d' % (moment.microsecond // 1000))
        elif ch == 'e':
            out.append(str(getattr(moment.tzinfo, 'key', None) or moment.tzname() or ''))
        elif ch == 'I':
            out.append('1' if moment.dst() else '0')
        elif ch == 'O':
            out.append(_offset(moment, False))
        elif ch == 'P':
            out.append(_offset(moment, True))
        elif ch == 'p':
            out.append('Z' if not moment.utcoffset() else _offset(moment, True))
        elif ch == 'T':
            out.append(moment.tzname() or '')
        elif ch == 'Z':
            out.append(str(int((moment.utcoffset() or dt.timedelta(0)).total_seconds())))
        elif ch == 'c':
            out.append(moment.strftime('%Y-%m-%dT%H:%M:%S') + _offset(moment, True))
        elif ch == 'r':
            out.append('%s, %02d %s %d %s %s' % (
                WEEKDAYS_SHORT[moment.weekday()].capitalize(), moment.day,
                MONTHS_SHORT[moment.month - 1].capitalize(), moment.year,
                moment.strftime('%H:%M:%S'), _offset(moment, False)))
        elif ch == 'U':
            out.append(str(int(moment.timestamp())))
        else:
            out.append(ch)
    return ''.join(out)


# --------------------------------------------------------------------------- translating input

def _word_pattern(word):
    """Match `word` only as a whole word (it may itself contain spaces or symbols)."""
    return r'(?<![^\W\d_])%s(?![^\W\d_])' % re.escape(word)


def translate(ctx, query):
    """Rewrite the query in the English vocabulary the parser understands:
    "ahora más 3 días" -> "now + 3 days", "31 diciembre" -> "31 december"."""
    text = ' %s ' % clean_query(query)
    keywords = ctx.lang.keywords('time')
    for key in sorted(keywords, key=len, reverse=True):
        value = keywords[key]
        key = key.strip()
        if not key or not isinstance(value, str):
            continue
        text = re.sub(_word_pattern(key), ' %s ' % value, text)

    sources = [] if ctx.lang.code.startswith('en') else [ctx.lang.section('time')]
    sources += [extra.get('time') for extra in ctx.lang.input_strings if isinstance(extra.get('time'), dict)]
    if sources:
        table = {}
        for strings in sources:
            for english in ('second', 'seconds', 'minute', 'minutes', 'hour', 'hours', 'day', 'days',
                            'week', 'weeks', 'month', 'months', 'year', 'years'):
                local = strings.get(english)
                if isinstance(local, str) and local:
                    table.setdefault(local.lower(), english)
            for key, english_names in (('months', MONTHS), ('months_short', MONTHS_SHORT),
                                       ('weekdays', WEEKDAYS), ('weekdays_short', WEEKDAYS_SHORT)):
                local_names = strings.get(key)
                if isinstance(local_names, list) and len(local_names) == len(english_names):
                    for local, english in zip(local_names, english_names):
                        table.setdefault(str(local).lower(), english)
        for local in list(table):
            table.setdefault(strip_accents(local), table[local])

        def swap(match):
            word = match.group(0)
            return table.get(word) or table.get(strip_accents(word)) or word
        text = re.sub(r'[^\W\d_]+', swap, text)
    return re.sub(r'\s+', ' ', text).strip()


# --------------------------------------------------------------------------- parsing

class Parsed(object):
    def __init__(self, moment, has_time, zone_shown):
        self.moment = moment          # aware datetime in the zone it should be displayed in
        self.has_time = has_time      # False when only a date was given (midnight implied)
        self.zone_shown = zone_shown  # zone name when it is not the user's own


def _build_date(year, month, day):
    """A date that forgives day overflow the way PHP does (31 November -> 1 December)."""
    if not (1 <= month <= 12 and 1 <= day <= 31 and 1 <= year <= 9999):
        return None
    first = dt.date(year, month, 1)
    try:
        return first + dt.timedelta(days=day - 1)
    except OverflowError:
        return None


def _two_digit_year(text):
    year = int(text)
    if len(text) <= 2:
        year += 2000 if year < 70 else 1900
    return year


def parse(text, now, local_zone, month_first):
    """Understand a date/time expression. `now` is an aware datetime in the user's zone.
    Returns Parsed or None."""
    text = text.lower().replace(',', ' ')
    text = re.sub(r'\b(\d{1,2})(?:st|nd|rd|th)\b', r'\1', text)
    text = re.sub(r'\b(?:at|on|the)\b', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^(\d{1,2}) of (?=%s\b)' % _MONTH, r'\1 ', text)      # "31st of december"

    target_zone = None
    tail = re.search(r'(?:^| )in ([a-z][a-z /_+:\-0-9]*)$', text)
    if tail:
        zone = find_zone(tail.group(1))
        if zone:
            target_zone = zone
            text = text[:tail.start()].strip()

    date = None
    clock = None                 # (hour, minute, second)
    midnight = False             # a word like "today" pins the time to 00:00
    steps = []                   # [(amount, unit)]
    weekday = None               # (weekday number, direction)
    edge = None                  # "first" / "last" day of the month
    source_zone = None
    explicit = False

    def take(pattern):
        match = re.match(pattern, text)
        return match

    guard = 0
    while text and guard < 40:
        guard += 1
        match = take(r'^(\d{4})-(\d{1,2})-(\d{1,2})(?:t(?=\d))?')
        if match:
            date = _build_date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            if date is None:
                return None
            text = text[match.end():].strip()
            continue
        match = take(r'^(\d{4})/(\d{1,2})/(\d{1,2})\b')
        if match:
            date = _build_date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            if date is None:
                return None
            text = text[match.end():].strip()
            continue
        match = take(r'^(\d{1,2})([/.-])(\d{1,2})\2(\d{4}|\d{2})\b')
        if match:
            first, second = int(match.group(1)), int(match.group(3))
            year = _two_digit_year(match.group(4))
            # 01/02/2026 is ambiguous: slashes follow the user's region, dashes and dots
            # are day first. Either way an impossible month flips the reading.
            if match.group(2) == '/' and month_first:
                month, day = first, second
            else:
                day, month = first, second
            if month > 12 and day <= 12:
                day, month = month, day
            date = _build_date(year, month, day)
            if date is None:
                return None
            text = text[match.end():].strip()
            continue
        match = take(r'^(\d{1,2}) (%s)\b\.?(?: (\d{4})\b)?' % _MONTH)
        if match:
            year = int(match.group(3)) if match.group(3) else now.year
            date = _build_date(year, MONTH_NUMBER[match.group(2)], int(match.group(1)))
            if date is None:
                return None
            text = text[match.end():].strip()
            continue
        match = take(r'^(%s)\b\.? (\d{1,2})(?![:\d])(?: (\d{4})\b)?' % _MONTH)
        if match:
            year = int(match.group(3)) if match.group(3) else now.year
            date = _build_date(year, MONTH_NUMBER[match.group(1)], int(match.group(2)))
            if date is None:
                return None
            text = text[match.end():].strip()
            continue
        match = take(r'^(%s)\b\.?(?: (\d{4})\b)?' % _MONTH)
        if match:
            year = int(match.group(2)) if match.group(2) else now.year
            month = MONTH_NUMBER[match.group(1)]
            day = 1 if match.group(2) else min(now.day, calendar.monthrange(year, month)[1])
            date = _build_date(year, month, day)
            text = text[match.end():].strip()
            continue
        # the lookahead lets a trailing "z" (UTC, as in ISO 8601) through to the zone check
        match = take(r'^(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\.\d+)? ?(am|pm|a\.m\.|p\.m\.)?(?![a-y\d])')
        if not match:
            match = take(r'^(\d{1,2})()() ?(am|pm|a\.m\.|p\.m\.)(?![a-y\d])')
        if match:
            hour, minute, second = int(match.group(1)), int(match.group(2) or 0), int(match.group(3) or 0)
            half = (match.group(4) or '')[:1]
            if half:
                if not 1 <= hour <= 12:
                    return None
                hour = hour % 12 + (12 if half == 'p' else 0)
            if hour > 24 or minute > 59 or second > 59 or (hour == 24 and (minute or second)):
                return None
            clock = (hour, minute, second)
            text = text[match.end():].strip()
            continue
        match = take(r'^([+-]) ?(\d+(?:\.\d+)?) ?(%s)\b' % _UNIT)
        if not match:
            match = take(r'^()(\d+(?:\.\d+)?) ?(%s)\b' % _UNIT)
        if match:
            amount = float(match.group(2)) * (-1 if match.group(1) == '-' else 1)
            steps.append([amount, UNIT_WORDS[match.group(3)]])
            text = text[match.end():].strip()
            continue
        match = take(r'^in (\d+(?:\.\d+)?) ?(%s)\b' % _UNIT)        # "monday in 3 weeks"
        if match:
            steps.append([float(match.group(1)), UNIT_WORDS[match.group(2)]])
            text = text[match.end():].strip()
            continue
        match = take(r'^(next|last|previous|this) (%s|%s)\b' % (_UNIT, _WEEKDAY))
        if match:
            direction = {'next': 1, 'last': -1, 'previous': -1, 'this': 0}[match.group(1)]
            word = match.group(2)
            if word in WEEKDAY_NUMBER:
                weekday = (WEEKDAY_NUMBER[word], direction)
                midnight = True
            elif direction:
                steps.append([float(direction), UNIT_WORDS[word]])
            explicit = True
            text = text[match.end():].strip()
            continue
        match = take(r'^(%s)\b' % _WEEKDAY)
        if match:
            weekday = (WEEKDAY_NUMBER[match.group(1)], 0)
            midnight = True
            text = text[match.end():].strip()
            continue
        match = take(r'^(first|last) day(?: of)?\b')
        if match:
            edge = match.group(1)
            midnight = True
            text = text[match.end():].strip()
            continue
        match = take(r'^(now|today|midnight|noon|tomorrow|yesterday|ago|of)\b')
        if match:
            word = match.group(1)
            if word == 'ago':
                if not steps:
                    return None
                for step in steps:
                    step[0] = -abs(step[0])
            elif word == 'noon':
                clock = (12, 0, 0)
            elif word in ('today', 'midnight'):
                midnight = True
            elif word in ('tomorrow', 'yesterday'):
                midnight = True
                steps.append([1.0 if word == 'tomorrow' else -1.0, 'day'])
            explicit = True
            text = text[match.end():].strip()
            continue
        match = take(r'^@(-?\d+)\b')
        if match:
            try:
                stamp = dt.datetime.fromtimestamp(int(match.group(1)), dt.timezone.utc)
            except (OverflowError, OSError, ValueError):
                return None
            shown = zone_info(target_zone) if target_zone else local_zone
            return Parsed(stamp.astimezone(shown), True, target_zone)
        match = take(r'^(\d{4})$')
        if match and date is None:
            date = _build_date(int(match.group(1)), 1, 1)
            if date is None:
                return None
            text = ''
            continue
        # a time zone: "utc", "wib", "new york", "+07:00"
        words = text.split(' ')
        found = None
        for size in (3, 2, 1):
            if len(words) >= size:
                zone = find_zone(' '.join(words[:size]))
                if zone:
                    found = (zone, size)
                    break
        if found:
            source_zone = found[0]
            text = ' '.join(words[found[1]:]).strip()
            continue
        return None
    if text:
        return None

    specified = bool(date or clock or steps or weekday or edge or midnight or explicit)
    if source_zone and not specified and not target_zone:
        target_zone, source_zone = source_zone, None        # "time tokyo" = now, over there

    zone = zone_info(source_zone) if source_zone else local_zone
    base = now.astimezone(zone)
    if date is not None:
        base = base.replace(year=date.year, month=date.month, day=date.day)
    has_time = clock is not None
    if clock is not None:
        day_shift = 1 if clock[0] == 24 else 0
        base = base.replace(hour=clock[0] % 24, minute=clock[1], second=clock[2], microsecond=0)
        if day_shift:
            base += dt.timedelta(days=1)
    elif date is not None or midnight:
        base = base.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        has_time = True                                      # relative to this very moment

    try:
        if weekday is not None:
            wanted, direction = weekday
            ahead = (wanted - base.weekday()) % 7
            if direction > 0:
                ahead = ahead or 7
            elif direction < 0:
                ahead = ahead - 7 if ahead else -7
            base += dt.timedelta(days=ahead)
        for amount, unit in steps:
            if unit in SECONDS:
                base += dt.timedelta(seconds=amount * SECONDS[unit])
            elif unit == 'day':
                base += dt.timedelta(days=amount)
            elif unit == 'week':
                base += dt.timedelta(weeks=amount)
            elif unit == 'fortnight':
                base += dt.timedelta(weeks=2 * amount)
            elif unit == 'weekday':
                base = add_weekdays(base, amount)
            elif unit == 'month':
                base = add_months(base, int(round(amount)))
            elif unit == 'year':
                base = add_months(base, int(round(amount * 12)))
            elif unit == 'decade':
                base = add_months(base, int(round(amount * 120)))
        if edge == 'first':
            base = base.replace(day=1)
        elif edge == 'last':
            base = base.replace(day=calendar.monthrange(base.year, base.month)[1])
    except (OverflowError, ValueError):
        return None

    shown = zone_info(target_zone) if target_zone else local_zone
    return Parsed(base.astimezone(shown), has_time, target_zone)


# --------------------------------------------------------------------------- the keyword

_RELATIVE_ONLY = re.compile(r'^(?:\d+(?:\.\d+)? ?%s ?)+(?:ago)?$' % _UNIT)


def _zone_label(name, moment):
    if not name:
        return ''
    label = name[7:] if name.startswith('offset:') else name.replace('_', ' ')
    if name.startswith('offset:'):
        return 'UTC' + label
    return '%s (UTC%s)' % (label, _offset(moment, True))


def _instant_rows(ctx, parsed, now, is_now):
    moment = parsed.moment
    strings = ctx.lang.section('time')
    zone = _zone_label(parsed.zone_shown, moment)
    rows = []
    formats = [fmt for fmt in ctx.settings.date_formats if php_date(fmt, moment, ctx).strip()]
    for fmt in formats or ['j F, Y, g:i:s a']:          # a format that prints nothing is ignored
        shown = php_date(fmt, moment, ctx)
        subtitle = (strings.get('format_subtitle') or 'Format %s') % fmt
        if zone:
            subtitle = '%s  ·  %s' % ((strings.get('in_zone') or 'Time in %s') % zone, subtitle)
        rows.append(item(shown, subtitle, arg=shown))
    if not is_now and moment != now:
        span = ago(ctx, moment, now) if moment < now else timespan(ctx, now, moment)
        rows.append(item(span, strings.get('timespan') or 'Timespan', arg=span))
    stamp = str(int(moment.timestamp()))
    rows.append(item(stamp, strings.get('timestamp') or 'Timestamp', arg=stamp))
    return rows


def _phrase_match(ctx, name, text, leading):
    """Find a trigger phrase such as "until" / "hasta". Returns (before, after) or None."""
    for phrase in sorted(ctx.lang.phrases('time', name), key=len, reverse=True):
        if leading:
            if text.startswith(phrase + ' '):
                return '', text[len(phrase):].strip()
            if text == phrase:
                return '', ''
        else:
            marker = ' %s ' % phrase
            position = text.find(marker)
            if position > 0:
                return text[:position].strip(), text[position + len(marker):].strip()
    return None


def _edge_of(kind, what, now):
    """start of / end of <year|month|week|day|2021|march|march 2021|next month...>."""
    start = kind == 'start'
    shift = 0
    lead = re.match(r'^(next|last|previous|this) (.+)$', what)
    if lead:
        shift = {'next': 1, 'last': -1, 'previous': -1, 'this': 0}[lead.group(1)]
        what = lead.group(2)
    what = re.sub(r'^the ', '', what)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = now.replace(hour=23, minute=59, second=59, microsecond=0)

    def month_edge(year, month):
        last = calendar.monthrange(year, month)[1]
        if start:
            return day_start.replace(year=year, month=month, day=1)
        return day_end.replace(year=year, month=month, day=last)

    if what in ('year', 'this year') or re.match(r'^\d{4}$', what):
        year = int(what) if what.isdigit() else now.year + shift
        if not 1 <= year <= 9999:
            return None
        return day_start.replace(year=year, month=1, day=1) if start else day_end.replace(year=year, month=12, day=31)
    if what in ('month', 'this month'):
        moved = add_months(now.replace(day=1), shift)
        return month_edge(moved.year, moved.month)
    if what in ('week', 'this week'):
        monday = day_start - dt.timedelta(days=now.weekday()) + dt.timedelta(weeks=shift)
        if start:
            return monday
        sunday = monday + dt.timedelta(days=6)
        return sunday.replace(hour=23, minute=59, second=59)
    if what in ('day', 'today'):
        moved = now + dt.timedelta(days=shift)
        return (day_start if start else day_end).replace(year=moved.year, month=moved.month, day=moved.day)
    named = re.match(r'^(%s)\b\.?(?: (\d{4}))?$' % _MONTH, what)
    if named:
        year = int(named.group(2)) if named.group(2) else now.year + shift
        return month_edge(year, MONTH_NUMBER[named.group(1)])
    return None


def _nearest_year(text, target, now, since):
    """"days until 1 january" means the coming 1 January, "days since 25 december" the last one.
    Applies only to dates written with a month name and no year."""
    if re.search(r'\b\d{4}\b', text) or not re.search(r'\b%s\b' % _MONTH, text):
        return target
    moment = target.moment
    if not since and moment < now:
        moment = add_months(moment, 12)
    elif since and moment > now:
        moment = add_months(moment, -12)
    else:
        return target
    return Parsed(moment, target.has_time, target.zone_shown)


def _until(ctx, unit_word, target, now, since):
    """How many <unit> until (or since) a moment."""
    unit = UNIT_WORDS.get(unit_word)
    if unit is None or unit in ('fortnight', 'decade'):
        return None
    moment = target.moment
    start, end = (moment, now) if since else (now, moment)
    if end < start:
        start, end = end, start
    seconds = (end - start).total_seconds()
    if unit == 'weekday':
        first, last = start.date(), end.astimezone(start.tzinfo).date()
        number = sum(1 for offset in range(1, (last - first).days + 1)
                     if (first + dt.timedelta(days=offset)).weekday() < 5)
        return number, 'workday' if number == 1 else 'workdays'
    if unit == 'day':
        if target.has_time:
            number = round(seconds / 86400.0)
        else:
            number = abs((moment.date() - now.astimezone(moment.tzinfo).date()).days)
    elif unit == 'week':
        number = round(seconds / 604800.0, 1)
    elif unit in SECONDS:
        number = int(seconds // SECONDS[unit])
    else:
        years, months = calendar_diff(start, end)[:2]
        number = years if unit == 'year' else years * 12 + months
    word = unit if number == 1 else unit + 's'
    return number, ctx.text('time', word, word)


def _week_rows(ctx, year, week, now):
    """ISO week `week` of `year`: its Monday-to-Sunday range, then the Monday as usual."""
    try:
        monday = dt.date.fromisocalendar(year, week, 1)
    except ValueError:
        return None
    sunday = monday + dt.timedelta(days=6)
    start = now.replace(year=monday.year, month=monday.month, day=monday.day, hour=0, minute=0, second=0)
    end = start + dt.timedelta(days=6)
    template = ctx.text('time', 'week_range', '') or 'Week %s of %s'
    span = '%s – %s' % (php_date('j F' if monday.year == sunday.year else 'j F Y', start, ctx),
                        php_date('j F Y', end, ctx))
    rows = [item(span, template % (week, year), arg=span)]
    return rows + _instant_rows(ctx, Parsed(start, False, None), now, False)


def _edge_moment(ctx, text, now):
    """"end of month" / "start of next year" -> Parsed, or None."""
    for name, kind in (('end of', 'end'), ('start of', 'start')):
        found = _phrase_match(ctx, name, text, leading=True)
        if found is not None and found[1]:
            moment = _edge_of(kind, found[1], now)
            if moment is not None:
                return Parsed(moment, False, None)        # counted in calendar days, like a date
    return None


_LEFT = re.compile(r'^(seconds|minutes|hours|days|weeks|weekdays) left(?: (?:in|of))?(?: this| the)? '
                   r'(day|week|month|year)$')


def _left_rows(ctx, unit, period, now):
    """"days left in this month": whole days after today up to the end of the period."""
    end = _edge_of('end', period, now)
    if end is None:
        return None
    if unit == 'days':
        number = (end.date() - now.date()).days
    elif unit == 'weekdays':
        number = sum(1 for offset in range(1, (end.date() - now.date()).days + 1)
                     if (now.date() + dt.timedelta(days=offset)).weekday() < 5)
    elif unit == 'weeks':
        number = round((end.date() - now.date()).days / 7.0, 1)
    else:
        seconds = (end - now).total_seconds() + 1
        number = int(seconds // SECONDS[unit[:-1]])
    if unit == 'weekdays':
        word = 'workday' if number == 1 else 'workdays'
    else:
        word = unit[:-1] if number == 1 else unit
        word = ctx.text('time', word, word)
    title = '%s %s' % (ctx.fmt(number), word)
    template = ctx.text('time', 'left_subtitle', '') or 'Left until %s'
    return [item(title, template % php_date('j F Y', end, ctx), arg=ctx.fmt(number))]


def keyword(ctx, query, now=None):
    settings = ctx.settings
    zone = settings.timezone
    now = (now or dt.datetime.now(zone)).astimezone(zone).replace(microsecond=0)
    strings = ctx.lang.section('time')
    invalid = [message('...', strings.get('notvalid_subtitle') or 'Enter a valid date')]
    text = translate(ctx, query or '')
    month_first = settings.month_first

    if not text or text in ('now', 'time'):
        return _instant_rows(ctx, Parsed(now, True, None), now, True)

    # "week 44 2026", "week 44", "week": ISO weeks
    week = re.match(r'^(?:week|wk)(?: ?(\d{1,2})(?: (\d{4}))?)?$', text)
    if week:
        year, number, _ = now.isocalendar()
        if week.group(1):
            number = int(week.group(1))
            year = int(week.group(2)) if week.group(2) else now.year
        return _week_rows(ctx, year, number, now) or invalid

    left = _LEFT.match(text)
    if left:
        return _left_rows(ctx, left.group(1), left.group(2), now) or invalid

    # two dates: the time between them
    if ' - ' in text:
        left, right = [part.strip() for part in text.split(' - ', 1)]
        if left and right and not _RELATIVE_ONLY.match(right):
            first = parse(left, now, zone, month_first)
            second = parse(right, now, zone, month_first)
            if not first or not second:
                return invalid
            span = timespan(ctx, first.moment, second.moment)
            subtitle = (strings.get('difference_subtitle') or 'Time difference between %s and %s') % (
                first.moment.strftime('%Y-%m-%d %H:%M:%S'), second.moment.strftime('%Y-%m-%d %H:%M:%S'))
            rows = [item(span, subtitle, arg=span)]
            days = abs((second.moment - first.moment).total_seconds()) / 86400.0
            if days >= 7:
                total = '%s %s' % (ctx.fmt(round(days, 2)), ctx.text('time', 'days', 'days'))
                rows.append(item(total, subtitle, arg=total))
            return rows

    # "days until 31 december", "hours since yesterday"
    for name, since in (('until', False), ('since', True)):
        found = _phrase_match(ctx, name, text, leading=False)
        if found and found[0] in UNIT_WORDS and found[1]:
            target = _edge_moment(ctx, found[1], now)
            if target is None:
                target = parse(found[1], now, zone, month_first)
                if not target:
                    return invalid
                target = _nearest_year(found[1], target, now, since)
            counted = _until(ctx, found[0], target, now, since)
            if not counted:
                return invalid
            number, word = counted
            title = '%s %s' % (ctx.fmt(number), word)
            template = strings.get('since_subtitle' if since else 'until_subtitle') or '%s until %s'
            when = php_date('j F Y, H:i' if target.has_time else 'j F Y', target.moment, ctx)
            return [item(title, template % (word, when), arg=ctx.fmt(number))]

    # "start of year", "end of 2021", "end of next month"
    for name, kind in (('end of', 'end'), ('start of', 'start')):
        found = _phrase_match(ctx, name, text, leading=True)
        if found is not None:
            if not found[1]:
                return invalid
            moment = _edge_of(kind, found[1], now)
            if moment is None:
                rest = parse(found[1], now, zone, month_first)
                if not rest:
                    return invalid
                moment = rest.moment
            return _instant_rows(ctx, Parsed(moment, True, None), now, False)

    # a bare number is a Unix timestamp (13 digits: milliseconds); four digits read as a year
    if re.match(r'^-?\d+$', text) and not re.match(r'^\d{4}$', text):
        number = int(text)
        if len(text.lstrip('-')) >= 12:
            number = number / 1000.0
        try:
            moment = dt.datetime.fromtimestamp(number, dt.timezone.utc).astimezone(zone)
        except (OverflowError, OSError, ValueError):
            return invalid
        return _instant_rows(ctx, Parsed(moment.replace(microsecond=0), True, None), now, False)

    parsed = parse(text, now, zone, month_first)
    if not parsed:
        return invalid
    return _instant_rows(ctx, parsed, now, False)
