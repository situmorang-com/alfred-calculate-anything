# -*- coding: utf-8 -*-
"""Unit conversion.

    100 kilometers to meters    100 km m       100oz = kg     -25F to C
    10 years to months          1hr s          100 ml to oz   4500 ft2 to m2

Each category has a base unit; every other unit is "how many base units is one of
me" (temperature needs functions instead of a factor).
"""
import math

from .core import item, lookup, message, mod, parse_number, plain_digits, plain_number, split_amount, term_splits

UNITS = {
    'length': {
        'm': 1.0, 'km': 1000.0, 'dm': 0.1, 'cm': 0.01, 'mm': 0.001,
        'μm': 1e-6, 'nm': 1e-9, 'pm': 1e-12,
        'in': 0.0254, 'ft': 0.3048, 'yd': 0.9144, 'mi': 1609.344, 'nmi': 1852.0,
        'h': 0.1016,                    # hand
        'ly': 9460730472580800.0,       # light year
        'au': 149597870700.0,           # astronomical unit
        'pc': 30856775814913673.0,      # parsec
    },
    'area': {
        'm2': 1.0, 'km2': 1e6, 'cm2': 1e-4, 'mm2': 1e-6,
        'in2': 0.00064516, 'ft2': 0.09290304, 'yd2': 0.83612736, 'mi2': 2589988.110336,
        'ac': 4046.8564224, 'ha': 10000.0,
    },
    'volume': {
        'l': 1.0, 'dm3': 1.0, 'ml': 0.001, 'cm3': 0.001, 'hl': 100.0, 'kl': 1000.0, 'm3': 1000.0,
        'pt': 0.473176473, 'uspt': 0.473176473, 'ukpt': 0.56826125,
        'gal': 3.785411784, 'usgal': 3.785411784, 'ukgal': 4.54609,
        'qt': 0.946352946, 'usqt': 0.946352946, 'ukqt': 1.1365225,
        'yd3': 764.554857984, 'ft3': 28.316846592, 'in3': 0.016387064,
        'floz': 0.0295735295625, 'ukfloz': 0.0284130625,
        'cup': 0.2365882365, 'tbsp': 0.01478676478125, 'tsp': 0.00492892159375,
    },
    'weight': {
        'kg': 1.0, 'g': 0.001, 'mg': 1e-6,
        'N': 1 / 9.80665,               # newton, as the weight of a mass on Earth
        'st': 6.35029318, 'lb': 0.45359237, 'oz': 0.028349523125,
        't': 1000.0, 'ukt': 1016.0469088, 'ust': 907.18474,
    },
    'speed': {
        'mps': 1.0, 'kph': 1 / 3.6, 'mph': 0.44704, 'fps': 0.3048, 'knot': 1852.0 / 3600.0,
    },
    'rotation': {
        'deg': 1.0, 'rad': 180.0 / math.pi,
    },
    'temperature': {
        'k': 1.0,
        'c': (lambda value: value + 273.15, lambda kelvin: kelvin - 273.15),
        'f': (lambda value: (value + 459.67) * 5.0 / 9.0, lambda kelvin: kelvin * 9.0 / 5.0 - 459.67),
    },
    'pressure': {
        'pa': 1.0, 'hpa': 100.0, 'kpa': 1000.0, 'mpa': 1e6, 'bar': 1e5, 'mbar': 100.0,
        'psi': 6894.757293168, 'atm': 101325.0, 'torr': 101325.0 / 760.0, 'mmhg': 133.322387415,
    },
    'time': {
        's': 1.0, 'year': 31536000.0, 'month': 2628000.0, 'week': 604800.0, 'day': 86400.0,
        'hr': 3600.0, 'min': 60.0, 'ms': 1e-3, 'μs': 1e-6, 'ns': 1e-9,
        'decade': 315360000.0, 'century': 3153600000.0,
    },
    'energy': {
        'j': 1.0, 'kj': 1000.0, 'mj': 1e6, 'cal': 4.184, 'kcal': 4184.0,
        'Nm': 1.0, 'ftlb': 1.3558179483314004,
        'whr': 3600.0, 'kwhr': 3.6e6, 'mwhr': 3.6e9,
        'mev': 1.602176634e-13, 'btu': 1055.05585262,
    },
    'power': {
        'w': 1.0, 'kw': 1000.0, 'ps': 735.49875, 'hp': 745.69987158227022,
    },
}

# Abbreviations people use that already mean something else in another category.
# Only tried when the obvious reading cannot be converted ("2 h to min", "100 ml to oz").
FALLBACKS = [
    ('h', 'time', 'hr'),
    ('m', 'time', 'min'),
    ('d', 'time', 'day'),
    ('w', 'time', 'week'),
    ('oz', 'volume', 'floz'),
]

# Larger unit -> the smaller one used for the second "7 ft, 4 in" style row.
FRACTION = {
    'm': 'cm', 'km': 'm', 'dm': 'cm', 'cm': 'mm', 'mm': 'μm', 'μm': 'nm', 'nm': 'pm',
    'ft': 'in', 'yd': 'in', 'mi': 'ft',
    'l': 'ml', 'pt': 'floz', 'uspt': 'floz', 'ukpt': 'ukfloz',
    'gal': 'qt', 'qt': 'pt', 'usqt': 'uspt', 'ukqt': 'ukpt', 'usgal': 'usqt', 'ukgal': 'ukqt',
    'kg': 'g', 'g': 'mg', 'st': 'lb', 'lb': 'oz',
    'hr': 'min', 'min': 's', 'day': 'hr', 'week': 'day',
}

# How a unit is written in results; anything not listed is shown as its key.
DISPLAY = {
    'c': '°C', 'f': '°F', 'k': 'K', 'h': 'hands',
    'm2': 'm²', 'km2': 'km²', 'cm2': 'cm²', 'mm2': 'mm²',
    'in2': 'in²', 'ft2': 'ft²', 'yd2': 'yd²', 'mi2': 'mi²',
    'm3': 'm³', 'cm3': 'cm³', 'dm3': 'dm³', 'yd3': 'yd³', 'ft3': 'ft³', 'in3': 'in³',
    'floz': 'fl oz', 'ukfloz': 'UK fl oz', 'uspt': 'US pt', 'ukpt': 'UK pt',
    'usgal': 'US gal', 'ukgal': 'UK gal', 'usqt': 'US qt', 'ukqt': 'UK qt',
    'ukt': 'UK long tons', 'ust': 'US short tons',
    'mps': 'm/s', 'kph': 'km/h', 'fps': 'ft/s', 'knot': 'kn',
    'j': 'J', 'kj': 'kJ', 'mj': 'MJ', 'whr': 'Wh', 'kwhr': 'kWh', 'mwhr': 'MWh',
    'mev': 'MeV', 'btu': 'BTU', 'ftlb': 'ft⋅lb',
    'pa': 'Pa', 'hpa': 'hPa', 'kpa': 'kPa', 'mpa': 'MPa', 'mmhg': 'mmHg',
    'w': 'W', 'kw': 'kW', 'ps': 'PS',
}

# Time results read better as words: "240 hours", not "240 hr".
TIME_WORDS = {
    'ns': ('nanosecond', 'nanoseconds'), 'μs': ('microsecond', 'microseconds'),
    'ms': ('millisecond', 'milliseconds'), 's': ('second', 'seconds'), 'min': ('minute', 'minutes'),
    'hr': ('hour', 'hours'), 'day': ('day', 'days'), 'week': ('week', 'weeks'),
    'month': ('month', 'months'), 'year': ('year', 'years'),
    'decade': ('decade', 'decades'), 'century': ('century', 'centuries'),
}


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
    for alias, category, unit in FALLBACKS:
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


def process(ctx, query):
    parts = split_amount(query)
    if not parts or not parts[1]:
        return None
    number, rest = parts
    index = build_index(ctx.lang)
    mismatch = None
    for from_term, to_term, _ in term_splits(rest, ctx.lang.stop_words('units')):
        if not to_term:
            continue
        sources = resolve(index, from_term)
        if not sources:
            continue
        targets = resolve(index, to_term)
        if not targets:
            continue
        for category, source in sources:
            for target_category, target in targets:
                if category == target_category:
                    amount = parse_number(number, ctx.settings)
                    return _rows(ctx, amount, source, target, category)
        if mismatch is None:
            mismatch = (sources[0][1], targets[0][1])
    if mismatch:
        template = ctx.text('units', 'error', 'Error, you can not convert from %s to %s')
        return [message(template % (DISPLAY.get(mismatch[0], mismatch[0]), DISPLAY.get(mismatch[1], mismatch[1])))]
    return None


def _rows(ctx, amount, source, target, category):
    converted = convert(amount, source, target, category)
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

    smaller = FRACTION.get(target)
    if smaller and converted > 0 and '.' in plain_digits(converted):
        whole = math.floor(converted + 1e-9)
        remainder = round(convert(converted - whole, target, smaller, category), 2)
        per_whole = convert(1.0, target, smaller, category)
        if whole >= 1 and 0 < remainder < per_whole:
            mixed = '%s %s, %s %s' % (
                ctx.fmt(whole, 0), unit_label(ctx, target, category, whole),
                ctx.fmt(remainder, -1), unit_label(ctx, smaller, category, remainder))
            rows.append(item(mixed, copy_hint, arg=mixed, mods={
                'cmd': mod(plain_number(converted, decimals), plain_hint),
                'alt': mod(mixed, unit_hint),
            }))
    return rows
