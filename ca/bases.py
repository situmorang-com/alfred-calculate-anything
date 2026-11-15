# -*- coding: utf-8 -*-
"""Number bases.

    255 to hex      255 to binary     255 to octal     255 to base 7
    0xff            0b1010            0o17             0xff to decimal

A plain decimal number needs a target, so "255" alone stays an ordinary search.
"""
import re

from .core import item, mod

NAMES = {'hex': 16, 'hexadecimal': 16, 'binary': 2, 'bin': 2, 'octal': 8, 'oct': 8, 'decimal': 10, 'dec': 10}
PREFIX = {16: '0x', 2: '0b', 8: '0o'}
LABEL = {16: 'hexadecimal', 2: 'binary', 8: 'octal', 10: 'decimal'}
_DIGITS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
_VALUE = r'(-?)(0x[0-9a-f]{1,32}|0b[01]{1,128}|0o[0-7]{1,43}|\d{1,38})'
_TARGET = r'(%s|base ?\d{1,2})' % '|'.join(sorted(NAMES, key=len, reverse=True))


def digits(number, base):
    if number == 0:
        return '0'
    out = []
    value = abs(number)
    while value:
        value, remainder = divmod(value, base)
        out.append(_DIGITS[remainder])
    return ('-' if number < 0 else '') + ''.join(reversed(out))


def _base_of(word):
    if word in NAMES:
        return NAMES[word]
    base = int(word[4:].strip())
    return base if 2 <= base <= 36 else None


def process(ctx, query):
    stops = '|'.join(re.escape(word) for word in sorted(ctx.lang.stop_words('units'), key=len, reverse=True))
    match = re.match(r'^%s(?: (?:(?:%s) )?%s)?$' % (_VALUE, stops or 'to', _TARGET), query)
    if not match:
        return None
    sign, text, target = match.group(1), match.group(2), match.group(3)
    prefixed = text[:2] in ('0x', '0b', '0o')
    if not prefixed and not target:
        return None
    number = int(text, 0) if prefixed else int(text)
    number = -number if sign else number
    if target:
        base = _base_of(target)
        if base is None:
            return None
        bases = [base]
    else:
        bases = [10] + [base for base in (16, 2, 8) if PREFIX[base] != text[:2]]
    rows = []
    for base in bases:
        shown = digits(number, base)
        label = (LABEL.get(base) or 'base %d' % base).capitalize()
        if base in PREFIX:
            written = ('-' if number < 0 else '') + PREFIX[base] + digits(abs(number), base)
            rows.append(item(shown, '%s · ⌘ copies %s' % (label, written), arg=shown,
                             mods={'cmd': mod(written, 'Copy %s' % written)}))
        else:
            rows.append(item(shown, label, arg=shown, mods={'cmd': mod(shown, label)}))
    return rows
