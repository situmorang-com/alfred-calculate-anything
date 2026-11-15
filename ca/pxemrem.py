# -*- coding: utf-8 -*-
"""CSS sizes: px, em, rem, pt.

    12px                     0.75em, 0.75rem, 9pt
    12px to em               0.75em
    2rem to pt               24pt
    12px in em base 17px     0.70588em
"""
import re

from .core import NUMBER, item, parse_number, plain_number

UNITS = ('px', 'em', 'rem', 'pt')
POINTS_PER_PIXEL = 0.75


def _convert(amount, source, target, base):
    relative = ('em', 'rem')
    if source == target or (source in relative and target in relative):
        return amount
    pixels = amount * base if source in relative else (amount / POINTS_PER_PIXEL if source == 'pt' else amount)
    if target == 'px':
        return pixels
    if target == 'pt':
        return pixels * POINTS_PER_PIXEL
    return pixels / base


def process(ctx, query):
    match = re.match(r'^(%s) ?(px|em|rem|pt)\b(.*)$' % NUMBER, query)
    if not match:
        return None
    amount = parse_number(match.group(1), ctx.settings)
    source = match.group(2)
    rest = match.group(3).strip()
    base = ctx.settings.base_pixels

    custom_base = re.search(r'\bbase ?(\d+(?:[.,]\d+)?) ?(?:px)?$', rest)
    if custom_base:
        base = parse_number(custom_base.group(1), ctx.settings) or base
        rest = rest[:custom_base.start()].strip()

    words = rest.split()
    stops = ctx.lang.stop_words('units')
    if words and words[0] in stops:
        words = words[1:]
    target = ''
    if words:
        if len(words) != 1 or words[0] not in UNITS:
            return None                       # not a font-size question after all
        target = words[0]

    targets = [target] if target else [unit for unit in UNITS if unit != source]
    hint = ctx.text('general', 'action_copy')
    rows = []
    for unit in targets:
        value = plain_number(round(_convert(amount, source, unit, base), 5)) + unit
        rows.append(item(value, hint, arg=value))
    return rows
