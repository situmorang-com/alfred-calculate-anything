# -*- coding: utf-8 -*-
"""The README animation's storyboard, built from the workflow's real answers.

    /usr/bin/python3 tools/demo/storyboard.py > board.json

Each frame is what Alfred shows after one more keystroke: the query, the rows this workflow
returns for it (with their icons), a caption naming the feature, and how long the frame
stays up. Rates come from the workflow's cache, so refresh them first. make.sh runs this,
then render.swift, then ffmpeg.
"""
import json
import os
import plistlib
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.dont_write_bytecode = True
sys.path.insert(0, ROOT)
from ca import app  # noqa: E402

ENV = {'language': 'en_EN', 'input_language': 'none', 'base_currencies': 'USD, EUR, JPY, IDR',
       'timezone': 'Asia/Jakarta'}

# (caption, what is typed: one string per burst, with a short pause between bursts)
SCENES = [
    ('Currencies, as many as you like', ['100 usd to eur', ' gbp jpy']),
    ('Crypto, in your own currencies', ['1 btc']),
    ('Units, even without a target', ['100 kg']),
    ('Feet and inches', ['5\'11"']),
    ('How long a download takes', ['4 gb at 50 mbps']),
    ('Percentages in plain words', ['15% tip on 80']),
    ('Every color format', ['color #ff6600']),
]
MAX_ROWS = 6                # Alfred's visible results, set to six


def keyword_row(word):
    """The row Alfred shows while a keyword is being typed, from the filter's title."""
    with open(os.path.join(ROOT, 'info.plist'), 'rb') as handle:
        plist = plistlib.load(handle)
    for obj in plist['objects']:
        config = obj.get('config', {})
        if config.get('keyword') == '{var:keyword_%s}' % word:
            return {'title': config.get('title', ''), 'subtitle': config.get('subtext', ''),
                    'icon': os.path.join(ROOT, 'icon.png')}
    return None


def rows_for(query):
    keyword = 'color'
    if query and ' ' not in query and keyword.startswith(query):
        row = keyword_row(keyword) if len(query) >= 3 else None
        return [row] if row else []
    if query.startswith(keyword + ' '):
        items = app.run('color', query[len(keyword) + 1:], ENV)['items']
    else:
        items = app.run('auto', query, ENV)['items']
    rows = []
    for item in items[:MAX_ROWS]:
        icon = (item.get('icon') or {}).get('path') or 'icon.png'
        rows.append({'title': item['title'], 'subtitle': item.get('subtitle', ''),
                     'icon': icon if os.path.isabs(icon) else os.path.join(ROOT, icon)})
    return rows


def frame(query, rows, caption, duration, select_all=False, cursor=True):
    return {'query': query, 'rows': rows, 'caption': caption, 'duration': round(duration, 3),
            'selectAll': select_all, 'cursor': cursor}


def main():
    pace = random.Random(7)                 # a human typing rhythm, the same on every run
    frames = [frame('', [], 'Type a number in Alfred', 1.2)]
    for caption, bursts in SCENES:
        typed = ''
        for number, burst in enumerate(bursts):
            for char in burst:
                typed += char
                delay = 0.11 if char == ' ' else 0.06 + pace.random() * 0.04
                frames.append(frame(typed, rows_for(typed), caption, delay))
            last = number == len(bursts) - 1
            frames[-1]['duration'] = (2.0 + 0.12 * len(frames[-1]['rows'])) if last else 1.1
        frames.append(frame(typed, frames[-1]['rows'], caption, 0.3, select_all=True, cursor=False))
        frames.append(frame('', [], caption, 0.25))
    board = {'width': 1000, 'height': 536, 'scale': 2, 'frames': frames}
    json.dump(board, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
