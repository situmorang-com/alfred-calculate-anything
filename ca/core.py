# -*- coding: utf-8 -*-
"""Shared plumbing: settings, language data, number parsing/formatting, Alfred items.

Everything here is standard library only and has to run on the Python 3.9 that
ships with Apple's developer tools (/usr/bin/python3) as well as newer Pythons.
"""
import json
import os
import re
import unicodedata

WORKFLOW_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE_ID = 'com.situmorang.calculateanything'
DEFAULT_LANG = 'en_EN'

# Regions whose everyday numeric dates put the month first (01/02 = January 2nd).
MONTH_FIRST_REGIONS = frozenset(['US', 'AS', 'GU', 'MP', 'PR', 'UM', 'VI', 'PH', 'FM', 'MH', 'PW'])


# --------------------------------------------------------------------------- paths

def data_dir():
    """Alfred's per-workflow data folder (falls back to the same path outside Alfred)."""
    path = os.environ.get('alfred_workflow_data') or os.path.expanduser(
        '~/Library/Application Support/Alfred/Workflow Data/' + BUNDLE_ID)
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    return path


def cache_dir():
    path = os.path.join(data_dir(), 'cache')
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    return path


_json_cache = {}


def load_json(path):
    """Read a JSON file once per run; a missing or broken file is None, never an error."""
    if path not in _json_cache:
        try:
            with open(path, encoding='utf-8') as handle:
                _json_cache[path] = json.load(handle)
        except (OSError, ValueError):
            _json_cache[path] = None
    return _json_cache[path]


def bundled(*parts):
    return os.path.join(WORKFLOW_DIR, *parts)


# --------------------------------------------------------------------------- text

def nfc(text):
    return unicodedata.normalize('NFC', text)


def strip_accents(text):
    return ''.join(ch for ch in unicodedata.normalize('NFD', text) if not unicodedata.combining(ch))


_SPACES = re.compile(r'\s+')


def clean_query(query):
    """Normalise what the user typed: composed Unicode, single spaces, lower case.

    Alfred hands over decomposed characters (n + combining tilde), which would never
    match the keyword files, so composing first matters for every non-English word.
    """
    if not query:
        return ''
    text = nfc(query)
    text = text.replace('µ', 'μ')              # micro sign -> Greek mu (as in "μm")
    text = text.replace('²', '2').replace('³', '3')  # m² -> m2, m³ -> m3
    text = text.replace(' ', ' ').replace(' ', ' ')
    text = _SPACES.sub(' ', text).strip()
    return text.lower()


# --------------------------------------------------------------------------- settings

def _first_number(text, default):
    match = re.search(r'-?\d+(?:[.,]\d+)?', str(text))
    if not match:
        return default
    try:
        return float(match.group(0).replace(',', '.'))
    except ValueError:
        return default


def _flag(value):
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def system_locale():
    """The macOS locale identifier, e.g. "en_ID" (read straight from the preferences file)."""
    try:
        import plistlib
        with open(os.path.expanduser('~/Library/Preferences/.GlobalPreferences.plist'), 'rb') as handle:
            return str(plistlib.load(handle).get('AppleLocale') or '')
    except Exception:
        return os.environ.get('LANG', '')


class Settings(object):
    """The workflow's configuration, as Alfred exports it to the environment."""

    def __init__(self, environ=None):
        self.env = os.environ if environ is None else environ
        get = self.get
        self.language = get('language', DEFAULT_LANG)
        self.decimal_separator = 'comma' if get('decimal_separator', 'dot') == 'comma' else 'dot'
        self.number_output_format = get('number_output_format', 'comma_dot')
        self.currency_decimals = int(_first_number(get('currency_decimals', '2'), 2))
        self.crypto_decimals = int(_first_number(get('crypto_decimals', '-1'), -1))
        self.vat_percentage = _first_number(get('vat_value', '11%'), 11.0)    # Indonesia's PPN
        self.base_pixels = _first_number(get('pixels_base', '16px'), 16.0) or 16.0
        self.force_binary = _flag(get('datastorage_force_binary', '0'))
        self.fixer_key = get('apikey_fixer', '')
        self.coinmarketcap_key = get('apikey_coinmarket', '')
        self.currency_cache_seconds = self._hours('currency_cache_hours', 6.0)
        self.crypto_cache_seconds = self._hours('cryptocurrency_cache_hours', 0.25)
        formats = [part.strip() for part in get('date_format', 'j F, Y, g:i:s a').split('|')]
        self.date_formats = [part for part in formats if part] or ['j F, Y, g:i:s a']
        self.date_order = get('date_order', 'auto')
        self._locale = None
        self._timezone = None
        self._base_currencies = None

    def get(self, name, default=''):
        value = self.env.get(name)
        if value is None or str(value).strip() == '':
            return default
        return str(value).strip()

    def _hours(self, name, default):
        hours = _first_number(self.get(name, ''), default)
        if hours <= 0:
            hours = default
        return hours * 3600.0

    # -- derived from the system when the user has not configured them --

    @property
    def locale(self):
        if self._locale is None:
            self._locale = system_locale()
        return self._locale

    @property
    def region(self):
        match = re.match(r'^[A-Za-z]{2,3}(?:[_-][A-Za-z]{4})?[_-]([A-Za-z]{2})\b', self.locale)
        return match.group(1).upper() if match else ''

    @property
    def local_currency(self):
        match = re.search(r'currency=([A-Za-z]{3})', self.locale)
        if match:
            return match.group(1).upper()
        regions = load_json(bundled('data', 'regions.json')) or {}
        return regions.get(self.region, '')

    @property
    def base_currencies(self):
        """Target currencies for "100 eur" with no target. Configured, else local + USD + EUR."""
        if self._base_currencies is None:
            raw = self.get('base_currencies', '')
            codes = [code.strip().upper() for code in re.split(r'[,;\s]+', raw) if code.strip()]
            if not codes:
                codes = [self.local_currency, 'USD', 'EUR']
            seen = []
            for code in codes:
                if code and code not in seen:
                    seen.append(code)
            self._base_currencies = seen or ['USD']
        return self._base_currencies

    @property
    def month_first(self):
        """How to read 01/02/2026: True means January 2nd, False means 1 February."""
        if self.date_order == 'mdy':
            return True
        if self.date_order == 'dmy':
            return False
        return self.region in MONTH_FIRST_REGIONS

    @property
    def timezone_name(self):
        name = self.get('timezone', 'none')
        if name and name.lower() != 'none':
            return name
        try:
            target = os.path.realpath('/etc/localtime')
            if 'zoneinfo/' in target:
                return target.split('zoneinfo/', 1)[1]
        except OSError:
            pass
        return os.environ.get('TZ', '') or 'UTC'

    @property
    def timezone(self):
        if self._timezone is None:
            self._timezone = load_timezone(self.timezone_name)
        return self._timezone


def load_timezone(name):
    """A tzinfo for an IANA name; falls back to the machine's current offset."""
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:
        import datetime
        return datetime.datetime.now().astimezone().tzinfo


# --------------------------------------------------------------------------- language

def _norm_key(key):
    return nfc(str(key)).lower()


class Lang(object):
    """Display strings plus the keyword tables that turn natural language into units.

    lang/<code>.json       what the workflow says
    lang/<code>-keys.json  what the user may type ("kilometers" -> "km", stop words)
    English is always loaded underneath, so a partial translation still works, and a
    custom-keys.json in the workflow's data folder is layered on top so personal
    keywords survive workflow updates.
    """

    def __init__(self, code):
        base = load_json(bundled('lang', DEFAULT_LANG + '.json')) or {}
        base_keys = load_json(bundled('lang', DEFAULT_LANG + '-keys.json')) or {}
        strings, keys = base, base_keys
        if code and code != DEFAULT_LANG:
            own = load_json(bundled('lang', code + '.json'))
            own_keys = load_json(bundled('lang', code + '-keys.json'))
            if isinstance(own, dict) and own:
                strings = self._merge_strings(base, own)
            else:
                code = DEFAULT_LANG
            if isinstance(own_keys, dict) and own_keys:
                keys = self._merge_keys(own_keys, base_keys)
        custom = load_json(os.path.join(data_dir(), 'custom-keys.json'))
        if isinstance(custom, dict) and custom:
            keys = self._merge_keys(custom, keys)
        self.code = code or DEFAULT_LANG
        self.strings = strings
        self.keys = keys
        self._keyword_cache = {}

    @staticmethod
    def _merge_strings(base, own):
        merged = dict(base)
        for section, value in own.items():
            if isinstance(value, dict) and isinstance(base.get(section), dict):
                combined = dict(base[section])
                combined.update(value)
                merged[section] = combined
            elif value not in (None, [], {}):
                merged[section] = value
        return merged

    @staticmethod
    def _merge_keys(own, base):
        """`own` wins on conflicts; lists (stop words, phrases) are unioned."""
        merged = {}
        for section in list(own.keys()) + [s for s in base.keys() if s not in own]:
            mine = own.get(section)
            theirs = base.get(section)
            if not isinstance(mine, dict):
                merged[section] = dict(theirs) if isinstance(theirs, dict) else {}
                continue
            combined = dict(mine)
            if isinstance(theirs, dict):
                for key, value in theirs.items():
                    if key not in combined:
                        combined[key] = value
                    elif isinstance(combined[key], list) and isinstance(value, list):
                        combined[key] = combined[key] + [v for v in value if v not in combined[key]]
            merged[section] = combined
        return merged

    def text(self, section, key, default=''):
        value = (self.strings.get(section) or {}).get(key)
        return value if isinstance(value, str) and value else default

    def section(self, section):
        value = self.strings.get(section)
        return value if isinstance(value, dict) else {}

    def keywords(self, section):
        """keyword -> replacement, lower-cased, with accent-free spellings added."""
        if section not in self._keyword_cache:
            table = {}
            for key, value in (self.keys.get(section) or {}).items():
                if isinstance(value, (list, dict)) or key == 'stop_words':
                    continue
                table[_norm_key(key)] = value
            for key in list(table):
                plain = strip_accents(key)
                if plain != key and plain not in table:
                    table[plain] = table[key]
            self._keyword_cache[section] = table
        return self._keyword_cache[section]

    def stop_words(self, section):
        words = (self.keys.get(section) or {}).get('stop_words') or []
        return [_norm_key(word) for word in words if isinstance(word, str) and word]

    def phrases(self, section, name):
        """Trigger phrases such as time -> "until": ["until", "hasta"]."""
        words = (self.keys.get(section) or {}).get(name) or []
        if isinstance(words, str):
            words = [words]
        out = []
        for word in words:
            word = _norm_key(word)
            for form in (word, strip_accents(word)):
                if form and form not in out:
                    out.append(form)
        return out


def lookup(table, term):
    """Dictionary lookup that also tolerates missing accents ("dias" for "días")."""
    if term in table:
        return table[term]
    plain = strip_accents(term)
    if plain != term and plain in table:
        return table[plain]
    return None


# --------------------------------------------------------------------------- numbers

def parse_number(text, settings):
    """"1,350.50" / "1 350,50" -> float, honouring the configured decimal separator."""
    raw = str(text).strip().replace(' ', '').replace(' ', '')
    sign = -1.0 if raw.startswith('-') else 1.0
    raw = raw.lstrip('+-')
    if settings is not None and settings.decimal_separator == 'comma':
        raw = raw.replace('.', '').replace(',', '.')
    else:
        raw = raw.replace(',', '')
    match = re.match(r'\d*\.?\d*', raw)
    digits = match.group(0) if match else ''
    if digits in ('', '.'):
        return 0.0
    try:
        return sign * float(digits)
    except ValueError:
        return 0.0


def _separators(settings):
    style = settings.number_output_format if settings is not None else 'comma_dot'
    if style == 'dot_comma':
        return '.', ','
    if style == 'space_comma':
        return ' ', ','
    return ',', '.'


def plain_digits(value, significant=14):
    """abs(value) written out positionally (never 1e-05) at 14 significant digits.

    14 digits hides binary-float noise (0.1 + 0.2) the same way the original did.
    """
    from decimal import Context, ROUND_HALF_UP
    number = Context(prec=significant, rounding=ROUND_HALF_UP).create_decimal(repr(abs(float(value))))
    text = format(number, 'f')
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    return text or '0'


def _rounded_parts(value, decimals):
    """(negative, integer digits, fraction digits) after applying the display rules.

    decimals < 0   "natural": every meaningful decimal, at most 8 (for values below 1,
                   8 after the leading zeros so tiny results never collapse to 0)
    decimals >= 0  that many places, except that values below 0.1 keep that many
                   significant digits (0.00035486 with 2 -> 0.00035) and values above 1
                   are not padded with zeros (150.5 stays 150.5, 150 stays 150)
    """
    from decimal import Decimal, ROUND_HALF_UP
    number = float(value)
    text = plain_digits(number)
    whole, _, fraction = text.partition('.')
    if not fraction:
        places = 0
    else:
        total = len(fraction)
        leading = (total - len(fraction.lstrip('0'))) if whole == '0' else 0
        if decimals is None or decimals < 0:
            places = min(total, leading + 8 if whole == '0' else 8)
        else:
            places = int(decimals)
            if whole == '0' and leading and places > 0:
                places = leading + min(total - leading, places)
            elif whole != '0' and places > total:
                places = total
    quantum = Decimal(1).scaleb(-places)
    rounded = Decimal(text).quantize(quantum, rounding=ROUND_HALF_UP)
    out = format(rounded, 'f')
    whole, _, fraction = out.partition('.')
    negative = number < 0 and rounded != 0
    return negative, whole, fraction


def format_number(value, decimals=-1, settings=None):
    """A number as the user wants to read it (thousands separators, their decimal mark)."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number != number or number in (float('inf'), float('-inf')):
        return str(value)
    negative, whole, fraction = _rounded_parts(number, decimals)
    thousands, point = _separators(settings)
    groups = []
    while len(whole) > 3:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    groups.insert(0, whole)
    out = thousands.join(groups)
    if fraction:
        out += point + fraction
    return ('-' if negative else '') + out


def plain_number(value, decimals=-1):
    """The same value with no grouping and a dot decimal point, for "copy without format"."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number != number or number in (float('inf'), float('-inf')):
        return str(value)
    negative, whole, fraction = _rounded_parts(number, decimals)
    return ('-' if negative else '') + whole + ('.' + fraction if fraction else '')


# --------------------------------------------------------------------------- query pieces

# A number as typed: 1350.5, 1,350.50, 1.350,50, .5 and, with spaces, only real thousands
# groups (1 350 or 10 000.5) so "20 20 vision" is not read as 2020.
NUMBER = r'(?:\d{1,3}(?: \d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)*|[.,]\d+)'
_AMOUNT = re.compile(r'^(?P<sign>[-+]?)\s*(?P<num>%s)' % NUMBER)


def split_amount(query):
    """"1 350.50km to m" -> ("1 350.50", "km to m"); None when it does not start with a number."""
    match = _AMOUNT.match(query)
    if not match:
        return None
    number = match.group('sign') + match.group('num')
    return number, query[match.end():].strip()


def term_splits(rest, stop_words):
    """Ways to read "<from> [stop word] <to>", most plausible first.

    Yields (from_term, to_term, had_stop_word). to_term may be empty ("100 usd",
    "100 usd to"). Terms can be several words ("us dollars", "miles per hour"), and a
    stop word can double as a unit ("100 cm in in"), hence trying every split.
    """
    tokens = rest.replace('=', ' = ').split()
    count = len(tokens)
    if not count:
        return
    stops = [word.split() for word in sorted(set(stop_words), key=len, reverse=True) if word]
    for index in range(1, count):
        for words in stops:
            size = len(words)
            if tokens[index:index + size] == words:
                yield ' '.join(tokens[:index]), ' '.join(tokens[index + size:]), True
    for index in range(count, 0, -1):
        yield ' '.join(tokens[:index]), ' '.join(tokens[index:]), False


# --------------------------------------------------------------------------- Alfred output

def item(title, subtitle='', arg=None, valid=True, icon=None, mods=None, copy=None, largetype=None,
         autocomplete=None, variables=None):
    """One row in Alfred's result list."""
    row = {'title': str(title), 'subtitle': str(subtitle or '')}
    if arg is not None:
        row['arg'] = str(arg)
    row['valid'] = bool(valid) and arg is not None
    if icon:
        row['icon'] = {'path': icon}
    if mods:
        row['mods'] = mods
    text = {}
    if copy is None and arg is not None:
        copy = arg
    if copy is not None:
        text['copy'] = str(copy)
    if largetype is None:
        largetype = title
    text['largetype'] = str(largetype)
    row['text'] = text
    if autocomplete is not None:
        row['autocomplete'] = autocomplete
    if variables:
        row['variables'] = variables
    return row


def mod(arg, subtitle):
    return {'valid': True, 'arg': str(arg), 'subtitle': str(subtitle or '')}


def message(title, subtitle=''):
    """A row that only informs (errors, "Updating rates...")."""
    return {'title': str(title), 'subtitle': str(subtitle or ''), 'valid': False}


class Context(object):
    """What every calculator needs for one run: settings, language, and a way to ask
    Alfred to run the query again shortly (used while rates download in the background)."""

    def __init__(self, environ=None):
        self.settings = Settings(environ)
        self.lang = Lang(self.settings.language)
        self.rerun = None
        self.variables = {}

    def text(self, section, key, default=''):
        return self.lang.text(section, key, default)

    def fmt(self, value, decimals=-1):
        return format_number(value, decimals, self.settings)

    def request_rerun(self, seconds):
        if self.rerun is None or seconds < self.rerun:
            self.rerun = seconds
