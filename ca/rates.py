# -*- coding: utf-8 -*-
"""Exchange rates and cryptocurrency prices: where they come from and how they are kept.

No API key is needed. Each kind of data has a list of free public sources that are
tried in order, so one of them going away (which is what broke the original workflow)
does not take the feature down:

    currency   exchangerate-api.com, then the fawazahmed0 currency API (two CDNs),
               then frankfurter.dev, then the European Central Bank's daily file
    crypto     coinpaprika.com, then coingecko.com, then coinlore.net

A Fixer or CoinMarketCap key from the workflow configuration is still honoured and
tried first, falling back to the free sources when it fails.

Downloads never happen while Alfred is waiting for results. A query that finds the
cache out of date starts a detached copy of this script to refresh it and answers
from the old numbers straight away; Alfred is asked to re-run the query a moment
later and picks up the new ones. Everything is stored against the US dollar.
"""
import json
import os
import sys
import time

from .core import WORKFLOW_DIR, bundled, cache_dir, load_json

USER_AGENT = 'CalculateAnything-Alfred-Workflow/5.0'
LOCK_SECONDS = 90        # a refresh that has not finished by then is presumed dead
ERROR_BACKOFF = 20       # after a failed refresh, wait this long before trying again
KINDS = ('currency', 'crypto')
MAX_COINS = 2500


class FetchError(Exception):
    pass


# --------------------------------------------------------------------------- cache files

def _path(kind, suffix='json'):
    return os.path.join(cache_dir(), '%s.%s' % (kind, suffix))


def _write(path, data):
    temporary = '%s.%d.tmp' % (path, os.getpid())
    with open(temporary, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, ensure_ascii=False, separators=(',', ':'))
    os.replace(temporary, path)


def _remove(path):
    try:
        os.remove(path)
    except OSError:
        pass


def load(kind):
    """The cached data for `kind`, or None when there is none worth using."""
    try:
        with open(_path(kind), encoding='utf-8') as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    key = 'rates' if kind == 'currency' else 'coins'
    if not isinstance(data, dict) or not isinstance(data.get(key), dict) or not data[key]:
        return None
    return data


def last_error(kind):
    try:
        with open(_path(kind, 'err'), encoding='utf-8') as handle:
            error = json.load(handle)
        return error if isinstance(error, dict) and 'time' in error else None
    except (OSError, ValueError):
        return None


def refresh_running(kind):
    try:
        return time.time() - os.path.getmtime(_path(kind, 'lock')) < LOCK_SECONDS
    except OSError:
        return False


def start_refresh(kind):
    """Launch a detached refresh unless one is already under way. True if one is running."""
    if refresh_running(kind):
        return True
    lock = _path(kind, 'lock')
    try:
        with open(lock, 'w') as handle:
            handle.write(str(os.getpid()))
    except OSError:
        return False
    try:
        import subprocess
        subprocess.Popen(
            [sys.executable, os.path.join(WORKFLOW_DIR, 'calculate.py'), '--refresh', kind],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True, close_fds=True, cwd=WORKFLOW_DIR)
        return True
    except Exception:
        _remove(lock)
        return False


def get(kind, max_age):
    """(data, state) for a calculator.

    fresh       data is current
    refreshing  data is out of date and being replaced right now; ask Alfred to re-run
    stale       data is out of date and the last refresh failed; still the best we have
    loading     nothing cached yet, download in progress
    error       nothing cached and the download failed
    """
    data = load(kind)
    now = time.time()
    if data and now - float(data.get('fetched') or 0) < max_age:
        return data, 'fresh'
    running = refresh_running(kind)
    if not running:
        error = last_error(kind)
        if not (error and now - float(error.get('time') or 0) < ERROR_BACKOFF):
            running = start_refresh(kind)
    if data:
        return data, 'refreshing' if running else 'stale'
    return None, 'loading' if running else 'error'


# --------------------------------------------------------------------------- HTTP

def http_get(url, headers=None, timeout=12):
    """Body of a GET as text. urllib first (it follows the macOS proxy settings); if that
    cannot connect, e.g. Python has no usable certificate store, curl has a go."""
    send = {'User-Agent': USER_AGENT, 'Accept': 'application/json, */*', 'Accept-Encoding': 'gzip'}
    send.update(headers or {})
    import urllib.error
    import urllib.request
    try:
        request = urllib.request.Request(url, headers=send)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            if response.headers.get('Content-Encoding') == 'gzip' or body[:2] == b'\x1f\x8b':
                import gzip
                body = gzip.decompress(body)
        return body.decode('utf-8', 'replace')
    except urllib.error.HTTPError as error:
        raise FetchError('HTTP %s' % error.code)
    except Exception as first:
        import subprocess
        command = ['/usr/bin/curl', '-sS', '-L', '--fail', '--compressed', '-m', str(timeout), '-A', USER_AGENT]
        for name, value in (headers or {}).items():
            command += ['-H', '%s: %s' % (name, value)]
        command.append(url)
        try:
            done = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout + 5)
        except Exception:
            raise FetchError(str(first) or first.__class__.__name__)
        if done.returncode != 0:
            reason = done.stderr.decode('utf-8', 'replace').strip().splitlines()
            raise FetchError(reason[-1] if reason else str(first))
        return done.stdout.decode('utf-8', 'replace')


def http_json(url, headers=None, timeout=12):
    try:
        return json.loads(http_get(url, headers, timeout))
    except ValueError:
        raise FetchError('unexpected response')


# --------------------------------------------------------------------------- currency sources

def known_currencies():
    names = (load_json(bundled('lang', 'en_EN.json')) or {}).get('currency') or {}
    return set(code for code in names if len(code) == 3 and code.isupper())


def _clean_rates(raw, known):
    rates = {}
    for code, value in (raw or {}).items():
        code = str(code).upper()
        if code not in known:
            continue
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        if value > 0:
            rates[code] = value
    return rates


def _rebase(rates, base):
    """Turn rates quoted against `base` into rates quoted against the US dollar."""
    rates = dict(rates)
    rates[base] = 1.0
    dollar = rates.get('USD')
    if not dollar:
        raise FetchError('no USD rate')
    return dict((code, value / dollar) for code, value in rates.items())


def _day_to_time(day):
    try:
        import calendar
        return calendar.timegm(time.strptime(str(day)[:10], '%Y-%m-%d'))
    except Exception:
        return None


def _exchangerate_api(_settings):
    data = http_json('https://open.er-api.com/v6/latest/USD')
    if data.get('result') != 'success':
        raise FetchError(str(data.get('error-type') or 'request refused'))
    return data.get('rates'), data.get('time_last_update_unix')


def _fawazahmed0(url):
    def fetch(_settings):
        data = http_json(url)
        return data.get('usd'), _day_to_time(data.get('date'))
    return fetch


def _frankfurter(_settings):
    data = http_json('https://api.frankfurter.dev/v1/latest?base=USD')
    rates = dict(data.get('rates') or {})
    rates['USD'] = 1.0
    return rates, _day_to_time(data.get('date'))


def _ecb(_settings):
    import re
    text = http_get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
    pairs = re.findall(r"currency=['\"]([A-Z]{3})['\"]\s+rate=['\"]([0-9.]+)['\"]", text)
    if not pairs:
        raise FetchError('unexpected response')
    day = re.search(r"time=['\"](\d{4}-\d{2}-\d{2})['\"]", text)
    rates = _rebase(dict((code, float(value)) for code, value in pairs), 'EUR')
    return rates, _day_to_time(day.group(1)) if day else None


def _fixer(settings):
    key = settings.fixer_key
    try:
        data = http_json('https://api.apilayer.com/fixer/latest', {'apikey': key})
    except FetchError:
        data = {}
    if not data.get('success'):          # keys issued before Fixer moved to APILayer
        data = http_json('https://data.fixer.io/api/latest?access_key=%s&format=1' % key)
    if not data.get('success'):
        info = data.get('error') or {}
        raise FetchError(str(info.get('info') or info.get('type') or data.get('message') or 'key rejected'))
    return _rebase(data.get('rates') or {}, str(data.get('base') or 'EUR').upper()), data.get('timestamp')


FAWAZ_URLS = (
    'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json',
    'https://latest.currency-api.pages.dev/v1/currencies/usd.json',
)

CURRENCY_SOURCES = [
    ('exchangerate-api.com', _exchangerate_api),
    ('currency-api (jsDelivr)', _fawazahmed0(FAWAZ_URLS[0])),
    ('currency-api (Cloudflare)', _fawazahmed0(FAWAZ_URLS[1])),
    ('frankfurter.dev', _frankfurter),
    ('European Central Bank', _ecb),
]


def fetch_currency(settings):
    known = known_currencies()
    sources = list(CURRENCY_SOURCES)
    if settings.fixer_key:
        sources.insert(0, ('fixer.io', _fixer))
    problems = []
    for name, fetch in sources:
        try:
            raw, updated = fetch(settings)
            rates = _clean_rates(raw, known)
            if len(rates) < 20 or abs(rates.get('USD', 0) - 1.0) > 1e-9:
                raise FetchError('incomplete data')
        except Exception as error:
            problems.append('%s: %s' % (name, error))
            continue
        # A few currencies (North Korean won, Salvadoran colon, ...) are only carried by
        # the community API; borrow those so nothing the original listed goes missing.
        if not name.startswith('currency-api'):
            for url in FAWAZ_URLS:
                try:
                    extra, _ = _fawazahmed0(url)(settings)
                    for code, value in _clean_rates(extra, known).items():
                        rates.setdefault(code, value)
                    break
                except Exception:
                    continue
        return {'source': name, 'updated': updated, 'rates': rates, 'problems': problems}
    raise FetchError('; '.join(problems) or 'no source available')


# --------------------------------------------------------------------------- crypto sources

def _symbol(text):
    symbol = str(text or '').strip().upper()
    return symbol if symbol.isalnum() and symbol.isascii() and len(symbol) <= 10 else ''


def _add_coin(coins, symbol, name, price, rank):
    symbol = _symbol(symbol)
    try:
        price = float(price)
        rank = int(rank or 0) or 999999
    except (TypeError, ValueError):
        return
    if not symbol or price <= 0:
        return
    current = coins.get(symbol)
    if current is None or rank < current[2]:          # several coins share a ticker: keep the biggest
        coins[symbol] = [str(name or symbol).strip(), price, rank]


def _coinpaprika(_settings):
    coins = {}
    for coin in http_json('https://api.coinpaprika.com/v1/tickers?quotes=USD', timeout=25):
        quote = ((coin.get('quotes') or {}).get('USD') or {})
        _add_coin(coins, coin.get('symbol'), coin.get('name'), quote.get('price'), coin.get('rank'))
    return coins


def _coingecko(_settings):
    coins = {}
    url = ('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc'
           '&per_page=250&sparkline=false&page=%d')
    for page in (1, 2):
        try:
            rows = http_json(url % page, timeout=20)
        except FetchError:
            if page == 1:
                raise
            break
        for coin in rows:
            _add_coin(coins, coin.get('symbol'), coin.get('name'), coin.get('current_price'),
                      coin.get('market_cap_rank'))
    return coins


def _coinlore(_settings):
    coins = {}
    for start in (0, 100, 200, 300):
        try:
            rows = http_json('https://api.coinlore.net/api/tickers/?start=%d&limit=100' % start, timeout=20)
        except FetchError:
            if start == 0:
                raise
            break
        for coin in rows.get('data') or []:
            _add_coin(coins, coin.get('symbol'), coin.get('name'), coin.get('price_usd'), coin.get('rank'))
    return coins


def _coinmarketcap(settings):
    data = http_json('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=5000',
                     {'X-CMC_PRO_API_KEY': settings.coinmarketcap_key}, timeout=25)
    rows = data.get('data')
    if not rows:
        status = data.get('status') or {}
        raise FetchError(str(status.get('error_message') or 'key rejected'))
    coins = {}
    for coin in rows:
        quote = ((coin.get('quote') or {}).get('USD') or {})
        _add_coin(coins, coin.get('symbol'), coin.get('name'), quote.get('price'), coin.get('cmc_rank'))
    return coins


CRYPTO_SOURCES = [
    ('coinpaprika.com', _coinpaprika),
    ('coingecko.com', _coingecko),
    ('coinlore.net', _coinlore),
]


def with_satoshi(coins):
    """A satoshi is a hundred-millionth of a bitcoin; no price feed lists it."""
    bitcoin = coins.get('BTC')
    if bitcoin:
        coins['SAT'] = ['Satoshi', bitcoin[1] / 1e8, 0]
    return coins


def fetch_crypto(settings):
    sources = list(CRYPTO_SOURCES)
    if settings.coinmarketcap_key:
        sources.insert(0, ('coinmarketcap.com', _coinmarketcap))
    problems = []
    for name, fetch in sources:
        try:
            coins = fetch(settings)
            if len(coins) < 50 or 'BTC' not in coins:
                raise FetchError('incomplete data')
        except Exception as error:
            problems.append('%s: %s' % (name, error))
            continue
        ranked = sorted(coins.items(), key=lambda entry: entry[1][2])[:MAX_COINS]
        return {'source': name, 'updated': int(time.time()), 'coins': with_satoshi(dict(ranked)),
                'problems': problems}
    raise FetchError('; '.join(problems) or 'no source available')


# --------------------------------------------------------------------------- refresh

def refresh(kind, settings=None):
    """Download `kind` now and replace the cache. Returns (ok, message)."""
    if settings is None:
        from .core import Settings
        settings = Settings()
    try:
        data = fetch_currency(settings) if kind == 'currency' else fetch_crypto(settings)
        data['fetched'] = time.time()
        _write(_path(kind), data)
        _remove(_path(kind, 'err'))
        count = len(data['rates'] if kind == 'currency' else data['coins'])
        return True, '%s: %d entries from %s' % (kind, count, data['source'])
    except Exception as error:
        try:
            _write(_path(kind, 'err'), {'time': time.time(), 'message': str(error)[:400]})
        except OSError:
            pass
        return False, '%s: %s' % (kind, error)
    finally:
        _remove(_path(kind, 'lock'))


def refresh_command(arguments):
    kinds = [kind for kind in arguments if kind in KINDS] or list(KINDS)
    failed = False
    for kind in kinds:
        ok, text = refresh(kind)
        failed = failed or not ok
        sys.stdout.write(text + '\n')
    return 1 if failed else 0


def clear_command():
    """The _caclear keyword: forget every cached rate."""
    folder = cache_dir()
    try:
        names = os.listdir(folder)
    except OSError:
        names = []
    for name in names:
        path = os.path.join(folder, name)
        if os.path.isdir(path):
            import shutil
            shutil.rmtree(path, ignore_errors=True)
        else:
            _remove(path)
    from .core import Lang, Settings
    sys.stdout.write(Lang(Settings().language).text('general', 'cache_deleted', 'Cache deleted correctly'))
    return 0
