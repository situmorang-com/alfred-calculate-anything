# -*- coding: utf-8 -*-
"""Decides which calculator answers a query and shapes the reply Alfred expects."""
import re

from .core import Context, NUMBER, clean_query, message, split_amount


def auto(ctx, query):
    """Queries typed with no keyword. They always start with a number, and the first
    calculator that recognises the rest wins (order matters: "12 pt to l" is a pint)."""
    ctx.typed = clean_query(query, lower=False)
    query = clean_query(query)
    if len(query) < 3:
        return []
    head = query[1:2] if query[0] in '-+' else query[0]
    if not (head.isdigit() or (head == '.' and len(query) > 1)):
        return []
    from . import bases, datastorage, money, percentage, pxemrem, units, vat
    for tool in (units, bases, percentage, pxemrem, vat, datastorage, money):
        rows = tool.process(ctx, query)
        if rows is not None:
            return rows
    return []


_FIRST_NUMBER = re.compile(r'[-+]?(?:\d|[.,]\d)')
_DATE_WORDS = re.compile(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b|^\d{4}-\d{2}-\d{2}')


def selection_query(ctx, text):
    """Text from anywhere, reshaped the way the calculators read it.

    "Rp 1.500.000" -> "1.500.000 rp", "USD 100 to IDR" -> "100 usd to idr",
    "costs about $25." -> "25 $". Words before the amount are dropped, unless the word
    right before it is a currency ("$", "Rp", "usd") or a well-known coin.
    """
    text = clean_query(text).rstrip('.,;:!?)')
    match = _FIRST_NUMBER.search(text)
    if not match:
        return text
    before, rest = text[:match.start()].rstrip(), text[match.start():]
    candidate = before.split(' ')[-1] if before else ''
    if candidate:
        from .money import Money
        if Money(ctx).resolve(candidate):
            amount = split_amount(rest)
            if amount:
                number, after = amount
                return ' '.join(part for part in (number, candidate, after) if part)
    return rest


def selection(ctx, text):
    """The `calc` keyword, the Universal Action and the hotkey: whatever text arrives."""
    raw = clean_query(text)
    if not raw:
        return [message('Calculate Anything', 'Type or select an amount, for example $25, Rp 1.500.000 or 100 usd to idr')]
    from . import color, timecalc
    if color.parse_color(raw) is not None:
        return color.keyword(ctx, raw)
    query = selection_query(ctx, raw)
    rows = auto(ctx, query)
    if rows:
        return rows
    if re.fullmatch(r'\d{10}|\d{13}', query) or _DATE_WORDS.search(raw):
        rows = timecalc.keyword(ctx, raw)
        if rows and rows[0].get('valid') is not False:
            return rows
    if re.fullmatch(NUMBER, query):
        return [message('Add a unit or currency after the number',
                        'For example: %s idr, %s km to miles' % (query, query))]
    return [message("Calculate Anything can't read this", 'Try a number and a unit, for example 100 usd to idr')]


def run(action, query, environ=None):
    ctx = Context(environ)
    if action == 'vat':
        from . import vat
        rows = vat.keyword(ctx, clean_query(query))
    elif action == 'time':
        from . import timecalc
        rows = timecalc.keyword(ctx, query)
    elif action == 'color':
        from . import color
        rows = color.keyword(ctx, query)
    elif action == 'any':
        rows = selection(ctx, query)
    elif action == 'symbol':
        rows = auto(ctx, selection_query(ctx, query))      # "$100 to idr", typed with no keyword
    else:
        rows = auto(ctx, query)
    response = {'items': rows or []}
    if ctx.rerun:
        response['rerun'] = ctx.rerun
    if ctx.variables:
        response['variables'] = ctx.variables
    return response
