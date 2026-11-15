#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Calculate Anything for Alfred: entry point.

    calculate.py "100 usd to idr"      a query typed with no keyword
    calculate.py --dot "5km to m"      Alfred's "." keyword ate the leading dot: 0.5km
    calculate.py --neg "25f to c"      Alfred's "-" keyword ate the minus sign: -25f
    calculate.py --vat "of 400"        the vat / time / color keywords
    calculate.py --any "Rp 1.500.000"  the calc keyword, Universal Action and hotkey: any text
    calculate.py --symbol "$100 to idr"  the $ € £ ¥ keywords: an amount written symbol first
    calculate.py --refresh currency    download rates now (normally started in the background)
    calculate.py --clear               delete cached rates
"""
import json
import os
import sys

# Alfred's triggers point Python's bytecode cache at the workflow cache folder. Run by hand
# there is no such folder, so write no bytecode at all rather than litter the workflow folder
# (which lives in the synced Alfred preferences).
if not os.environ.get('PYTHONPYCACHEPREFIX'):
    sys.dont_write_bytecode = True

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    args = argv[1:]
    action, query = 'auto', ' '.join(args)
    if args and args[0].startswith('--'):
        flag, query = args[0][2:], ' '.join(args[1:])
        if flag == 'refresh':
            from ca import rates
            return rates.refresh_command(args[1:])
        if flag == 'clear':
            from ca import rates
            return rates.clear_command()
        if flag == 'dot':
            query = ('0.' + query) if query[:1].isdigit() else ''
        elif flag == 'neg':
            query = ('-' + query) if (query[:1].isdigit() or query[:1] == '.') else ''
        elif flag in ('vat', 'time', 'color', 'any', 'symbol'):
            action = flag
        else:
            query = ' '.join(args)
    try:
        from ca import app
        response = app.run(action, query)
    except Exception:                               # never leave Alfred with broken output
        import traceback
        traceback.print_exc()
        response = {'items': []}
        if action != 'auto':
            response['items'].append({'title': 'Calculate Anything hit an error',
                                      'subtitle': 'Open the workflow debugger in Alfred to see the details',
                                      'valid': False})
    sys.stdout.write(json.dumps(response, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
