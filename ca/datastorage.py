# -*- coding: utf-8 -*-
"""Data storage sizes.

    100 gigabytes in megabytes     2 gb to mb     400MiB to kib     2tb gb     1b kb

Follows the IEC standard: 1 MB = 1000 kB and 1 MiB = 1024 KiB. The "Binary mode"
setting makes the decimal names binary as well (1 MB = 1024 kB), as many people expect.
"""
from .core import item, lookup, mod, parse_number, plain_number, split_amount, term_splits

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


def process(ctx, query):
    parts = split_amount(query)
    if not parts or not parts[1]:
        return None
    number, rest = parts
    index = build_index(ctx.lang)
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
