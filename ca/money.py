# -*- coding: utf-8 -*-
"""Currency and cryptocurrency conversion.

    100 usd to idr        100 euros in dollars      100€ to $       100eur
    2 bitcoins to dollars 5 bitcoins in ethereum    1eth btc        1btc
    150k idr to usd       2.5 million yen to eur

One parser serves both because either side of a conversion can be a currency or a
coin. A regular currency always wins over a coin with the same ticker (PLN, ISK...).
With no target the amount is converted to the configured base currencies.
"""
import os
import time

from .core import (bundled, item, load_json, lookup, message, mod, parse_number, plain_number, split_amount,
                   strip_accents, term_splits)
from . import rates

# Hundreds of tickers are everyday words (WHY, ONE, GAS, TIME...). Typed with an explicit
# target ("5 why to usd") any listed coin converts; typed bare ("5 why") only coins this
# high in the market-cap ranking do, so ordinary Alfred searches stay free of noise.
BARE_COIN_RANK = 250


class Money(object):

    def __init__(self, ctx):
        self.ctx = ctx
        names = ctx.lang.section('currency')
        self.names = dict((code, name) for code, name in names.items() if len(code) == 3 and code.isupper())
        self.currency_words = ctx.lang.keywords('currency')
        self.crypto_words = ctx.lang.keywords('crypto_currency')
        self._name_index = None
        self._coins = None
        self._coin_names = None

    # ------------------------------------------------------------- recognising what was typed

    def fiat(self, term, _retry=True):
        if not term:
            return None
        code = term.upper()
        if code in self.names:
            return code
        word = lookup(self.currency_words, term)
        if isinstance(word, str) and len(word) == 3:
            return word.upper()
        if self._name_index is None:
            self._name_index = self._build_name_index()
        code = lookup(self._name_index, term)
        if code:
            return code
        if _retry and len(term) > 3 and term.endswith('s'):
            return self.fiat(term[:-1], False)          # "rupiahs", "usds"
        return None

    def _build_name_index(self):
        index = {}
        english = (load_json(bundled('lang', 'en_EN.json')) or {}).get('currency') or {}
        for source in (english, self.names):
            for code, name in source.items():
                if len(code) != 3 or not code.isupper() or not isinstance(name, str):
                    continue
                for part in name.split('|'):
                    part = part.strip().lower()
                    if part:
                        index.setdefault(part, code)
                        index.setdefault(strip_accents(part), code)
        return index

    def coins(self):
        """SYMBOL -> [name, price in USD, rank]; a bundled list stands in until prices load."""
        if self._coins is None:
            cached = rates.load('crypto')
            if cached:
                self._coins = cached['coins']
            else:
                seed = load_json(bundled('data', 'crypto-symbols.json')) or {}
                # the bundled list is in market-cap order, so position stands in for rank
                self._coins = dict((symbol, [name, 0.0, 0 if symbol == 'SAT' else position + 1])
                                   for position, (symbol, name) in enumerate(seed.items()))
        return self._coins

    def prominent(self, symbol):
        entry = self.coins().get(symbol)
        return bool(entry) and int(entry[2] or 0) <= BARE_COIN_RANK

    def crypto(self, term, _retry=True):
        if not term:
            return None
        coins = self.coins()
        # the keyword file first: "sats" means satoshis even though a SATS token exists
        word = lookup(self.crypto_words, term)
        if isinstance(word, str) and word.upper() in coins:
            return word.upper()
        symbol = term.upper()
        if symbol in coins:
            return symbol
        if self._coin_names is None:
            names = {}
            for ticker, entry in sorted(coins.items(), key=lambda pair: pair[1][2] or 999999):
                names.setdefault(str(entry[0]).lower(), ticker)
            self._coin_names = names
        symbol = self._coin_names.get(term)
        if symbol:
            return symbol
        if _retry and len(term) > 3 and term.endswith('s'):
            return self.crypto(term[:-1], False)        # "bitcoins", "dogecoins"
        return None

    def resolve(self, term, explicit=False):
        """('fiat', code) or ('crypto', symbol) for what was typed, else None.

        `explicit` says the query spelled out a stop word ("5 why to usd"). Without one,
        an obscure or one-letter ticker is assumed to be an ordinary word.
        """
        if not term or term.isdigit():
            return None
        code = self.fiat(term)
        if code:
            return ('fiat', code)
        symbol = self.crypto(term)
        if symbol and (explicit or (len(symbol) > 1 and self.prominent(symbol))):
            return ('crypto', symbol)
        return None

    # ------------------------------------------------------------- converting

    def rows(self, amount, source, targets):
        ctx = self.ctx
        settings = ctx.settings
        kinds = set(kind for kind, _ in [source] + targets)
        notes = {}
        data = {}
        pending = None
        for kind, max_age in (('fiat', settings.currency_cache_seconds), ('crypto', settings.crypto_cache_seconds)):
            if kind not in kinds:
                continue
            name = 'currency' if kind == 'fiat' else 'crypto'
            section = 'currency' if kind == 'fiat' else 'crypto_currency'
            loaded, state = rates.get(name, max_age)
            if loaded is None:
                if state == 'loading':
                    pending = pending or message(ctx.text(section, 'updating_rates', 'Updating rates...'))
                    ctx.request_rerun(0.3)
                else:
                    error = rates.last_error(name) or {}
                    return [message(ctx.text(section, 'fetch_error', 'Unable to get currencies data'),
                                    ctx.text('currency', 'fetch_error_subtitle') or str(error.get('message', '')))]
                continue
            if state == 'refreshing':
                ctx.request_rerun(0.5)
            data[kind] = loaded
            notes[kind] = self._note(loaded)
        if pending:
            return [pending]

        fiat_rates = (data.get('fiat') or {}).get('rates') or {}
        coins = (data.get('crypto') or {}).get('coins') or {}

        def dollars_per(kind, code):
            """How many US dollars one unit is worth, or None when we have no rate."""
            if kind == 'fiat':
                rate = fiat_rates.get(code)
                return 1.0 / rate if rate else None
            entry = coins.get(code)
            return float(entry[1]) if entry and entry[1] else None

        source_kind, source_code = source
        source_value = dollars_per(source_kind, source_code)
        if source_value is None:
            return [self._no_rate(source_kind, source_code)]

        rows = []
        for kind, code in targets:
            target_value = dollars_per(kind, code)
            if target_value is None:
                rows.append(self._no_rate(kind, code))
                continue
            single = source_value / target_value
            total = amount * single
            decimals = settings.currency_decimals if kind == 'fiat' else settings.crypto_decimals
            shown = ctx.fmt(total, decimals)
            subtitle = '1 %s = %s %s' % (source_code, ctx.fmt(single, -1), code)
            if kind == 'crypto' and coins.get(code):
                subtitle += ' - %s' % coins[code][0]
            note = notes.get('crypto') if 'crypto' in kinds else notes.get('fiat')
            if note:
                subtitle += '  ·  ' + note
            section = 'currency' if source_kind == 'fiat' else 'crypto_currency'
            icon = None
            if kind == 'fiat' and os.path.exists(bundled('flags', code + '.png')):
                icon = 'flags/%s.png' % code
            rows.append(item('%s %s' % (shown, code), subtitle, arg=shown, icon=icon, mods={
                'cmd': mod(plain_number(total, decimals), ctx.text(section, 'cmd')),
                'alt': mod(plain_number(single, -1), ctx.text(section, 'alt')),
            }))
        return rows

    def _no_rate(self, kind, code):
        if kind == 'crypto':
            return message(self.ctx.text('crypto_currency', 'nosymbol_title',
                                         'The crypto currency is not available'), code)
        return message((self.ctx.text('currency', 'no_rate') or 'No exchange rate available for %s') % code,
                       self.names.get(code, ''))

    def _note(self, loaded):
        """"updated 3h ago": how old the numbers behind this row are."""
        moment = loaded.get('updated') or loaded.get('fetched')
        try:
            seconds = max(0, time.time() - float(moment))
        except (TypeError, ValueError):
            return ''
        if seconds < 90:
            age = '%ds' % seconds
        elif seconds < 5400:
            age = '%dm' % round(seconds / 60.0)
        elif seconds < 129600:
            age = '%dh' % round(seconds / 3600.0)
        else:
            age = '%dd' % round(seconds / 86400.0)
        template = self.ctx.text('currency', 'updated', 'updated %s ago')
        return template % age


def _multiplied(ctx, rest):
    """"k usd" -> (1000, "usd"); thousands and millions written as a word or suffix."""
    table = ctx.lang.keywords('multipliers')
    words = rest.split(' ', 1)
    if len(words) == 2 and words[1].strip():
        factor = lookup(table, words[0])
        if isinstance(factor, (int, float)) and factor > 0:
            return float(factor), words[1].strip()
    return None


def process(ctx, query):
    parts = split_amount(query)
    if not parts or not parts[1]:
        return None
    number, rest = parts
    money = Money(ctx)
    stops = ctx.lang.stop_words('currency') + ctx.lang.stop_words('crypto_currency')
    attempts = []
    scaled = _multiplied(ctx, rest)
    if scaled:
        attempts.append(scaled)
    attempts.append((1.0, rest))
    for factor, text in attempts:
        for from_term, to_term, had_stop in term_splits(text, stops):
            if from_term in stops:
                continue
            explicit = had_stop and bool(to_term)
            source = money.resolve(from_term, explicit)
            if not source:
                continue
            if to_term:
                target = money.resolve(to_term, explicit)
                if not target:
                    continue
                targets = [target]
            else:
                if source[0] == 'crypto' and _also_a_unit(ctx, from_term):
                    continue                    # "100 km" is not a request for the KM coin
                targets = [('fiat', code) for code in ctx.settings.base_currencies if ('fiat', code) != source]
                targets = targets or [source]
            amount = parse_number(number, ctx.settings) * factor
            return money.rows(amount, source, targets)
    return None


def _also_a_unit(ctx, term):
    from . import datastorage, units
    return units.is_unit_term(ctx.lang, term) or bool(lookup(datastorage.build_index(ctx.lang), term))
