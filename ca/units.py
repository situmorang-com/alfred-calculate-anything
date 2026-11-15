# -*- coding: utf-8 -*-
"""Unit conversion.

    100 kilometers to meters    100 km m       100oz = kg     -25F to C
    10 years to months          1hr s          100 ml to oz   4500 ft2 to m2
    100 kg    72 f    2 cups    no target: the Default units setting, else the other system
    5'11" to cm    5 ft 11 in   2 h 30 min to min      parts of one kind are added up
    1/8 in to mm   1 1/2 cups   fractions (from core.split_amount)
    145 min to timespan         a duration in words and as h:mm:ss
    100 mbps to mb/s            data rates; see rate_unit for bits and bytes

Each category has a base unit; every other unit is "how many base units is one of
me" (temperature and fuel economy need functions instead of a factor).
"""
import math
import re

from .core import FRACTION_NUMBER, NUMBER, item, lookup, message, mod, parse_number, plain_digits, plain_number, \
    split_amount, term_splits

UNITS = {
    'length': {
        'm': 1.0, 'km': 1000.0, 'dm': 0.1, 'cm': 0.01, 'mm': 0.001,
        'μm': 1e-6, 'nm': 1e-9, 'pm': 1e-12,
        'in': 0.0254, 'ft': 0.3048, 'yd': 0.9144, 'mi': 1609.344, 'nmi': 1852.0,
        'fur': 201.168, 'ftm': 1.8288,
        'hh': 0.1016,                   # hand, for horses
        'ly': 9460730472580800.0,       # light year
        'au': 149597870700.0,           # astronomical unit
        'pc': 30856775814913673.0,      # parsec
    },
    'area': {
        'm2': 1.0, 'km2': 1e6, 'cm2': 1e-4, 'mm2': 1e-6,
        'in2': 0.00064516, 'ft2': 0.09290304, 'yd2': 0.83612736, 'mi2': 2589988.110336,
        'ac': 4046.8564224, 'ha': 10000.0, 'are': 100.0,
        'tumbak': 14.0,                 # Indonesian land measure (also bata, ru); it varies by region
    },
    'volume': {
        'l': 1.0, 'dm3': 1.0, 'ml': 0.001, 'cl': 0.01, 'dl': 0.1, 'cm3': 0.001, 'hl': 100.0, 'kl': 1000.0,
        'm3': 1000.0,
        'pt': 0.473176473, 'uspt': 0.473176473, 'ukpt': 0.56826125,
        'gal': 3.785411784, 'usgal': 3.785411784, 'ukgal': 4.54609,
        'qt': 0.946352946, 'usqt': 0.946352946, 'ukqt': 1.1365225,
        'yd3': 764.554857984, 'ft3': 28.316846592, 'in3': 0.016387064,
        'floz': 0.0295735295625, 'ukfloz': 0.0284130625,
        'cup': 0.2365882365, 'tbsp': 0.01478676478125, 'tsp': 0.00492892159375,
    },
    'weight': {
        'kg': 1.0, 'g': 0.001, 'mg': 1e-6, 'μg': 1e-9,
        'N': 1 / 9.80665,               # newton, as the weight of a mass on Earth
        'st': 6.35029318, 'lb': 0.45359237, 'oz': 0.028349523125,
        'ozt': 0.0311034768,            # troy ounce, for gold and silver
        'ct': 0.0002,                   # carat, for gems
        't': 1000.0, 'ukt': 1016.0469088, 'ust': 907.18474,
        'ons': 0.1, 'kuintal': 100.0,   # Indonesian: 1 ons = 100 g, 1 kuintal = 100 kg
    },
    'speed': {
        'mps': 1.0, 'kph': 1 / 3.6, 'mph': 0.44704, 'fps': 0.3048, 'knot': 1852.0 / 3600.0,
    },
    'rotation': {
        'deg': 1.0, 'rad': 180.0 / math.pi, 'arcmin': 1 / 60.0, 'arcsec': 1 / 3600.0, 'rev': 360.0,
        'grad': 0.9,
    },
    'temperature': {
        'k': 1.0,
        'c': (lambda value: value + 273.15, lambda kelvin: kelvin - 273.15),
        'f': (lambda value: (value + 459.67) * 5.0 / 9.0, lambda kelvin: kelvin * 9.0 / 5.0 - 459.67),
    },
    'pressure': {
        'pa': 1.0, 'hpa': 100.0, 'kpa': 1000.0, 'mpa': 1e6, 'bar': 1e5, 'mbar': 100.0,
        'psi': 6894.757293168, 'atm': 101325.0, 'torr': 101325.0 / 760.0, 'mmhg': 133.322387415,
        'inhg': 3386.389,
    },
    'time': {
        's': 1.0, 'year': 31536000.0, 'month': 2628000.0, 'week': 604800.0, 'day': 86400.0,
        'hr': 3600.0, 'min': 60.0, 'ms': 1e-3, 'μs': 1e-6, 'ns': 1e-9,
        'fortnight': 1209600.0, 'decade': 315360000.0, 'century': 3153600000.0,
    },
    'energy': {
        'j': 1.0, 'kj': 1000.0, 'mj': 1e6, 'cal': 4.184, 'kcal': 4184.0,
        'Nm': 1.0, 'ftlb': 1.3558179483314004,
        'whr': 3600.0, 'kwhr': 3.6e6, 'mwhr': 3.6e9, 'gwhr': 3.6e12, 'twhr': 3.6e15,
        'ev': 1.602176634e-19, 'mev': 1.602176634e-13, 'btu': 1055.05585262,
    },
    'power': {
        'w': 1.0, 'kw': 1000.0, 'MW': 1e6, 'GW': 1e9, 'ps': 735.49875, 'hp': 745.69987158227022,
        'btu/h': 0.29307107017222,
    },
    'frequency': {
        'Hz': 1.0, 'kHz': 1e3, 'MHz': 1e6, 'GHz': 1e9, 'THz': 1e12,
        'rpm': 1 / 60.0, 'rps': 1.0, 'rad/s': 1 / (2 * math.pi),
    },
    'force': {
        'N': 1.0, 'kN': 1000.0, 'lbf': 4.4482216152605, 'kgf': 9.80665,
    },
    'acceleration': {
        'm/s2': 1.0, 'ft/s2': 0.3048, 'gn': 9.80665,        # gn: standard gravity, typed "g"
    },
    'fuel': {
        'km/l': 1.0,
        'l/100km': (lambda value: 100.0 / value, lambda base: 100.0 / base),
        'mpg': 1.609344 / 3.785411784, 'ukmpg': 1.609344 / 4.54609,
    },
    'datarate': {
        'bit/s': 1.0, 'kbit/s': 1e3, 'Mbit/s': 1e6, 'Gbit/s': 1e9, 'Tbit/s': 1e12,
        'B/s': 8.0, 'kB/s': 8e3, 'MB/s': 8e6, 'GB/s': 8e9, 'TB/s': 8e12,
        'KiB/s': 8 * 1024.0, 'MiB/s': 8 * 1024.0 ** 2, 'GiB/s': 8 * 1024.0 ** 3,
    },
    'screen': {
        'ppi': 1.0, 'ppcm': 2.54,
    },
}

# Abbreviations people use that already mean something else in another category.
# Only tried when the obvious reading cannot be converted ("90 m to hr", "100 ml to oz").
# The last field says whether the reading also counts for an amount with no target:
# "12 oz" shows grams and millilitres, but "2 tb" is two terabytes, not tablespoons.
FALLBACKS = [
    ('m', 'time', 'min', False),
    ('d', 'time', 'day', False),
    ('w', 'time', 'week', False),
    ('oz', 'volume', 'floz', True),
    ('tb', 'volume', 'tbsp', False),
]

# Larger unit -> the smaller one used for the second "7 ft, 4 in" style row.
FRACTION = {
    'm': 'cm', 'km': 'm', 'dm': 'cm', 'cm': 'mm', 'mm': 'μm', 'μm': 'nm', 'nm': 'pm',
    'ft': 'in', 'yd': 'in', 'mi': 'ft',
    'l': 'ml', 'pt': 'floz', 'uspt': 'floz', 'ukpt': 'ukfloz',
    'gal': 'qt', 'qt': 'pt', 'usqt': 'uspt', 'ukqt': 'ukpt', 'usgal': 'usqt', 'ukgal': 'ukqt',
    'kg': 'g', 'g': 'mg', 'st': 'lb', 'lb': 'oz',
    'hr': 'min', 'min': 's', 'day': 'hr', 'week': 'day', 'fortnight': 'day', 'year': 'month',
}

# An amount typed with no target ("100 kg") converts to these, unless the Default units
# setting names a unit of the same kind. Units not listed (time, angles, frequencies,
# prefixes of one system such as mg) give no rows, so ordinary searches stay untouched.
DEFAULTS = {
    'km': ['mi'], 'm': ['ft'], 'cm': ['in', 'ft'], 'mm': ['in'], 'mi': ['km'], 'yd': ['m'],
    'ft': ['m', 'cm'], 'in': ['cm'], 'nmi': ['km', 'mi'], 'hh': ['cm'], 'fur': ['m'], 'ftm': ['m'],
    'm2': ['ft2'], 'km2': ['mi2'], 'cm2': ['in2'], 'mm2': ['in2'], 'in2': ['cm2'], 'ft2': ['m2'],
    'yd2': ['m2'], 'mi2': ['km2'], 'ac': ['ha', 'm2'], 'ha': ['ac', 'm2'], 'are': ['m2'], 'tumbak': ['m2'],
    'l': ['gal'], 'ml': ['floz'], 'cl': ['floz'], 'dl': ['cup'], 'm3': ['ft3'], 'cm3': ['in3'],
    'gal': ['l'], 'usgal': ['l'], 'ukgal': ['l'], 'qt': ['l'], 'usqt': ['l'], 'ukqt': ['l'],
    'pt': ['ml'], 'uspt': ['ml'], 'ukpt': ['ml'], 'floz': ['ml'], 'ukfloz': ['ml'], 'cup': ['ml'], 'tbsp': ['ml'],
    'tsp': ['ml'], 'ft3': ['m3'], 'in3': ['cm3'], 'yd3': ['m3'],
    'kg': ['lb'], 'g': ['oz'], 't': ['lb'], 'lb': ['kg'], 'oz': ['g'], 'st': ['kg'], 'ukt': ['t'],
    'ust': ['t'], 'ozt': ['g'], 'ct': ['g'], 'ons': ['g'], 'kuintal': ['kg'],
    'kph': ['mph'], 'mph': ['kph'], 'mps': ['kph'], 'fps': ['mps'], 'knot': ['kph', 'mph'],
    'c': ['f'], 'f': ['c'], 'k': ['c'],
    'psi': ['bar', 'kpa'], 'bar': ['psi'], 'kpa': ['psi'], 'atm': ['kpa'], 'mmhg': ['kpa'],
    'inhg': ['hpa'], 'hpa': ['inhg'],
    'kcal': ['kj'], 'kj': ['kcal'], 'kwhr': ['mj'], 'btu': ['kj'],
    'hp': ['kw'], 'kw': ['hp'], 'ps': ['kw'], 'btu/h': ['w'],
    'km/l': ['l/100km', 'mpg'], 'l/100km': ['km/l', 'mpg'], 'mpg': ['km/l', 'l/100km'],
    'ukmpg': ['km/l', 'l/100km'],
    'N': ['lbf'], 'kN': ['lbf'], 'lbf': ['N'], 'kgf': ['N'],
    'bit/s': ['B/s'], 'kbit/s': ['kB/s'], 'Mbit/s': ['MB/s'], 'Gbit/s': ['MB/s'], 'Tbit/s': ['GB/s'],
    'B/s': ['bit/s'], 'kB/s': ['kbit/s'], 'MB/s': ['Mbit/s'], 'GB/s': ['Gbit/s'], 'TB/s': ['Tbit/s'],
    'KiB/s': ['kbit/s'], 'MiB/s': ['Mbit/s'], 'GiB/s': ['Gbit/s'],
    'ppi': ['ppcm'], 'ppcm': ['ppi'],
}

# Typed alone these usually mean something else: 10k (ten thousand), 1t (a trillion),
# 1st (first), 12pt (a font size), 1n. A set of categories skips only those readings:
# "10 kn" is ten knots, not kilonewtons.
BARE_SKIP = {'k': None, 't': None, 'st': None, 'pt': None, 'n': None, 'kn': {'force'}}

# The other side of a no-target row worth a "5 ft, 10.87 in" row too.
BARE_MIXED = frozenset(['ft', 'lb', 'st'])

# How a unit is written in results; anything not listed is shown as its key.
DISPLAY = {
    'c': '°C', 'f': '°F', 'k': 'K', 'hh': 'hands',
    'm2': 'm²', 'km2': 'km²', 'cm2': 'cm²', 'mm2': 'mm²',
    'in2': 'in²', 'ft2': 'ft²', 'yd2': 'yd²', 'mi2': 'mi²',
    'm3': 'm³', 'cm3': 'cm³', 'dm3': 'dm³', 'yd3': 'yd³', 'ft3': 'ft³', 'in3': 'in³',
    'floz': 'fl oz', 'ukfloz': 'UK fl oz', 'uspt': 'US pt', 'ukpt': 'UK pt',
    'usgal': 'US gal', 'ukgal': 'UK gal', 'usqt': 'US qt', 'ukqt': 'UK qt',
    'ukt': 'UK long tons', 'ust': 'US short tons', 'ozt': 'oz t',
    'mps': 'm/s', 'kph': 'km/h', 'fps': 'ft/s', 'knot': 'kn',
    'j': 'J', 'kj': 'kJ', 'mj': 'MJ', 'whr': 'Wh', 'kwhr': 'kWh', 'mwhr': 'MWh', 'gwhr': 'GWh', 'twhr': 'TWh',
    'ev': 'eV', 'mev': 'MeV', 'btu': 'BTU', 'ftlb': 'ft⋅lb',
    'pa': 'Pa', 'hpa': 'hPa', 'kpa': 'kPa', 'mpa': 'MPa', 'mmhg': 'mmHg', 'inhg': 'inHg',
    'w': 'W', 'kw': 'kW', 'ps': 'PS', 'btu/h': 'BTU/h',
    'm/s2': 'm/s²', 'ft/s2': 'ft/s²', 'gn': 'g',
    'l/100km': 'l/100 km', 'ukmpg': 'UK mpg',
}

# Time results read better as words: "240 hours", not "240 hr".
TIME_WORDS = {
    'ns': ('nanosecond', 'nanoseconds'), 'μs': ('microsecond', 'microseconds'),
    'ms': ('millisecond', 'milliseconds'), 's': ('second', 'seconds'), 'min': ('minute', 'minutes'),
    'hr': ('hour', 'hours'), 'day': ('day', 'days'), 'week': ('week', 'weeks'),
    'fortnight': ('fortnight', 'fortnights'), 'month': ('month', 'months'), 'year': ('year', 'years'),
    'decade': ('decade', 'decades'), 'century': ('century', 'centuries'),
}

# Data rates whose case decides between bits and bytes: "Mb/s" and "Mbps" are megabits,
# "MB/s" and "MBps" megabytes. Typed all in one case, "mbps" (or "MBPS") is megabits and
# "mb/s" megabytes, as "mb" is a megabyte everywhere else in this workflow.
_RATE = re.compile(r'^(k|m|g|t)?(b)(ps|/s)$', re.I)
_RATE_PREFIX = {'': '', 'k': 'k', 'm': 'M', 'g': 'G', 't': 'T'}


def rate_unit(cased):
    """The data-rate unit a term means, judged by its case, or None to look it up as usual."""
    match = _RATE.match(cased or '')
    if not match:
        return None
    prefix, letter, tail = match.group(1) or '', match.group(2), match.group(3).lower()
    if cased.islower() or cased.isupper():
        in_bytes = tail == '/s'
    else:
        in_bytes = letter == 'B'
    return _RATE_PREFIX[prefix.lower()] + ('B/s' if in_bytes else 'bit/s')


def category_of(unit):
    for category, table in UNITS.items():
        if unit in table:
            return category
    return None


def convert(amount, from_unit, to_unit, category=None):
    table = UNITS[category or category_of(from_unit)]
    source, target = table[from_unit], table[to_unit]
    base = source[0](amount) if isinstance(source, tuple) else amount * source
    return target[1](base) if isinstance(target, tuple) else base / target


def build_index(lang):
    """Everything a user may type for a unit -> [(category, unit), ...], best guess first."""
    index = {}
    exact = {}
    by_key = {}

    def add(alias, category, unit):
        entries = index.setdefault(alias, [])
        if (category, unit) not in entries:
            entries.append((category, unit))

    for category, table in UNITS.items():
        for unit in table:
            add(unit.lower(), category, unit)
            exact.setdefault(unit, []).append((category, unit))
            by_key.setdefault(unit.lower(), []).append((category, unit))
    for alias, target in lang.keywords('units').items():
        target = str(target)
        # "newton meters" -> "Nm" must not also mean nanometers, so exact case wins
        for category, unit in exact.get(target) or by_key.get(target.lower(), ()):
            add(alias, category, unit)
    for alias, category, unit, _ in FALLBACKS:
        add(alias, category, unit)
    return index


def resolve(index, term):
    found = lookup(index, term)
    if not found and len(term) > 2 and term.endswith('s'):
        found = lookup(index, term[:-1])     # "kms", "hrs", "gals"
    return found or []


def is_unit_term(lang, term):
    """Used by the currency parser to avoid reading "100 km" as some obscure coin."""
    return bool(resolve(build_index(lang), term))


def unit_label(ctx, unit, category, value):
    if category == 'time' and unit in TIME_WORDS:
        singular, plural = TIME_WORDS[unit]
        word = singular if abs(value - 1) < 1e-12 else plural
        return ctx.text('time', word, word)
    return DISPLAY.get(unit, unit)


def duration_text(ctx, seconds):
    """8700 -> "2 hours, 25 minutes": years of 365 days, days, hours, minutes, seconds."""
    seconds = abs(float(seconds))
    parts = []
    for unit, size in (('year', 31536000.0), ('day', 86400.0), ('hr', 3600.0), ('min', 60.0)):
        count = math.floor(seconds / size + 1e-9)
        if count:
            parts.append((count, unit))
            seconds = max(0.0, seconds - count * size)
    seconds = round(seconds, 2)
    if seconds >= 0.005 or not parts:
        parts.append((seconds, 's'))
    return ', '.join('%s %s' % (ctx.fmt(count), unit_label(ctx, unit, 'time', count)) for count, unit in parts[:4])


def clock_text(seconds):
    """8700 -> "2:25:00"."""
    whole = int(round(abs(float(seconds))))
    return '%d:%02d:%02d' % (whole // 3600, whole % 3600 // 60, whole % 60)


# ------------------------------------------------------------------ reading the query

_NUMBER_TOKEN = re.compile(r'^(?:%s|%s)$' % (FRACTION_NUMBER, NUMBER))


def _candidates(ctx, index, term, last=False):
    """resolve(), with the case of data rates as typed taken into account."""
    special = rate_unit(ctx.cased(term, last))
    if special:
        return [('datarate', special)]
    return resolve(index, term)


def _bare_candidates(ctx, index, term):
    """The readings that count for an amount with no target."""
    skip = BARE_SKIP.get(term, ())
    if skip is None:
        return []
    blocked = set((category, unit) for alias, category, unit, bare in FALLBACKS
                  if not bare and alias in (term, term[:-1] if term.endswith('s') else term))
    return [(category, unit) for category, unit in _candidates(ctx, index, term)
            if category not in skip and (category, unit) not in blocked]


def _compound(ctx, index, query):
    """"5 ft 11 in to cm" -> (5.9166, 'length', 'ft', 'to cm'); None unless the query starts
    with at least two number-and-unit parts of one kind. A bare last number takes the
    smaller unit ("5'11", "2 h 30")."""
    text = re.sub(r"(\d)\s*(ft|['′])\s*(?=\d)", r"\1 \2 ", query)       # 5'11" -> 5 ' 11"
    text = re.sub(r"(\d)(['\"′″])", r"\1 \2", text)
    text = re.sub(r'(\d)([a-zμ°])', r'\1 \2', text)
    tokens = text.split()
    parts = []
    position = 0
    while position < len(tokens) and _NUMBER_TOKEN.match(tokens[position]):
        number = tokens[position]
        position += 1
        if position < len(tokens) and '/' in tokens[position] and '/' not in number \
                and _NUMBER_TOKEN.match(tokens[position]):
            number += ' ' + tokens[position]                                # 3 1/2
            position += 1
        end = position
        while end < len(tokens) and not _NUMBER_TOKEN.match(tokens[end]):
            end += 1
        parts.append((number, tokens[position:end]))
        position = end
    if len(parts) < 2 or position < len(tokens):
        return None
    category, first_unit, total, previous = None, None, 0.0, None
    for number, words in parts[:-1]:
        found = [pair for pair in resolve(index, ' '.join(words)) if category in (None, pair[0])]
        if not words or not found:
            return None
        category, unit = found[0]
        if first_unit is None:
            first_unit = unit
        total += convert(parse_number(number, ctx.settings), unit, first_unit, category)
        previous = unit
    number, words = parts[-1]
    amount = parse_number(number, ctx.settings)
    if not words:
        smaller = FRACTION.get(previous)
        if not smaller:
            return None
        return total + convert(amount, smaller, first_unit, category), category, first_unit, ''
    stops = ctx.lang.stop_words('units')
    for from_term, to_term, had_stop in term_splits(' '.join(words), stops):
        found = [pair for pair in resolve(index, from_term) if pair[0] == category]
        if found:
            total += convert(amount, found[0][1], first_unit, category)
            rest = to_term if not had_stop or not to_term else 'to ' + to_term
            return total, category, first_unit, rest
    return None


def process(ctx, query):
    index = build_index(ctx.lang)
    compound = _compound(ctx, index, query)
    if compound:
        amount, category, unit, rest = compound
        target = rest[3:] if rest.startswith('to ') else rest
        if not target:
            return _bare_rows(ctx, index, amount, [(category, unit)]) or None
        if _is_timespan(ctx, target) and category == 'time':
            return _timespan_rows(ctx, amount, unit)
        targets = [pair for pair in _candidates(ctx, index, target, last=True) if pair[0] == category]
        if not targets:
            return None
        return _rows(ctx, amount, unit, targets[0][1], category)

    parts = split_amount(query)
    if not parts or not parts[1]:
        return None
    number, rest = parts
    mismatch = None
    bare = None
    for from_term, to_term, _ in term_splits(rest, ctx.lang.stop_words('units')):
        if not to_term:
            if bare is None and (rest == from_term or rest.startswith(from_term + ' ')):
                bare = from_term
            continue
        sources = _candidates(ctx, index, from_term)
        if not sources:
            continue
        if _is_timespan(ctx, to_term):
            for category, source in sources:
                if category == 'time':
                    return _timespan_rows(ctx, parse_number(number, ctx.settings), source)
            continue
        targets = _candidates(ctx, index, to_term, last=True)
        if not targets:
            continue
        for category, source in sources:
            for target_category, target in targets:
                if category == target_category:
                    # None: the units fit but the number does not ("0 l/100km to km/l")
                    return _rows(ctx, parse_number(number, ctx.settings), source, target, category)
        if mismatch is None:
            mismatch = (sources[0][1], targets[0][1])
    if mismatch:
        template = ctx.text('units', 'error', 'Error, you can not convert from %s to %s')
        return [message(template % (DISPLAY.get(mismatch[0], mismatch[0]), DISPLAY.get(mismatch[1], mismatch[1])))]
    if bare:
        rows = _bare_rows(ctx, index, parse_number(number, ctx.settings), _bare_candidates(ctx, index, bare))
        if rows:
            return rows
    return None


def _is_timespan(ctx, term):
    return term == 'timespan' or lookup(ctx.lang.keywords('units'), term) == 'timespan'


def _preferred(ctx, index):
    """The Default units setting, read as [(category, unit), ...]."""
    chosen = []
    for word in re.split(r'[,;]+', ctx.settings.default_units or ''):
        word = word.strip().lower()
        if word:
            found = resolve(index, word.replace('²', '2').replace('³', '3'))
            if found and found[0] not in chosen:
                chosen.append(found[0])
    return chosen


def _bare_rows(ctx, index, amount, candidates):
    """Rows for an amount typed with no target ("100 kg", "72 f")."""
    preferred = _preferred(ctx, index)
    rows = []
    for category, unit in candidates:
        mine = [target for kind, target in preferred if kind == category and target != unit]
        targets = mine or [target for target in DEFAULTS.get(unit, ()) if target in UNITS[category]]
        for target in targets:
            found = _rows(ctx, amount, unit, target, category, mixed=target in BARE_MIXED)
            rows.extend(found or [])
        if len(rows) >= 4:
            break
    return rows[:4]


def _timespan_rows(ctx, amount, unit):
    seconds = convert(amount, unit, 's', 'time')
    words, clock = duration_text(ctx, seconds), clock_text(seconds)
    hint = ctx.text('general', 'action_copy')
    return [item(words, hint, arg=words), item(clock, hint, arg=clock)]


def _rows(ctx, amount, source, target, category, mixed=True):
    try:
        converted = convert(amount, source, target, category)
    except (ZeroDivisionError, OverflowError, ValueError):
        return None
    if not math.isfinite(converted):
        return None
    decimals = 2 if category == 'temperature' else -1
    value = ctx.fmt(converted, decimals)
    label = unit_label(ctx, target, category, converted)
    with_unit = value + ' ' + label
    copy_hint = ctx.text('general', 'action_copy')
    plain_hint = ctx.text('units', 'cmd')
    unit_hint = ctx.text('units', 'alt')
    rows = [item(with_unit, copy_hint, arg=value, mods={
        'cmd': mod(plain_number(converted, decimals), plain_hint),
        'alt': mod(with_unit, unit_hint),
    })]

    smaller = FRACTION.get(target) if mixed else None
    if smaller and converted > 0 and '.' in plain_digits(converted):
        whole = math.floor(converted + 1e-9)
        remainder = round(convert(converted - whole, target, smaller, category), 2)
        per_whole = convert(1.0, target, smaller, category)
        # beyond about 15 digits the fraction is float noise ("1 ly km" would add 800.78 m)
        precise = math.ulp(converted) * per_whole < 0.005
        if whole >= 1 and 0 < remainder < per_whole and precise:
            text = '%s %s, %s %s' % (
                ctx.fmt(whole, 0), unit_label(ctx, target, category, whole),
                ctx.fmt(remainder, -1), unit_label(ctx, smaller, category, remainder))
            rows.append(item(text, copy_hint, arg=text, mods={
                'cmd': mod(plain_number(converted, decimals), plain_hint),
                'alt': mod(text, unit_hint),
            }))
    return rows
