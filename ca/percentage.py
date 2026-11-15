# -*- coding: utf-8 -*-
"""Percentages.

    120 + 30%            156          (and the 36 that was added)
    120 - 30%            84
    15% of 50            7.5
    40 as a % of 50      40 is 80% of 50, plus the increase/decrease between the two
    30 % 40              the same question, short form
    20% off 150          120          (and the 30 saved)
    15% tip on 80        12           (and the 92 to pay)
    15% increase from 813 / 15% decrease from 813      934.95 / 691.05 (and the 121.95)
"""
import re

from .core import NUMBER, item, mod, parse_number, plain_number

_NUMBER = r'[-+]?' + NUMBER


def _translate(ctx, query):
    """Swap the words for their symbols: "120 plus 30%" -> "120 + 30%"."""
    text = ' %s ' % query
    keywords = ctx.lang.keywords('percentage')
    for key in sorted(keywords, key=len, reverse=True):
        value = keywords[key]
        if not isinstance(value, str):
            continue
        pattern = r'(?<![^\W\d_])%s(?![^\W\d_])' % re.escape(key)
        text = re.sub(pattern, ' %s ' % value, text)
    return re.sub(r'\s+', ' ', text).strip()


def process(ctx, query):
    text = _translate(ctx, query)
    if '%' not in text[1:]:
        return None
    words = sorted(set(ctx.lang.stop_words('percentage')), key=len, reverse=True)
    operators = [r'\+', '-', '%', 'off', 'tip', 'inc', 'dec'] + [re.escape(word) for word in words]
    pattern = r'^(%s)\s*(%%?)\s*(%s)\s*(%s)\s*(%%?)$' % (_NUMBER, '|'.join(operators), _NUMBER)
    match = re.match(pattern, text)
    if not match:
        return None
    first = parse_number(match.group(1), ctx.settings)
    second = parse_number(match.group(4), ctx.settings)
    operator = match.group(3)
    lang = ctx.lang.section('percentage')
    copy_hint = ctx.text('general', 'action_copy')
    plain_hint = lang.get('alt', '')

    def row(value, subtitle=None):
        shown = ctx.fmt(value)
        return item(shown, subtitle or copy_hint, arg=shown, mods={'cmd': mod(plain_number(value), plain_hint)})

    def share_of(percent, amount):
        return (lang.get('percentage_of') or '%s of %s is %s') % (
            ctx.fmt(percent) + '%', ctx.fmt(amount), ctx.fmt(percent / 100.0 * amount))

    if operator == '+':
        portion = second / 100.0 * first
        return [row(first + portion), row(portion, share_of(second, first))]
    if operator == '-':
        portion = second / 100.0 * first
        return [row(first - portion), row(portion, share_of(second, first))]
    if operator == 'off':
        portion = first / 100.0 * second
        return [row(second - portion), row(portion, share_of(first, second))]
    if operator == 'tip':
        portion = first / 100.0 * second
        tip = (lang.get('tip') or '%s tip on %s') % (ctx.fmt(first) + '%', ctx.fmt(second))
        total = (lang.get('with_tip') or '%s with the tip') % ctx.fmt(second)
        return [row(portion, tip), row(second + portion, total)]
    if operator in ('inc', 'dec'):
        portion = first / 100.0 * second
        key, default = ('increased', '%s increased by %s') if operator == 'inc' else ('decreased', '%s decreased by %s')
        changed = (lang.get(key) or default) % (ctx.fmt(second), ctx.fmt(first) + '%')
        result = second + portion if operator == 'inc' else second - portion
        return [row(result, changed), row(portion, share_of(first, second))]
    if operator == '%':
        return _compare(ctx, lang, first, second, plain_hint)
    # "15% of 50": a stop word joins the percentage and the amount
    return [row(first / 100.0 * second, share_of(first, second))]


def _compare(ctx, lang, first, second, plain_hint):
    """What percentage `first` is of `second`, and the change between them."""
    if not first or not second:
        return None
    rows = []
    a, b = ctx.fmt(first), ctx.fmt(second)
    results = [
        (first / second * 100.0, lang.get('result') or '%s is %s of %s', lambda p: (a, p, b)),
        ((second - first) / first * 100.0, lang.get('increase') or 'The percentage increase from %s to %s is %s',
         lambda p: (a, b, p)),
        ((second - first) / second * 100.0, lang.get('decrease') or 'The percentage decrease from %s to %s is %s',
         lambda p: (b, a, p)),
    ]
    for value, template, arguments in results:
        shown = ctx.fmt(value) + '%'
        rows.append(item(template % arguments(shown), shown, arg=shown,
                         mods={'cmd': mod(plain_number(value), plain_hint)}))
    return rows
