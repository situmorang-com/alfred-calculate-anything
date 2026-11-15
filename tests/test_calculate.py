# -*- coding: utf-8 -*-
"""Tests for Calculate Anything. Run from the workflow folder:

    /usr/bin/python3 tests/test_calculate.py

Everything here is offline: exchange rates and coin prices come from fixtures written
into a temporary data folder, and the clock is pinned for the date tests. The queries
are the examples from the original workflow's README plus the bugs reported against it.
"""
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True          # keep __pycache__ out of the synced workflow folder
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

DATA = tempfile.mkdtemp(prefix='calculate-anything-tests-')
os.environ['alfred_workflow_data'] = DATA

from ca import app, core, rates, timecalc  # noqa: E402

RATES = {'USD': 1.0, 'EUR': 0.9, 'IDR': 16000.0, 'MXN': 20.0, 'JPY': 150.0, 'CAD': 1.4, 'ARS': 1000.0,
         'GBP': 0.8, 'MYR': 4.5, 'SEK': 10.0, 'PLN': 4.0, 'COP': 4000.0, 'BRL': 5.0, 'KRW': 1300.0}
COINS = {'BTC': ['Bitcoin', 60000.0, 1], 'ETH': ['Ethereum', 3000.0, 2], 'DOGE': ['Dogecoin', 0.1, 9],
         'PLN': ['Some Token', 2.0, 900], 'WHY': ['Why Coin', 0.5, 800], 'KM': ['Kilometer Coin', 1.0, 40],
         'A': ['Vaulta', 0.5, 90], 'SATS': ['SATS (Ordinals)', 1e-8, 150],
         'SAT': ['Satoshi', 0.0006, 0]}

BASE_ENV = {'language': 'en_EN', 'base_currencies': 'USD, MXN', 'timezone': 'Asia/Jakarta',
            'vat_value': '16%', 'date_order': 'dmy'}
NOW = dt.datetime(2026, 11, 13, 20, 15, 0, tzinfo=core.load_timezone('Asia/Jakarta'))   # a Friday


def write_fixtures(age=0):
    folder = core.cache_dir()
    stamp = time.time() - age
    with open(os.path.join(folder, 'currency.json'), 'w') as handle:
        json.dump({'source': 'fixture', 'updated': stamp, 'fetched': stamp, 'rates': RATES}, handle)
    with open(os.path.join(folder, 'crypto.json'), 'w') as handle:
        json.dump({'source': 'fixture', 'updated': stamp, 'fetched': stamp, 'coins': COINS}, handle)


def ask(query, action='auto', **settings):
    env = dict(BASE_ENV)
    env.update(settings)
    return app.run(action, query, env)


def titles(query, action='auto', **settings):
    return [row['title'] for row in ask(query, action, **settings)['items']]


def first(query, action='auto', **settings):
    rows = titles(query, action, **settings)
    return rows[0] if rows else None


def when(query, **settings):
    env = dict(BASE_ENV)
    env.update(settings)
    ctx = core.Context(env)
    return [row['title'] for row in timecalc.keyword(ctx, query, now=NOW)]


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        core._json_cache.clear()
        write_fixtures()


class Numbers(Base):
    def test_format(self):
        fmt = core.format_number
        self.assertEqual(fmt(1234567.891, 2), '1,234,567.89')
        self.assertEqual(fmt(150.5, 2), '150.5')              # no zero padding above 1
        self.assertEqual(fmt(150, 2), '150')
        self.assertEqual(fmt(0.5, 2), '0.50')
        self.assertEqual(fmt(0.00035486302682, 2), '0.00035')  # small values keep significant digits
        self.assertEqual(fmt(0.1 + 0.2), '0.3')                # float noise is hidden
        self.assertEqual(fmt(1 / 3.0), '0.33333333')
        self.assertEqual(fmt(0.000000001), '0.000000001')      # tiny results never collapse to 0
        self.assertEqual(fmt(-31.666666, 2), '-31.67')
        self.assertEqual(fmt(2.675, 2), '2.68')                # rounds half up, like people do
        self.assertEqual(fmt(9460730472580800.0), '9,460,730,472,580,800')
        self.assertEqual(fmt(-0.0001, 2), '-0.0001')
        self.assertEqual(fmt(-0.00001, 0), '0')

    def test_output_styles(self):
        dot_comma = core.Settings({'number_output_format': 'dot_comma'})
        space_comma = core.Settings({'number_output_format': 'space_comma'})
        self.assertEqual(core.format_number(1234.56, 2, dot_comma), '1.234,56')
        self.assertEqual(core.format_number(1234.56, 2, space_comma), '1 234,56')
        self.assertEqual(core.plain_number(1234.56, 2), '1234.56')

    def test_parse(self):
        dot, comma = core.Settings({}), core.Settings({'decimal_separator': 'comma'})
        self.assertEqual(core.parse_number('1,350,200.50', dot), 1350200.5)
        self.assertEqual(core.parse_number('1 350.50', dot), 1350.5)
        self.assertEqual(core.parse_number('1.350,50', comma), 1350.5)
        self.assertEqual(core.parse_number('-25', dot), -25.0)
        self.assertEqual(core.parse_number('.250', dot), 0.25)
        # a number that reads only one way is read that way, whatever the setting
        self.assertEqual(core.parse_number('1.500.000', dot), 1500000.0)
        self.assertEqual(core.parse_number('1.500,50', dot), 1500.5)
        self.assertEqual(core.parse_number('1,500,000', comma), 1500000.0)
        self.assertEqual(core.parse_number('1,500.50', comma), 1500.5)
        # one that reads two ways follows the setting
        self.assertEqual(core.parse_number('1,500', dot), 1500.0)
        self.assertEqual(core.parse_number('1,500', comma), 1.5)

    def test_amount_split(self):
        self.assertEqual(core.split_amount('100km to m'), ('100', 'km to m'))
        self.assertEqual(core.split_amount('1 350.50km m'), ('1 350.50', 'km m'))
        self.assertEqual(core.split_amount('20 20 vision'), ('20', '20 vision'))
        self.assertEqual(core.split_amount('-25f to c'), ('-25', 'f to c'))
        self.assertIsNone(core.split_amount('km to m'))


class Units(Base):
    def test_readme_length(self):
        for query in ('100 kilometers to meters', '100 km in meters', '100 km m', '100km m'):
            self.assertEqual(first(query), '100,000 m', query)
        for query in ('100 miles as meters', '100miles in meters', '100 miles to m'):
            self.assertEqual(first(query), '160,934.4 m', query)

    def test_readme_weight(self):
        for query in ('100 ounces to kilograms', '100oz to kg', '100oz = kg', '100oz kg', '100oz=kg'):
            self.assertEqual(first(query), '2.83495231 kg', query)

    def test_readme_time(self):
        self.assertEqual(first('10 years to months'), '120 months')
        self.assertEqual(first('10years to seconds'), '315,360,000 seconds')
        self.assertEqual(first('10 years hr'), '87,600 hours')
        self.assertEqual(first('1 year to sec'), '31,536,000 seconds')
        self.assertEqual(first('1hr s'), '3,600 seconds')
        self.assertEqual(first('10 days hr'), '240 hours')
        self.assertEqual(first('60 min to hr'), '1 hour')

    def test_other_languages(self):
        self.assertEqual(first('10 días a horas', language='es_ES'), '240 horas')
        self.assertEqual(first('10 dias a horas', language='es_ES'), '240 horas')
        self.assertEqual(first('200 metros a km', language='es_ES'), '0.2 km')
        self.assertEqual(first('5 kilometer till meter', language='sv_SE'), '5,000 m')
        # English keeps working whatever the language
        self.assertEqual(first('100 km to m', language='es_ES'), '100,000 m')

    def test_original_test_file(self):
        self.assertEqual(first('100 ftlb to Nm'), '135.58179483 Nm')
        self.assertEqual(first('100 Nm to ftlb'), '73.75621493 ft⋅lb')
        self.assertEqual(first('100 nm to pm'), '100,000 pm')
        self.assertEqual(first('-25F to C'), '-31.67 °C')
        self.assertEqual(first('1120f c'), '604.44 °C')
        self.assertEqual(first('1,350km m'), '1,350,000 m')
        self.assertEqual(first('1,350.50 km m'), '1,350,500 m')
        self.assertEqual(first('1,350,200.50 km m'), '1,350,200,500 m')
        self.assertEqual(first('1 350.50km m'), '1,350,500 m')
        self.assertEqual(first('1,350,200.54 km m'), '1,350,200,540 m')

    def test_temperature(self):
        self.assertEqual(first('100 c to f'), '212 °F')
        self.assertEqual(first('98.6 f to c'), '37 °C')
        self.assertEqual(first('20 celsius to kelvin'), '293.15 K')
        self.assertEqual(first('0 k to c'), '-273.15 °C')

    def test_reported_bugs(self):
        self.assertEqual(first('4500 ft2 to m2'), '418.06368 m²')            # area never worked
        self.assertEqual(first('500 sqft in m2'), '46.45152 m²')
        self.assertEqual(first('8 ukpt to ukgal'), '1 UK gal')                    # UK gallon was 4.405 l
        self.assertEqual(first('1 ukgal to ukpt'), '8 UK pt')
        self.assertEqual(first('1 uk pints to ukpt'), '1 UK pt')
        self.assertEqual(first('100 ml to oz'), '3.38140227 fl oz')                # volume, so fluid ounces
        self.assertEqual(first('8 oz to ml'), '236.5882365 ml')
        self.assertEqual(titles('84 in ft'), ['7 ft'])                            # no bogus "7 ft, 12 in"
        self.assertEqual(titles('96 in ft'), ['8 ft'])
        self.assertEqual(titles('100 in to ft'), ['8.33333333 ft', '8 ft, 4 in'])
        self.assertEqual(first('1 cup to ml'), '236.5882365 ml')                   # requested units
        self.assertEqual(first('3 tsp to tbsp'), '1 tbsp')

    def test_ambiguous_abbreviations(self):
        self.assertEqual(first('2 h to min'), '120 minutes')       # "h" is also a hand
        self.assertEqual(first('90 m to hr'), '1.5 hours')         # "m" is also a metre
        self.assertEqual(first('5 h to cm'), '50.8 cm')            # ...and still is when that fits
        self.assertEqual(first('100 cm in in'), '39.37007874 in')  # "in" as stop word and as inch
        self.assertEqual(first('100 in cm'), '254 cm')
        self.assertEqual(first('100 cm in'), '39.37007874 in')
        self.assertEqual(first('1 n to kg'), '0.10197162 kg')

    def test_mixed_row(self):
        self.assertEqual(titles('100 min to hr'), ['1.66666667 hours', '1 hour, 40 minutes'])
        self.assertEqual(titles('170 cm to m'), ['1.7 m', '1 m, 70 cm'])
        self.assertEqual(titles('2 km to m'), ['2,000 m'])

    def test_modifiers(self):
        row = ask('1350.5 km to m')['items'][0]
        self.assertEqual(row['arg'], '1,350,500')
        self.assertEqual(row['mods']['cmd']['arg'], '1350500')
        self.assertEqual(row['mods']['alt']['arg'], '1,350,500 m')

    def test_cannot_convert(self):
        self.assertEqual(first('100 km to kg'), 'Error, you can not convert from km to kg')
        self.assertEqual(titles('100 km'), [])
        self.assertEqual(titles('100 km to'), [])

    def test_negative_and_leading_dot(self):
        self.assertEqual(first('0.250km to meters'), '250 m')
        self.assertEqual(first('-5 km to m'), '-5,000 m')

    def test_custom_keywords(self):
        path = os.path.join(core.data_dir(), 'custom-keys.json')
        with open(path, 'w') as handle:
            json.dump({'units': {'hakunamatata': 'year'}}, handle)
        core._json_cache.clear()
        try:
            self.assertEqual(first('1 hakunamatata to months'), '12 months')
        finally:
            os.remove(path)
            core._json_cache.clear()


class Percentages(Base):
    def test_readme(self):
        self.assertEqual(first('40 as a % of 50'), '40 is 80% of 50')
        self.assertEqual(first('20 is what % of 50'), '20 is 40% of 50')
        self.assertEqual(first('15% of 50'), '7.5')
        self.assertEqual(first('120 + 30%'), '156')
        self.assertEqual(first('120 plus 30%'), '156')
        self.assertEqual(first('120 - 30%'), '84')
        self.assertEqual(first('120 minus 30%'), '84')
        self.assertEqual(first('30 % 40'), '30 is 75% of 40')
        self.assertEqual(first('100 + 16%'), '116')

    def test_compare_rows(self):
        rows = ask('30 % 40')['items']
        self.assertEqual([row['title'] for row in rows], [
            '30 is 75% of 40',
            'The percentage increase from 30 to 40 is 33.33333333%',
            'The percentage decrease from 40 to 30 is 25%'])
        self.assertEqual(rows[0]['arg'], '75%')
        self.assertEqual(rows[0]['mods']['cmd']['arg'], '75')

    def test_spanish(self):
        self.assertEqual(first('120 más 30%', language='es_ES'), '156')
        self.assertEqual(first('120 mas 30%', language='es_ES'), '156')
        self.assertEqual(first('120 menos 10%', language='es_ES'), '108')
        self.assertEqual(first('40 como % de 50', language='es_ES'), '40 es 80% de 50')

    def test_reported_bugs(self):
        comma = {'decimal_separator': 'comma', 'number_output_format': 'dot_comma'}
        self.assertEqual(first('10,5+5%', **comma), '11,025')          # decimal comma was ignored
        self.assertEqual(first('30,5% of 100', **comma), '30,5')
        self.assertEqual(first('1000,5 + 10%', **comma), '1.100,55')   # output format was ignored

    def test_extras(self):
        self.assertEqual(titles('120 + 30%'), ['156', '36'])
        self.assertEqual(first('20% off 150'), '120')
        self.assertEqual(first('40 percent of 50'), '20')
        self.assertEqual(titles('100%'), [])
        self.assertEqual(titles('1+1'), [])


class FontSizes(Base):
    def test_readme(self):
        self.assertEqual(titles('12px'), ['0.75em', '0.75rem', '9pt'])
        self.assertEqual(titles('12px to em'), ['0.75em'])
        self.assertEqual(titles('2 rem'), ['32px', '2em', '24pt'])
        self.assertEqual(titles('2rem'), ['32px', '2em', '24pt'])
        self.assertEqual(titles('2rem to pt'), ['24pt'])
        self.assertEqual(titles('12px in em base 17px'), ['0.70588em'])
        self.assertEqual(titles('18px base 20px'), ['0.9em', '0.9rem', '13.5pt'])

    def test_configured_base(self):
        self.assertEqual(titles('12px to rem', pixels_base='10px'), ['1.2rem'])

    def test_pint_is_not_points(self):
        self.assertEqual(first('12 pt to l'), '5.67811768 l')
        self.assertEqual(titles('12 pt of beer'), [])


class Vat(Base):
    def test_keyword(self):
        self.assertEqual(titles('of 400', 'vat'), ['VAT of 400 = 64', '400 plus VAT = 464', '400 minus VAT = 344.83'])
        self.assertEqual(titles('400', 'vat'), titles('of 400', 'vat'))
        self.assertEqual(titles('400', 'vat', vat_value='11%')[0], 'VAT of 400 = 44')
        self.assertEqual(titles('400', 'vat', vat_value='')[0], 'VAT of 400 = 44')      # default: Indonesia's PPN
        self.assertEqual(titles('400 11%', 'vat')[0], 'VAT of 400 = 44')
        self.assertEqual(titles('', 'vat'), ['...'])

    def test_inline(self):
        self.assertEqual(titles('400 + vat'), ['464'])
        self.assertEqual(titles('400 + ppn', vat_value='11%'), ['444'])
        self.assertEqual(titles('400 plus vat'), ['464'])
        self.assertEqual(titles('400 - vat'), ['344.83'])
        self.assertEqual(titles('400 minus tax'), ['344.83'])
        self.assertEqual(titles('400 mas iva', language='es_ES'), ['464'])
        row = ask('1000 + vat')['items'][0]
        self.assertEqual(row['arg'], '1,160')
        self.assertEqual(row['mods']['cmd']['arg'], '1160')


class Storage(Base):
    def test_readme(self):
        self.assertEqual(first('100 gigabytes in megabytes'), '100,000 MB')
        self.assertEqual(first('100 gigas in megas'), '100,000 MB')
        self.assertEqual(first('100 Mebibytes in Kibibytes'), '102,400 KiB')
        self.assertEqual(first('100 gb to mb'), '100,000 MB')
        self.assertEqual(first('100gb to kb'), '100,000,000 kB')
        self.assertEqual(first('100gb mb'), '100,000 MB')
        self.assertEqual(first('400MiB in kib'), '409,600 KiB')
        self.assertEqual(first('2tb gb'), '2,000 GB')
        self.assertEqual(first('1b kb'), '0.001 kB')

    def test_standards(self):
        self.assertEqual(first('1MB in KB'), '1,000 kB')
        self.assertEqual(first('1MiB in KiB'), '1,024 KiB')
        self.assertEqual(first('1 mb in kb', datastorage_force_binary='1'), '1,024 kB')
        self.assertEqual(first('1 gib to mb'), '1,073.741824 MB')
        self.assertEqual(first('8 bit to b'), '1 B')
        self.assertEqual(first('1 kb to bit'), '8,000 bit')


class Currency(Base):
    def test_readme(self):
        self.assertEqual(first('100 us dollars in mexican pesos'), '2,000 MXN')
        self.assertEqual(first('100 canadian dollars in argentinian peso'), '71,428.57 ARS')
        for query in ('100 euros to dollars', '100 euros in dollars', '100 euros as dollars', '100€ to $',
                      '100 eur usd', '100eur usd', '100 EUR = USD'):
            self.assertEqual(first(query), '111.11 USD', query)
        self.assertEqual(first('100 euros a dolares', language='es_ES'), '111.11 USD')
        self.assertEqual(first('100 usd to mxn'), '2,000 MXN')
        self.assertEqual(first('100 usd mxn'), '2,000 MXN')
        self.assertEqual(first('100usd yen'), '15,000 JPY')
        self.assertEqual(first('100 ¥ in €'), '0.60 EUR')
        self.assertEqual(first('100¥ €'), '0.60 EUR')

    def test_base_currencies(self):
        self.assertEqual(titles('100eur'), ['111.11 USD', '2,222.22 MXN'])
        self.assertEqual(titles('100 usd'), ['2,000 MXN'])                 # never converts to itself
        self.assertEqual(titles('100 usd to'), ['2,000 MXN'])              # still typing the target
        self.assertEqual(titles('100 usd', base_currencies='USD'), ['100 USD'])
        self.assertEqual(titles('120 euros', base_currencies='idr,jpy'), ['2,133,333.33 IDR', '20,000 JPY'])

    def test_default_base_currencies(self):
        settings = core.Settings({'base_currencies': ''})
        settings._locale = 'en_ID'
        self.assertEqual(settings.base_currencies, ['IDR', 'USD', 'EUR', 'MYR'])
        settings = core.Settings({'base_currencies': ''})
        settings._locale = 'ms_MY'
        self.assertEqual(settings.base_currencies, ['MYR', 'USD', 'EUR'])

    def test_rows(self):
        row = ask('1234.5 usd to mxn')['items'][0]
        self.assertEqual(row['title'], '24,690 MXN')
        self.assertTrue(row['subtitle'].startswith('1 USD = 20 MXN'))
        self.assertEqual(row['arg'], '24,690')
        self.assertEqual(row['mods']['cmd']['arg'], '24690')
        self.assertEqual(row['mods']['alt']['arg'], '20')
        self.assertEqual(row['icon'], {'path': 'flags/MXN.png'})
        self.assertTrue(os.path.exists(os.path.join(ROOT, 'flags', 'MXN.png')))

    def test_names_and_symbols(self):
        self.assertEqual(first('100 usd to indonesian rupiah'), '1,600,000 IDR')
        self.assertEqual(first('100 usd to rupiah'), '1,600,000 IDR')
        self.assertEqual(first('1600000 rp to usd'), '100 USD')
        self.assertEqual(first('45 rm to usd'), '10 USD')
        self.assertEqual(first('100 pounds to euros'), '112.5 EUR')
        self.assertEqual(first('100 pounds to kg'), '45.359237 kg')       # the weight, not sterling
        self.assertEqual(first('100 usd to sek', language='sv_SE'), '1,000 SEK')
        self.assertEqual(first('100 kr till usd', language='sv_SE'), '10 USD')

    def test_decimals_setting(self):
        self.assertEqual(first('1 usd to eur', currency_decimals='4'), '0.9000 EUR')
        self.assertEqual(first('10 usd to cad', currency_decimals='0'), '14 CAD')
        self.assertEqual(first('1 idr to usd'), '0.000063 USD')

    def test_big_numbers(self):
        self.assertEqual(first('150k idr to usd'), '9.38 USD')
        self.assertEqual(first('2.5m idr to usd'), '156.25 USD')
        self.assertEqual(first('2 million idr to usd'), '125 USD')
        self.assertEqual(first('1 b idr to usd'), '62,500 USD')
        self.assertEqual(first('5 mil pesos mexicanos a usd', language='es_ES'), '250 USD')
        self.assertEqual(first('1 000 000 idr to usd'), '62.5 USD')

    def test_comma_decimals(self):
        comma = {'decimal_separator': 'comma', 'number_output_format': 'dot_comma'}
        self.assertEqual(first('1.234,5 usd to mxn', **comma), '24.690 MXN')
        self.assertEqual(first('0,5 usd to mxn', **comma), '10 MXN')

    def test_unknown(self):
        self.assertEqual(titles('100 usd to id'), [])
        self.assertEqual(titles('100 xyz'), [])
        self.assertEqual(first('100 usd to kpw'), 'No exchange rate available for KPW')


class Crypto(Base):
    def test_readme(self):
        self.assertEqual(first('2 bitcoins to dollars'), '120,000 USD')
        self.assertEqual(first('0.1 bitcoin in dollars'), '6,000 USD')
        self.assertEqual(first('5 bitcoins in ethereum'), '100 ETH')
        self.assertEqual(first('1 ethereum to ¥'), '450,000 JPY')
        self.assertEqual(first('10 ethereum in mxn'), '600,000 MXN')
        self.assertEqual(first('1eth btc'), '0.05 BTC')
        self.assertEqual(titles('1btc'), ['60,000 USD', '1,200,000 MXN'])

    def test_original_test_file(self):
        self.assertEqual(first('100 btc pln'), '24,000,000 PLN')          # the zloty, not the PLN token
        self.assertEqual(first('100 usd btc'), '0.0016666667 BTC')
        self.assertEqual(first('2500 usd eth'), '0.83333333 ETH')
        self.assertEqual(first('45000 mxn eth'), '0.75 ETH')
        self.assertEqual(first('50 btc eth'), '1,000 ETH')
        self.assertEqual(first('2 eth mxn'), '120,000 MXN')
        self.assertEqual(titles('2 btc'), ['120,000 USD', '2,400,000 MXN'])

    def test_rows(self):
        row = ask('5 bitcoins in ethereum')['items'][0]
        self.assertTrue(row['subtitle'].startswith('1 BTC = 20 ETH - Ethereum'))
        self.assertEqual(row['mods']['alt']['arg'], '20')
        self.assertNotIn('icon', row)

    def test_satoshi(self):
        self.assertEqual(first('1000 sats to usd'), '0.60 USD')           # not the SATS token
        self.assertEqual(first('100000000 satoshis to btc'), '1 BTC')

    def test_ordinary_words_are_not_coins(self):
        for query in ('5 why', '1 a', '100 km', '3 in why', '1 on 1', '20 20 vision', '2fa', '1password',
                      '10 downing street', '4k video downloader', '5 minute timer', '365 days'):
            self.assertEqual(titles(query), [], query)
        self.assertEqual(first('5 why to usd'), '2.5 USD')               # spelled out, any coin works
        self.assertEqual(first('100 km to usd'), '100 USD')


class RateStates(unittest.TestCase):
    """What the user sees while rates are missing or being refreshed."""

    def setUp(self):
        shutil.rmtree(core.cache_dir(), ignore_errors=True)
        self._start = rates.start_refresh
        self.started = []
        rates.start_refresh = lambda kind: (self.started.append(kind), self._running)[1]
        self._running = True

    def tearDown(self):
        rates.start_refresh = self._start
        write_fixtures()

    def test_first_run_shows_progress_and_asks_for_a_rerun(self):
        reply = ask('100 usd to mxn')
        self.assertEqual([row['title'] for row in reply['items']], ['Updating rates...'])
        self.assertFalse(reply['items'][0]['valid'])
        self.assertEqual(reply['rerun'], 0.3)
        self.assertEqual(self.started, ['currency'])

    def test_stale_rates_answer_immediately_and_refresh(self):
        write_fixtures(age=7 * 86400)
        reply = ask('100 usd to mxn')
        self.assertEqual(reply['items'][0]['title'], '2,000 MXN')
        self.assertEqual(reply['rerun'], 0.5)
        self.assertEqual(self.started, ['currency'])

    def test_fresh_rates_do_not_refresh(self):
        write_fixtures()
        reply = ask('100 usd to mxn')
        self.assertNotIn('rerun', reply)
        self.assertEqual(self.started, [])

    def test_failed_download_without_cache_says_so(self):
        self._running = False
        with open(os.path.join(core.cache_dir(), 'currency.err'), 'w') as handle:
            json.dump({'time': time.time(), 'message': 'offline'}, handle)
        reply = ask('100 usd to mxn')
        self.assertEqual(reply['items'][0]['title'], 'Unable to get currencies data')
        self.assertNotIn('rerun', reply)
        self.assertEqual(self.started, [])           # backs off instead of hammering the network

    def test_failed_download_keeps_old_rates(self):
        self._running = False
        write_fixtures(age=7 * 86400)
        with open(os.path.join(core.cache_dir(), 'currency.err'), 'w') as handle:
            json.dump({'time': time.time(), 'message': 'offline'}, handle)
        reply = ask('100 usd to mxn')
        self.assertEqual(reply['items'][0]['title'], '2,000 MXN')
        self.assertNotIn('rerun', reply)

    def test_crypto_only_needs_crypto_data(self):
        write_fixtures()
        os.remove(os.path.join(core.cache_dir(), 'currency.json'))
        self.assertEqual(first('1 eth btc'), '0.05 BTC')
        self.assertEqual(first('1 btc to usd'), 'Updating rates...')


class Dates(Base):
    FULL = 'j F, Y, g:i:s a'

    def test_now_and_timestamp(self):
        self.assertEqual(when(''), ['13 November, 2026, 8:15:00 pm', '1794575700'])
        self.assertEqual(when('1577836800'), ['1 January, 2020, 7:00:00 am', '6 years ago', '1577836800'])
        self.assertEqual(when('1577836800000')[0], '1 January, 2020, 7:00:00 am')

    def test_readme_relative(self):
        self.assertEqual(when('+15 days')[:2], ['28 November, 2026, 8:15:00 pm', '2 weeks, 1 day'])
        self.assertEqual(when('now plus 3 days')[0], '16 November, 2026, 8:15:00 pm')
        self.assertEqual(when('today + 3 workdays')[0], '18 November, 2026, 12:00:00 am')
        self.assertEqual(when('now + 3 workdays')[0], '18 November, 2026, 8:15:00 pm')
        self.assertEqual(when('+ 3 workdays')[0], '18 November, 2026, 8:15:00 pm')
        self.assertEqual(when('+15 years')[0], '13 November, 2041, 8:15:00 pm')

    def test_readme_until_and_edges(self):
        self.assertEqual(when('days until 31 december'), ['48 days'])
        self.assertEqual(when('start of year')[0], '1 January, 2026, 12:00:00 am')
        self.assertEqual(when('start of 2021')[0], '1 January, 2021, 12:00:00 am')
        self.assertEqual(when('end of year')[0], '31 December, 2026, 11:59:59 pm')
        self.assertEqual(when('end of 2021')[0], '31 December, 2021, 11:59:59 pm')

    def test_readme_spanish(self):
        self.assertEqual(when('inicio de 2020', language='es_ES')[0], '1 enero, 2020, 12:00:00 am')
        self.assertEqual(when('fin de 2020', language='es_ES')[0], '31 diciembre, 2020, 11:59:59 pm')
        self.assertEqual(when('dias hasta 31 diciembre', language='es_ES'), ['48 días'])
        self.assertEqual(when('ahora más 3 días', language='es_ES')[0], '16 noviembre, 2026, 8:15:00 pm')

    def test_readme_absolute(self):
        expected = '31 December, 2021, 6:00:00 pm'
        self.assertEqual(when('31 December, 2021 18:00:00')[0], expected)
        self.assertEqual(when('31/12/2021 18:00:00')[0], expected)
        self.assertEqual(when('12/31/2021 18:00:00')[0], expected)        # impossible month flips it
        self.assertEqual(when('2021-12-31 18:00')[0], expected)
        self.assertEqual(when('december 31 2021 6pm')[0], expected)
        self.assertEqual(when('31st of december 2021 at 6:00 pm')[0], expected)

    def test_ambiguous_dates_follow_the_setting(self):
        self.assertEqual(when('01/02/2026', date_order='dmy')[0], '1 February, 2026, 12:00:00 am')
        self.assertEqual(when('01/02/2026', date_order='mdy')[0], '2 January, 2026, 12:00:00 am')
        self.assertEqual(when('01-02-2026', date_order='mdy')[0], '1 February, 2026, 12:00:00 am')

    def test_readme_difference(self):
        self.assertEqual(when('25 December, 2021 - 31 December, 2021'), ['6 days'])
        self.assertEqual(when('31-11-2019 - 21-11-2019')[0], '1 week, 3 days')
        self.assertEqual(when('11/31/2019 - 11/21/2019')[0], '1 week, 3 days')
        self.assertEqual(when('1 january 2020 - 15 march 2021'), ['1 year, 2 months, 2 weeks', '439 days'])

    def test_more_expressions(self):
        self.assertEqual(when('now minus 3 days')[:2], ['10 November, 2026, 8:15:00 pm', '3 days ago'])
        self.assertEqual(when('3 days ago')[0], '10 November, 2026, 8:15:00 pm')
        self.assertEqual(when('tomorrow')[0], '14 November, 2026, 8:15:00 pm')
        self.assertEqual(when('yesterday 9am')[0], '12 November, 2026, 9:00:00 am')
        self.assertEqual(when('next friday 3pm')[0], '20 November, 2026, 3:00:00 pm')
        self.assertEqual(when('monday')[0], '16 November, 2026, 12:00:00 am')
        self.assertEqual(when('last monday')[0], '9 November, 2026, 12:00:00 am')
        self.assertEqual(when('next month')[0], '13 December, 2026, 8:15:00 pm')
        self.assertEqual(when('+1 week 2 days')[0], '22 November, 2026, 8:15:00 pm')
        self.assertEqual(when('end of month')[0], '30 November, 2026, 11:59:59 pm')
        self.assertEqual(when('start of next month')[0], '1 December, 2026, 12:00:00 am')
        self.assertEqual(when('first day of next month')[0], '1 December, 2026, 12:00:00 am')
        self.assertEqual(when('end of february 2024')[0], '29 February, 2024, 11:59:59 pm')
        self.assertEqual(when('2021')[0], '1 January, 2021, 12:00:00 am')
        self.assertEqual(when('hours until tomorrow'), ['24 hours'])
        self.assertEqual(when('days since 1 january'), ['316 days'])
        self.assertEqual(when('days until 1 january'), ['49 days'])          # the coming one, not last year's
        self.assertEqual(when('days since 25 december'), ['323 days'])       # the last one, not next month's
        self.assertEqual(when('days until 1 january 2026'), ['316 days'])    # an explicit year is respected
        self.assertEqual(when('31 january 2026 + 1 month')[0], '28 February, 2026, 12:00:00 am')

    def test_time_zones(self):
        self.assertEqual(when('3pm utc')[0], '13 November, 2026, 10:00:00 pm')       # asked for upstream
        self.assertEqual(when('now in tokyo')[0], '13 November, 2026, 10:15:00 pm')
        self.assertEqual(when('utc')[0], '13 November, 2026, 1:15:00 pm')
        self.assertEqual(when('9am in new york')[:2], ['12 November, 2026, 9:00:00 pm', '11 hours ago'])
        self.assertEqual(when('11pm in london')[:2], ['13 November, 2026, 4:00:00 pm', '2 hours, 45 minutes'])
        self.assertEqual(when('2021-12-31T18:00:00Z')[0], '1 January, 2022, 1:00:00 am')
        self.assertEqual(when('2021-12-31 18:00 +09:00')[0], '31 December, 2021, 4:00:00 pm')
        self.assertEqual(when('', timezone='America/Mexico_City')[0], '13 November, 2026, 7:15:00 am')

    def test_formats(self):
        rows = when('31 december 2021 18:05:09', date_format='Y-m-d H:i:s | D, d M y | l jS F Y | c | U')
        self.assertEqual(rows[:5], ['2021-12-31 18:05:09', 'Fri, 31 Dec 21', 'Friday 31st December 2021',
                                    '2021-12-31T18:05:09+07:00', '1640948709'])
        self.assertEqual(when('1 march 2021', date_format='l j F', language='sv_SE')[0], 'måndag 1 mars')

    def test_invalid(self):
        self.assertEqual(when('garbage words'), ['...'])
        self.assertEqual(when('31 foo 2021'), ['...'])
        self.assertEqual(when('25:99'), ['...'])


class Colors(Base):
    def test_conversions(self):
        self.assertEqual(titles('#ff6600 to hsl', 'color'), ['hsl(24, 100%, 50%)'])
        self.assertEqual(titles('rgb(255, 102, 0) to hex', 'color'), ['#ff6600'])
        self.assertEqual(titles('hsl(24, 100%, 50%) to rgb', 'color'), ['rgb(255, 102, 0)'])
        self.assertEqual(titles('tomato to hex', 'color'), ['#ff6347'])
        self.assertEqual(titles('#00f to rgb', 'color'), ['rgb(0, 0, 255)'])
        self.assertEqual(titles('#000 to hex', 'color'), ['#000000'])               # zeros used to be dropped
        self.assertEqual(titles('rgb(0, 10, 5) to hex', 'color'), ['#000a05'])
        self.assertEqual(titles('rgba(170, 161, 35, 0.85) to hex', 'color'), ['#aaa123d9'])
        self.assertEqual(titles('rgb(52 48 48 / 83%) to hex', 'color'), ['#343030d4'])
        self.assertEqual(titles('#ff0000 = cmyk', 'color'), ['cmyk(0%, 100%, 100%, 0%)'])
        self.assertEqual(titles('lab(53.24% 80.09 67.2) to hex', 'color'), ['#ff0000'])
        self.assertEqual(titles('oklch(62.8% 0.2577 29.23) to hex', 'color'), ['#ff0000'])
        self.assertEqual(titles('255, 102, 0 to hex', 'color'), ['#ff6600'])

    def test_every_format(self):
        self.assertEqual(titles('#ff0000', 'color'), [
            '#ff0000', 'rgb(255, 0, 0)', 'hsl(0, 100%, 50%)', 'hwb(0 0% 0%)', 'hsv(0, 100%, 100%)',
            'cmyk(0%, 100%, 100%, 0%)', 'lab(53.24% 80.09 67.2)', 'oklch(62.8% 0.2577 29.23)'])
        self.assertEqual(titles('#808080 to hsl', 'color'), ['hsl(0, 0%, 50%)'])
        self.assertEqual(titles('white to cmyk', 'color'), ['cmyk(0%, 0%, 0%, 0%)'])
        self.assertEqual(titles('black to cmyk', 'color'), ['cmyk(0%, 0%, 0%, 100%)'])

    def test_round_trips(self):
        from ca import color
        for name in ('tomato', 'rebeccapurple', 'teal', 'gold', 'white', 'black', 'gray'):
            original = color.parse_color(name)
            for kind in ('hex', 'rgb', 'hsl', 'hwb', 'hsv', 'lab', 'oklch'):
                back = color.parse_color(color.render(kind, original))
                self.assertIsNotNone(back, (name, kind))
                for a, b in zip(original[:3], back[:3]):
                    self.assertLessEqual(abs(a - b), 2.6, (name, kind, color.render(kind, original)))

    def test_invalid(self):
        self.assertEqual(titles('nonsense', 'color'), ['...'])
        self.assertEqual(titles('', 'color'), ['...'])
        self.assertEqual(titles('#ff0000 to foo', 'color'), ['There is no support for the foo color space yet'])


class Selection(Base):
    """The calc keyword, the Universal Action and the hotkey: text from anywhere."""

    def test_amounts_written_symbol_first(self):
        self.assertEqual(titles('$25', 'any', base_currencies='MXN'), ['500 MXN'])
        self.assertEqual(titles('Rp 1.600.000', 'any', base_currencies='USD'), ['100 USD'])
        self.assertEqual(first('USD 100 to MXN', 'any'), '2,000 MXN')
        self.assertEqual(first('€1.234,56 to usd', 'any'), '1,371.73 USD')
        self.assertEqual(first('costs about $25.', 'any', base_currencies='MXN'), '500 MXN')
        self.assertEqual(first('BTC 0.5 to usd', 'any'), '30,000 USD')

    def test_words_before_the_amount_are_dropped(self):
        self.assertEqual(first('it is 25 usd', 'any', base_currencies='MXN'), '500 MXN')
        self.assertEqual(first('roughly 100 km to miles', 'any'), '62.13711922 mi')
        self.assertEqual(first('a 5 day trip', 'any'), "Calculate Anything can't read this")

    def test_everything_typed_without_a_keyword_works(self):
        self.assertEqual(first('100 usd to mxn', 'any'), '2,000 MXN')
        self.assertEqual(first('120 + 30%', 'any'), '156')
        self.assertEqual(first('400 + vat', 'any'), '464')

    def test_colors_and_timestamps(self):
        self.assertEqual(first('#ff6600', 'any'), '#ff6600')
        self.assertEqual(first('rgb(255, 102, 0)', 'any'), '#ff6600')
        self.assertEqual(first('1577836800', 'any'), '1 January, 2020, 7:00:00 am')

    def test_hints(self):
        self.assertEqual(first('1.500.000', 'any'), 'Add a unit or currency after the number')
        self.assertEqual(first('hello world', 'any'), "Calculate Anything can't read this")
        self.assertEqual(first('', 'any'), 'Calculate Anything')


class Dispatch(Base):
    def test_info_plist_wiring(self):
        import plistlib
        with open(os.path.join(ROOT, 'info.plist'), 'rb') as handle:
            plist = plistlib.load(handle)
        objects = plist['objects']
        outputs = [o for o in objects if o['type'] == 'alfred.workflow.output.clipboard']
        copy = next(o['uid'] for o in outputs if not o['config']['autopaste'])
        paste = next(o['uid'] for o in outputs if o['config']['autopaste'])
        filters = [o for o in objects if o['type'] == 'alfred.workflow.input.scriptfilter']
        self.assertEqual(len(filters), 16)
        for item in filters:
            links = set((c['destinationuid'], c['modifiers']) for c in plist['connections'][item['uid']])
            self.assertEqual(links, {(copy, 0), (copy, 1048576), (copy, 524288), (paste, 262144)},
                             item['config']['keyword'])
        calc = next(o['uid'] for o in filters if o['config']['keyword'] == '{var:keyword_calc}')
        for kind in ('universalaction', 'hotkey'):
            trigger = next(o['uid'] for o in objects if o['type'].endswith(kind))
            self.assertEqual([c['destinationuid'] for c in plist['connections'][trigger]], [calc])
        keywords = dict((f['variable'], f['config']['default']) for f in plist['userconfigurationconfig']
                        if f['variable'].startswith('keyword_'))
        self.assertEqual(keywords, {'keyword_time': 'time', 'keyword_vat': 'vat', 'keyword_color': 'color',
                                    'keyword_calc': 'calc'})

    def test_every_reply_is_valid_alfred_json(self):
        for query in ('100 usd to mxn', '100 km to m', '12px', '120 + 30%', '2 gb to mb', '400 + vat', 'zzz', ''):
            reply = ask(query)
            json.dumps(reply)
            for row in reply['items']:
                self.assertIsInstance(row['title'], str)
                self.assertIsInstance(row.get('subtitle', ''), str)
                if 'arg' in row:
                    self.assertIsInstance(row['arg'], str)
                for modifier in (row.get('mods') or {}).values():
                    self.assertIsInstance(modifier['arg'], str)

    def test_needs_a_leading_number(self):
        self.assertEqual(titles('km to m'), [])
        self.assertEqual(titles('1'), [])
        self.assertEqual(titles('12'), [])

    def test_fast_enough_to_run_on_every_keystroke(self):
        started = time.time()
        for _ in range(50):
            ask('100 usd to mxn')
            ask('100 km to miles')
            ask('1password')
        per_query = (time.time() - started) / 150.0
        self.assertLess(per_query, 0.02, 'a query takes %.1f ms' % (per_query * 1000))


def tearDownModule():
    shutil.rmtree(DATA, ignore_errors=True)


if __name__ == '__main__':
    unittest.main(verbosity=1)
