# -*- coding: utf-8 -*-
"""Data storage sizes.

    100 gigabytes in megabytes     2 gb to mb     400MiB to kib     2tb gb     1b kb
    4 gb at 50 mbps                how long the transfer takes (also "over", "@")

Follows the IEC standard: 1 MB = 1000 kB and 1 MiB = 1024 KiB. The "Binary mode"
setting makes the decimal names binary as well (1 MB = 1024 kB), as many people expect.
"""
import re

from .core import NUMBER, item, lookup, mod, parse_number, plain_number, split_amount, term_splits

# "<size> at <rate>": a download or copy time.
_TRANSFER = re.compile(r'^(?P<size>.+?) (?:at|over|@|with|dengan) (?P<number>%s) ?(?P<rate>\S.*)$' % NUMBER)

# unit -> (label, name, power, binary)
SIZES = {
    'bit': ('bit', 'bit', 0, False),
    'b': ('B', 'byte', 0, False),
    'kb': ('kB', 'kilobyte', 1, False), 'mb': ('MB', 'megabyte', 2, False),
    'gb': ('GB', 'gigabyte', 3, False), 'tb': ('TB', 'terabyte', 4, False),
    'pb': ('PB', 'petabyte', 5, False), 'eb': ('EB', 'exabyte', 6, False),
    'zb': ('ZB', 'zettabyte', 7, False), 'yb': ('YB', 'yottabyte', 8, False),
    'kib': ('KiB', 'kibibyte', 1, True), 'mib': ('MiB', 'mebibyte', 2, True),
    'gib': ('GiB', 'gibibyte', 3, True), 'tib': ('TiB', 'tebibyte', 4, True),
    'pib': ('PiB', 'pebibyte', 5, True), 'eib': ('EiB', 'exbibyte', 6, True),
    'zib': ('ZiB', 'zebibyte', 7, True), 'yib': ('YiB', 'yobibyte', 8, True),
}


def bytes_per(unit, force_binary):
    if unit == 'bit':
        return 0.125
    _, _, power, binary = SIZES[unit]
    return float(1024 if (binary or force_binary) else 1000) ** power


def build_index(lang):
    index = {}
    for unit, (_, name, _, _) in SIZES.items():
        index[unit] = unit
        index[name] = unit
        index[name + 's'] = unit
    for alias, target in lang.keywords('datastorage').items():
        target = str(target).lower()
        if target in SIZES and alias not in index:
            index[alias] = target
    return index


def _transfer(ctx, index, number, rest):
    """"4 gb at 50 mbps" -> the time the transfer takes, or None."""
    match = _TRANSFER.match(rest)
    if not match:
        return None
    size = lookup(index, match.group('size'))
    if not size:
        return None
    from . import units
    rate_term = match.group('rate')
    rates = [unit for category, unit in units._candidates(ctx, units.build_index(ctx.lang), rate_term, last=True)
             if category == 'datarate']
    if not rates:
        return None
    speed = parse_number(match.group('number'), ctx.settings) * units.UNITS['datarate'][rates[0]]
    if speed <= 0:
        return None
    bits = parse_number(number, ctx.settings) * bytes_per(size, ctx.settings.force_binary) * 8
    seconds = bits / speed
    words = units.duration_text(ctx, seconds)
    subtitle = (ctx.text('datastorage', 'transfer', '') or 'Time to move %s at %s') % (
        '%s %s' % (number, SIZES[size][0]), '%s %s' % (match.group('number'), rates[0]))
    clock = units.clock_text(seconds)
    return [item(words, subtitle, arg=words), item(clock, subtitle, arg=clock)]


def process(ctx, query):
    parts = split_amount(query)
    if not parts or not parts[1]:
        return None
    number, rest = parts
    index = build_index(ctx.lang)
    transfer = _transfer(ctx, index, number, rest)
    if transfer:
        return transfer
    for from_term, to_term, _ in term_splits(rest, ctx.lang.stop_words('datastorage')):
        if not to_term:
            continue
        source = lookup(index, from_term)
        target = lookup(index, to_term)
        if not source or not target:
            continue
        amount = parse_number(number, ctx.settings)
        binary = ctx.settings.force_binary
        converted = amount * bytes_per(source, binary) / bytes_per(target, binary)
        value = ctx.fmt(converted)
        title = value + ' ' + SIZES[target][0]
        return [item(title, ctx.text('general', 'action_copy'), arg=value, mods={
            'cmd': mod(plain_number(converted), ctx.text('datastorage', 'cmd')),
            'alt': mod(title, ctx.text('units', 'alt')),
        })]
    return None
