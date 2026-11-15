# -*- coding: utf-8 -*-
"""Decides which calculator answers a query and shapes the reply Alfred expects."""
from .core import Context, clean_query


def auto(ctx, query):
    """Queries typed with no keyword. They always start with a number, and the first
    calculator that recognises the rest wins (order matters: "12 pt to l" is a pint)."""
    query = clean_query(query)
    if len(query) < 3:
        return []
    head = query[1:2] if query[0] in '-+' else query[0]
    if not (head.isdigit() or (head == '.' and len(query) > 1)):
        return []
    from . import datastorage, money, percentage, pxemrem, units, vat
    for tool in (units, percentage, pxemrem, vat, datastorage, money):
        rows = tool.process(ctx, query)
        if rows is not None:
            return rows
    return []


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
    else:
        rows = auto(ctx, query)
    response = {'items': rows or []}
    if ctx.rerun:
        response['rerun'] = ctx.rerun
    if ctx.variables:
        response['variables'] = ctx.variables
    return response
