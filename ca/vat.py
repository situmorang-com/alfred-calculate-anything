# -*- coding: utf-8 -*-
"""Value added tax.

    vat of 400          the tax, the amount plus tax, and the amount with tax taken out
    vat 400 11%         the same with a one-off rate instead of the configured one
    400 + vat           464      (also "plus", "minus", "tax" and the local word)
"""
import re

from .core import NUMBER as _NUMBER, item, message, mod, parse_number, plain_number

MONEY_DECIMALS = 2


def _percent_text(rate):
    return plain_number(rate) + '%'


def _breakdown(ctx, amount, rate):
    lang = ctx.lang.section('vat')
    tax = amount * rate / 100.0
    plus = amount + tax
    minus = amount / (1 + rate / 100.0)
    shown_amount = ctx.fmt(amount, MONEY_DECIMALS)
    percent = _percent_text(rate)
    return {
        'tax': (tax, (lang.get('result') or 'VAT of %s = %s') % (shown_amount, ctx.fmt(tax, MONEY_DECIMALS)),
                (lang.get('subtitle') or 'VAT of %s') % percent),
        'plus': (plus, (lang.get('plus') or '%s plus VAT = %s') % (shown_amount, ctx.fmt(plus, MONEY_DECIMALS)),
                 (lang.get('plus_subtitle') or '%s plus %s of VAT') % (shown_amount, percent)),
        'minus': (minus, (lang.get('minus') or '%s minus VAT = %s') % (shown_amount, ctx.fmt(minus, MONEY_DECIMALS)),
                  (lang.get('minus_subtitle') or '%s minus %s of VAT') % (shown_amount, percent)),
    }


def _row(ctx, entry, title=None):
    value, text, subtitle = entry
    shown = ctx.fmt(value, MONEY_DECIMALS)
    return item(title or text, subtitle, arg=shown,
                mods={'cmd': mod(plain_number(value, MONEY_DECIMALS), ctx.text('vat', 'cmd'))})


def keyword(ctx, query):
    """The `vat` keyword: every figure at once."""
    numbers = re.findall(r'(%s)\s*(%%?)' % _NUMBER, query or '')
    amount = None
    rate = ctx.settings.vat_percentage
    for number, percent in numbers:
        if percent:
            rate = parse_number(number, ctx.settings)
        elif amount is None:
            amount = parse_number(number, ctx.settings)
    if not amount or amount <= 0 or rate <= 0:
        return [message('...', ctx.text('vat', 'empty', 'Enter a value to process'))]
    parts = _breakdown(ctx, amount, rate)
    return [_row(ctx, parts['tax']), _row(ctx, parts['plus']), _row(ctx, parts['minus'])]


def process(ctx, query):
    """Inline form typed without the keyword: "400 + vat", "400 minus tax"."""
    keywords = ctx.lang.keywords('vat')
    plus_words = ['+'] + [key for key, value in keywords.items() if value == '+']
    minus_words = ['-'] + [key for key, value in keywords.items() if value == '-']
    tax_words = [key for key, value in keywords.items() if str(value).upper() == 'VAT']
    local = ctx.text('vat', 'vat', 'VAT').lower()
    for word in (local, 'vat'):
        if word not in tax_words:
            tax_words.append(word)
    operators = sorted(plus_words + minus_words, key=len, reverse=True)
    pattern = r'^(%s) ?(%s) ?(?:%s)$' % (
        _NUMBER, '|'.join(re.escape(word) for word in operators),
        '|'.join(re.escape(word) for word in sorted(tax_words, key=len, reverse=True)))
    match = re.match(pattern, query)
    if not match:
        return None
    amount = parse_number(match.group(1), ctx.settings)
    if amount <= 0 or ctx.settings.vat_percentage <= 0:
        return None
    parts = _breakdown(ctx, amount, ctx.settings.vat_percentage)
    entry = parts['plus'] if match.group(2) in plus_words else parts['minus']
    return [_row(ctx, entry, title=ctx.fmt(entry[0], MONEY_DECIMALS))]
