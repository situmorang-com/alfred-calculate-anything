# Architecture

How a keystroke in Alfred becomes a list of results. What the workflow must do is in `docs/PRD.md`; why it is built this way is in `docs/MEMORY.md`, "Decisions".

## Request flow

```
Alfred: "100 usd to idr"
  │  Script Filter whose keyword is the first character ("1"), argument "00 usd to idr"
  ▼
/bin/zsh --no-rcs:  PYTHONPYCACHEPREFIX="$alfred_workflow_cache/pycache" exec /usr/bin/python3 calculate.py "1$1"
  ▼
calculate.py        argv → (action, query). --refresh and --clear are sub-commands. A crash → stderr + empty result.
  ▼
ca/app.py run()     Context(settings, language) → one calculator → {"items": [...], "rerun": seconds?}
  │   no keyword:   units → percentage → pxemrem → vat → datastorage → money   (the first one that answers wins)
  │   keywords:     timecalc.keyword · vat.keyword · color.keyword
  ▼
JSON on stdout → Alfred shows the rows → Return / ⌘ Return / ⌥ Return → Copy to Clipboard
```

The money calculator reads rates from a cache that a detached process refreshes; see "Rates".

## Files

| Path | Role |
| --- | --- |
| `calculate.py` | Entry point: flags, `ca.app.run`, JSON out. |
| `ca/app.py` | Which calculator answers, and the response envelope. |
| `ca/core.py` | Shared plumbing: `Settings`, `Lang`, `Context`, query cleaning and splitting, number parsing and formatting, row builders. |
| `ca/units.py` | Unit tables and conversion. |
| `ca/datastorage.py` | Data sizes. |
| `ca/percentage.py` | Percentages. |
| `ca/pxemrem.py` | CSS sizes. |
| `ca/vat.py` | VAT, keyword and inline forms. |
| `ca/money.py` | Currency and crypto: recognising terms, converting, building rows. |
| `ca/rates.py` | Rate sources, cache files, background refresh, `--refresh`, `--clear`. |
| `ca/timecalc.py` | The `time` keyword: parsing, date arithmetic, zones, PHP-style formatting. |
| `ca/color.py` | The `color` keyword and swatch icons. |
| `lang/<code>.json` | Display strings per language, including currency names. |
| `lang/<code>-keys.json` | What users may type per language: keywords, stop words, time phrases, multipliers. |
| `data/regions.json` | ISO region → currency, for the default base currency. |
| `data/crypto-symbols.json` | Coins recognised before the first price download. |
| `flags/<CODE>.png` | Currency row icons. |
| `info.plist` | Alfred objects, connections and the configuration panel. |
| `tests/test_calculate.py` | Offline test suite. |
| `tools/alfredctl.swift` | Helper for testing inside Alfred; see `docs/MEMORY.md`. |

Each module's docstring lists the query forms it accepts.

## Alfred wiring (`info.plist`)

- One Script Filter per possible first character: keywords `0` to `9`, `.` and `-`, with "with space" off and the argument optional. Typing `100 usd` matches keyword `1` with argument `00 usd`, and the script puts the `1` back. The `.` and `-` filters call `--dot` and `--neg`, which restore `0.` or `-` and send nothing unless a digit follows.
- Keyword Script Filters for `{var:keyword_time}`, `{var:keyword_vat}` and `{var:keyword_color}` (configurable, defaulting to `time`, `vat` and `color`), argument required.
- Every Script Filter uses script language 11 (`/bin/zsh --no-rcs`), receives the query as `$1`, has Alfred's own filtering off, runs immediately, and uses queue mode 2, so a new keystroke terminates the running script.
- Each filter connects to the single Copy to Clipboard output three times: plain (modifiers `0`), ⌘ (`1048576`) and ⌥ (`524288`). The output copies `{query}`, which is the row's `arg` or the modifier's `arg`.
- `_caclear` keyword → Run Script `calculate.py --clear` → Post Notification.
- The time filter's icon is the PNG named after its UID (`301DCF01-…png`). Rows without an icon of their own use their filter's icon, or `icon.png`.
- The configuration panel (`userconfigurationconfig`) defines 19 variables. Alfred passes them to the script as environment variables and stores the owner's values in `prefs.plist` in this folder.

## Settings

`ca.core.Settings` reads those environment variables; its `__init__` lists each variable with its default, and `docs/MANUAL.md`, "Settings", explains them to users. Values derived from the Mac when a setting is empty:

- Locale: `AppleLocale` from `~/Library/Preferences/.GlobalPreferences.plist`. Its region (`ID` in `en_ID`) gives the local currency through `data/regions.json`; a `@currency=XXX` locale suffix wins.
- Base currencies: local currency, USD, EUR, MYR, without duplicates.
- Time zone: the target of `/etc/localtime`.
- Slash dates: month first only for regions in `core.MONTH_FIRST_REGIONS` (US-style).

## Language data

`ca.core.Lang(code)` builds two layers:

- Strings: `lang/<code>.json` over `lang/en_EN.json`, section by section.
- Keywords: `custom-keys.json` in the workflow data folder, over `lang/<code>-keys.json`, over `lang/en_EN-keys.json`. A higher layer wins on conflicts; lists (stop words, time phrases) are combined.

`keywords(section)` lower-cases every key and adds an accent-free spelling, and `lookup()` also tries the accent-free form, so `dias` finds `días`.

## Queries

- `clean_query` composes Unicode (Alfred delivers decomposed accents), maps `µ` to `μ`, `²` to `2`, `³` to `3` and non-breaking spaces to spaces, collapses whitespace and lower-cases.
- `split_amount` takes the leading number with `core.NUMBER`: `1350.5`, `1,350.50`, `1.350,50`, `.5`, and spaces only as real thousands groups (`1 000 000`, never `20 20`).
- `term_splits(rest, stop_words)` yields every reading of `<from> [stop word] <to>`, splits at stop words first, then at each space. Multi-word terms (`us dollars`, `miles per hour`) and stop words that are also units (`100 cm in in`) both work. A calculator takes the first reading it can resolve.
- `parse_number` follows the decimal-separator setting.

## Numbers

`format_number(value, decimals, settings)` writes results and `plain_number` writes the ⌘ Return copy.

- 14 significant digits hide float noise (`0.1 + 0.2` → `0.3`); rounding is half up.
- `decimals = -1`: every meaningful decimal, at most 8; below 1, up to 8 after the leading zeros.
- `decimals >= 0`: that many places, except that values under 0.1 keep that many significant digits and values over 1 are not padded (`150.5`, not `150.50`).
- Separators follow the number-format setting.

## Calculators

A no-keyword calculator is a module with `process(ctx, query)`. It returns `None` for "not mine, try the next one", or a list of rows, which may be a single message row. The order in `app.auto` is deliberate:

1. `units` comes before `money` (`100 pounds to kg` is a weight) and before `pxemrem` (`12 pt to l` is pints).
2. `percentage` needs a `%` after the first character.
3. `pxemrem` needs px, em, rem or pt right after the number, followed by nothing but a CSS unit or `base`.
4. `vat` (inline) needs a VAT word at the end.
5. `datastorage` comes before `money`, so `2 gb` is never a coin.
6. `money` comes last because it has the largest vocabulary.

### Units (`ca/units.py`)

- `UNITS[category][unit]` is the size of one unit in the category's base unit. Temperature units are `(to_kelvin, from_kelvin)` function pairs.
- `build_index(lang)` maps every typed form to `(category, unit)` candidates: the unit keys, then keyword-file aliases (exact case first, so `Nm` stays newton metres and `nm` nanometres), then `FALLBACKS` (`h` hour, `m` minute, `d` day, `w` week, `oz` fluid ounce). `resolve` also drops a plural `s`.
- `process` takes the first split whose two terms share a category. When both terms resolve but never share one, it returns the error row.
- `_rows` adds the mixed row from `FRACTION` when the result has a fraction whose remainder is a real part of the larger unit. `DISPLAY` and `TIME_WORDS` label results.

### Money (`ca/money.py`)

- `Money.resolve(term, explicit)` returns `('fiat', CODE)`, `('crypto', SYMBOL)` or `None`:
  1. digits only: `None`;
  2. fiat: ISO code, keyword file, currency name in English or the current language, then with a plural `s` dropped;
  3. crypto: keyword file, ticker, coin name, then with a plural `s` dropped. Accepted when the query has an explicit target, or when the ticker is longer than one letter and ranks within `BARE_COIN_RANK` (250).
- `process` tries a multiplier reading first (`150k idr`), skips readings whose first term is a stop word, and converts to the target or else to the base currencies. A bare coin whose term is also a unit (`100 km`) is skipped.
- `rows` loads only the rate kinds the conversion needs and converts through US dollars: `single = usd_per(source) / usd_per(target)`, `total = amount × single`. Subtitles carry the unit rate, the coin's name and the rate's age.

### Time (`ca/timecalc.py`)

- `translate` rewrites the query into the English vocabulary the parser knows: keyword-file words first (`ahora` → `now`, `mañana` → `+1 day`), then the language's month, weekday and unit names.
- `keyword` tries, in order: empty or `now`; `A - B` (a difference, unless `B` is purely relative such as `3 days`); `<unit> until|since <date>`; `start of` / `end of`; a bare number as a Unix timestamp (12 digits or more means milliseconds; 4 digits is a year); anything else through `parse`.
- `parse(text, now, zone, month_first)` consumes tokens left to right: ISO and slash, dot or dash dates; `31 december 2021`; `december 31`; clock times with am/pm; `+N unit` and `N unit`; `next|last|this <unit|weekday>`; weekdays; `first|last day of`; `now`, `today`, `tomorrow`, `yesterday`, `noon`, `midnight`, `ago`; `@timestamp`; a bare year; zones. It builds the moment in the source zone, applies the steps, and converts to the display zone. Any token it cannot read makes the query invalid.
- Zones: `ZONE_ALIASES`, then IANA names by full name or city (`tokyo`, `new york`), then `±hh:mm` offsets.
- `php_date` implements PHP `date()` letters with the language's month and weekday names.

### Color (`ca/color.py`)

`parse_color` returns `(r, g, b, alpha)`; `render(kind, color)` writes one format; `swatch` draws a 64 × 64 PNG per color into `cache/swatches/` and empties that folder past 300 files. Lab and OKLCH use the standard sRGB D65 conversions.

### Percentage, CSS sizes, VAT, data storage

Small regex-driven modules; their docstrings list the accepted forms.

## Rates (`ca/rates.py`)

Files in `$alfred_workflow_data/cache/`:

| File | Content |
| --- | --- |
| `currency.json` | `{source, updated, fetched, rates: {CODE: units per USD}, problems}` |
| `crypto.json` | `{source, updated, fetched, coins: {SYMBOL: [name, USD price, rank]}, problems}` |
| `<kind>.lock` | present while a refresh runs |
| `<kind>.err` | `{time, message}` of the last failed refresh |

`get(kind, max_age)` returns `(data, state)`:

| State | Situation | The user sees |
| --- | --- | --- |
| `fresh` | cache younger than `max_age` | results |
| `refreshing` | cache older, refresh running | results; Alfred re-runs the query in 0.5 s |
| `stale` | cache older, no refresh running (the last one failed under 20 s ago) | results |
| `loading` | no cache, refresh running | "Updating rates..."; re-run in 0.3 s |
| `error` | no cache, refresh failed | "Unable to get currencies data" |

A refresh writes the lock, then starts `calculate.py --refresh <kind>` detached. That process tries the sources in order and writes the cache atomically (temporary file, then `os.replace`), or writes `<kind>.err`. `http_get` uses `urllib` and falls back to `/usr/bin/curl` when Python cannot connect.

The source lists are `CURRENCY_SOURCES` and `CRYPTO_SOURCES`, tried in order; a configured Fixer or CoinMarketCap key puts that service first. Rules the lists do not show:

- Currency rates are kept only for codes named in `lang/en_EN.json`, "currency", and rebased to USD. Codes the winning source lacks are filled from the fawazahmed0 currency API.
- Coins: tickers are cleaned, a shared ticker goes to the higher-ranked coin, the list is capped at 2,500, and `SAT` (one hundred-millionth of a bitcoin) is added.

## Output contract

`core.item()` builds each row: `title`, `subtitle`, `arg` (what Return copies), `valid` (true only with an `arg`), `icon`, `mods.cmd` and `mods.alt` (`arg` and `subtitle`), `text.copy` (⌘C) and `text.largetype` (⌘L). `core.message()` builds an informational row with `valid: false`. `app.run` adds `rerun` when a calculator asked for one.

## Tests (`tests/test_calculate.py`)

- Offline. The suite points `alfred_workflow_data` at a temporary folder and writes fixture rates (USD 1, EUR 0.9, IDR 16,000, BTC at 60,000 USD, and so on).
- `Dates` pins the clock to Friday 2026-11-13, 20:15, Asia/Jakarta.
- `RateStates` replaces `rates.start_refresh` to walk through every cache state without a network.
- `Dispatch` checks that every reply is valid JSON with string arguments, and that a query takes under 20 ms in process.

## Extending

| To add | Do this |
| --- | --- |
| A unit | Add it to `UNITS` (its size in the base unit); a label in `DISPLAY` and a mixed-row partner in `FRACTION` if useful; the names people type in `lang/en_EN-keys.json`, "units"; a test. |
| A currency | Its name in `lang/en_EN.json`, "currency" (this list also decides which codes are kept from the sources); aliases in `lang/en_EN-keys.json`, "currency"; `flags/<CODE>.png` at 96 × 96. |
| A rate source | A function returning `(rates per USD, updated time)` appended to `CURRENCY_SOURCES`, or one returning a coin dictionary built with `_add_coin`, appended to `CRYPTO_SOURCES`. |
| A language | Copy both `en_EN` files to the new code and translate them; add the code to the language popup in `info.plist`. |
| A no-keyword calculator | A module with `process(ctx, query)`, placed deliberately in the order in `app.auto`. |
| A keyword | A Script Filter in `info.plist` connected to the clipboard output like the others, a flag in `calculate.py`, and a branch in `app.run`. |
