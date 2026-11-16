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
  │   no keyword:   units → bases → percentage → pxemrem → vat → datastorage → money   (the first one that answers wins)
  │   keywords:     timecalc.keyword · vat.keyword · color.keyword
  │   calc, Universal Action, hotkey:  app.selection (reshapes the text, then any of the above)
  │   $ € £ ¥:      the no-keyword calculators on app.selection_query's reshaped text, with no hint rows
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
| `ca/units.py` | Unit tables, conversion, defaults for a unit with no target, several-part amounts, durations. |
| `ca/bases.py` | Number bases. |
| `ca/datastorage.py` | Data sizes. |
| `ca/percentage.py` | Percentages. |
| `ca/pxemrem.py` | CSS sizes. |
| `ca/vat.py` | VAT, keyword and inline forms. |
| `ca/money.py` | Currency and crypto: recognising terms, converting, building rows. |
| `ca/rates.py` | Rate sources, cache files, background refresh, `--refresh`, `--clear`. |
| `ca/timecalc.py` | The `time` keyword: parsing, date arithmetic, zones, PHP-style formatting. |
| `ca/color.py` | The `color` keyword and swatch icons. |
| `lang/<code>.json` | Display strings per language, including currency names: `en_EN`, `id_ID`, `es_ES`, `sv_SE`. |
| `lang/<code>-keys.json` | What users may type per language: keywords, stop words, time phrases, multipliers. |
| `data/regions.json` | ISO region → currency, for the default base currency. |
| `data/crypto-symbols.json` | Coins recognised before the first price download. |
| `flags/<CODE>.png` | Currency row icons. |
| `info.plist` | Alfred objects, connections and the configuration panel. |
| `tests/test_calculate.py` | Offline test suite. |
| `tools/alfredctl.swift` | Helper for testing inside Alfred; see `docs/MEMORY.md`. |
| `tools/demo/` | The README animation: `storyboard.py` runs every keystroke of seven queries through `ca.app.run`, `render.swift` draws each frame in Alfred's Big Sur Dark theme, `make.sh` encodes `docs/images/demo.gif` with ffmpeg. |
| `docs/images/demo.gif` | The README animation (left out of the workflow package). |

Each module's docstring lists the query forms it accepts.

## Alfred wiring (`info.plist`)

- One Script Filter per possible first character: keywords `0` to `9`, `.` and `-`, with "with space" off and the argument optional. Typing `100 usd` matches keyword `1` with argument `00 usd`, and the script puts the `1` back. The `.` and `-` filters call `--dot` and `--neg`, which restore `0.` or `-` and send nothing unless a digit follows.
- Four more for amounts written symbol first, keywords `$`, `€`, `£` and `¥`: each calls `--symbol` with its symbol put back (`"\$$1"` in zsh), and `app.run` reshapes the text with `selection_query` before the no-keyword calculators. Unlike `calc`, it adds no hint rows, so `$` followed by anything else stays an ordinary search. Multi-letter symbols (`Rp`, `RM`) are not keywords: Alfred would run the filter for every query starting with those letters.
- Keyword Script Filters for `{var:keyword_time}`, `{var:keyword_vat}` and `{var:keyword_color}` (configurable, defaulting to `time`, `vat` and `color`), argument required.
- A `{var:keyword_calc}` Script Filter (default `calc`, argument optional) runs `--any`. The Universal Action (named Calculate Anything, text only) and an unassigned hotkey (argument: selection in macOS) both connect to it, so Alfred opens `calc <selected text>` and the text stays editable.
- Every Script Filter uses script language 11 (`/bin/zsh --no-rcs`), receives the query as `$1`, has Alfred's own filtering off, runs immediately, and uses queue mode 2, so a new keystroke terminates the running script.
- Each filter connects to the Copy to Clipboard output three times, plain (modifiers `0`), ⌘ (`1048576`) and ⌥ (`524288`), and to a second Copy to Clipboard output with auto-paste on ⌃ (`262144`). Both copy `{query}`: the row's `arg`, or the modifier's `arg`. Rows define no `ctrl` modifier, so ⌃ pastes the row's `arg`. `tests/test_calculate.py` checks this wiring.
- `_caclear` keyword → Run Script `calculate.py --clear` → Post Notification.
- The time filter's icon is the PNG named after its UID (`301DCF01-…png`). Rows without an icon of their own use their filter's icon, or `icon.png`.
- The configuration panel (`userconfigurationconfig`) defines 22 variables. Alfred passes them to the script as environment variables and stores the owner's values in `prefs.plist` in this folder.

## Settings

`ca.core.Settings` reads those environment variables; its `__init__` lists each variable with its default, and `docs/MANUAL.md`, "Settings", explains them to users. Values derived from the Mac when a setting is empty:

- Locale: `AppleLocale` from `~/Library/Preferences/.GlobalPreferences.plist`. Its region (`ID` in `en_ID`) gives the local currency through `data/regions.json`; a `@currency=XXX` locale suffix wins.
- Base currencies: local currency, USD, EUR, MYR, without duplicates.
- Input languages ("Also understand", `input_language` = `auto`): `core.INPUT_LANGUAGES` by the locale's language (`id`, `es`, `sv`), else `core.INPUT_LANGUAGES_BY_REGION` (`ID`). `none` turns it off; the tests set `none` so they do not depend on the Mac.
- Time zone: the target of `/etc/localtime`.
- Slash dates: month first only for regions in `core.MONTH_FIRST_REGIONS` (US-style).

## Language data

`ca.core.Lang(code)` builds two layers:

- Strings: `lang/<code>.json` over `lang/en_EN.json`, section by section.
- Keywords: `custom-keys.json` in the workflow data folder, over `lang/<code>-keys.json`, over `lang/en_EN-keys.json`, over the keys of each input language. A higher layer wins on conflicts; lists (stop words, time phrases) are combined. The input languages' strings go to `Lang.input_strings`, where `timecalc.translate` reads their month, weekday and unit names.

`keywords(section)` lower-cases every key and adds an accent-free spelling, and `lookup()` also tries the accent-free form, so `dias` finds `días`.

## Queries

- `clean_query` composes Unicode (Alfred delivers decomposed accents), maps `µ` to `μ`, `²` to `2`, `³` to `3`, non-breaking spaces to spaces and fraction characters to fractions (`1½` → `1 1/2`), collapses whitespace and lower-cases. `lower=False` keeps the case; `app.auto` stores that version in `ctx.typed`, and `ctx.cased(term)` finds a term's original case there (for bits and bytes).
- `split_amount` takes the leading number: a fraction (`core.FRACTION_NUMBER`: `3/4`, `1 1/2`, never part of a date like `1/2/2026`), else `core.NUMBER`: `1350.5`, `1,350.50`, `1.350,50`, `.5`, `1e6`, and spaces only as real thousands groups (`1 000 000`, never `20 20`).
- `term_splits(rest, stop_words)` yields every reading of `<from> [stop word] <to>`, splits at stop words first, then at each space. Multi-word terms (`us dollars`, `miles per hour`) and stop words that are also units (`100 cm in in`) both work. A calculator takes the first reading it can resolve.
- `parse_number` reads a number that reads only one way as such: a mark used twice groups thousands (`1.500.000`), with both marks the last one is the decimal point (`1.500,50`), and a single mark not followed by exactly three digits is a decimal point (`1,5`, `12.50`, `.250`). Only an ambiguous number (`1,500`) follows the decimal-separator setting. Fractions and exponents are read too.
- `app.selection_query` reshapes text from other apps: it drops words before the first number, and moves a currency written before the amount (`$25`, `Rp 1.500.000`, `USD 100`) behind it. `app.selection` then tries a color, the no-keyword calculators, and for 10 or 13 digits or a month name the `time` keyword, before showing a hint.

## Numbers

`format_number(value, decimals, settings)` writes results and `plain_number` writes the ⌘ Return copy.

- 14 significant digits hide float noise (`0.1 + 0.2` → `0.3`); rounding is half up.
- `decimals = -1`: every meaningful decimal, at most 8; below 1, up to 8 after the leading zeros.
- `decimals >= 0`: that many places, except that values under 0.1 keep that many significant digits and values over 1 are not padded (`150.5`, not `150.50`).
- Separators follow the number-format setting.

## Calculators

A no-keyword calculator is a module with `process(ctx, query)`. It returns `None` for "not mine, try the next one", or a list of rows, which may be a single message row. The order in `app.auto` is deliberate:

1. `units` comes before `money` (`100 pounds to kg` is a weight, `2 cups` is not the Cuban peso) and before `pxemrem` (`12 pt to l` is pints).
2. `bases` needs a target base or a `0x`, `0b` or `0o` number, and comes before `money` because `hex` is also a coin.
3. `percentage` needs a `%` after the first character.
4. `pxemrem` needs px, em, rem or pt right after the number, followed by nothing but a CSS unit or `base`.
5. `vat` (inline) needs a VAT word at the end.
6. `datastorage` comes before `money`, so `2 gb` is never a coin. It also answers `<size> at <rate>` with the transfer time.
7. `money` comes last because it has the largest vocabulary.

### Units (`ca/units.py`)

- `UNITS[category][unit]` is the size of one unit in the category's base unit. Temperature and fuel economy units (`l/100km`) are `(to_base, from_base)` function pairs. `N` sits in both `weight` and `force`.
- `build_index(lang)` maps every typed form to `(category, unit)` candidates: the unit keys, then keyword-file aliases (exact case first, so `Nm` stays newton metres and `nm` nanometres), then `FALLBACKS` (`m` minute, `d` day, `w` week, `oz` fluid ounce, `tb` tablespoon). `resolve` also drops a plural `s`.
- `_candidates` first asks `rate_unit` whether the term, in its typed case, is a data rate whose case decides bits or bytes (`Mb/s`, `MBps`, and in one case `mbps` bits, `mb/s` bytes).
- `process`: first `_compound`, which adds up several number-and-unit parts of one kind (`5'11"`, `2 h 30 min`; a bare last number takes the `FRACTION` partner) and expresses them in the first part's unit. Otherwise it takes the first split whose two terms share a category. `timespan` (or a word mapped to it) as the target of a time unit gives `duration_text` and `clock_text` rows. When both terms resolve but never share a category, it returns the error row. With no target, `_bare_rows`.
- `_bare_rows`: the units from the Default units setting of the same kind, else `DEFAULTS` (the other measurement system). `BARE_SKIP` lists typed terms that never convert alone (`k`, `t`, `st`, `pt`, `n`; `kn` only as a knot), and a fallback reading counts only when its last field says so (`12 oz` is grams and millilitres, `2 tb` nothing). At most four rows; mixed rows only for `BARE_MIXED` targets (ft, lb, st).
- `_rows` adds the mixed row from `FRACTION` when the result has a fraction whose remainder is a real part of the larger unit and the float still holds that much precision (`math.ulp`), so `1 ly to km` gets no noise row. `DISPLAY` and `TIME_WORDS` label results.

### Money (`ca/money.py`)

- `Money.resolve(term, explicit)` returns `('fiat', CODE)`, `('crypto', SYMBOL)` or `None`:
  1. digits only: `None`;
  2. fiat: ISO code, keyword file, currency name in English or the current language, then with a plural `s` dropped;
  3. crypto: keyword file, ticker, coin name, then with a plural `s` dropped. Accepted when the query has an explicit target, or when the ticker is longer than one letter and ranks within `BARE_COIN_RANK` (250).
- `Money.targets(term)` is one currency or coin, or several separated by spaces, commas or `and` (`idr eur myr`), matched greedily up to three words each (`mexican pesos eur`).
- `Money.metal(term)`: `<weight> [of] <metal>` (`10 g gold`) as troy ounces of XAU, XAG, XPT or XPD; an `oz` of metal is a troy ounce.
- `process` tries a multiplier reading first (`150k idr`), skips readings whose first term is a stop word, and converts to the target(s) or else to the base currencies. A multiplier listed under `multipliers` → `local_currency` (Indonesian `rb`, `jt`, `juta`...) followed by nothing or a stop word means the local currency (`500rb`, `1,5jt ke usd`). A bare coin whose term is also a unit (`100 km`) is skipped.
- `rows` loads only the rate kinds the conversion needs and converts through US dollars: `single = usd_per(source) / usd_per(target)`, `total = amount × single`. Subtitles carry the unit rate, the coin's name and the rate's age.

### Time (`ca/timecalc.py`)

- `translate` rewrites the query into the English vocabulary the parser knows: keyword-file words first (`ahora` → `now`, `mañana` → `+1 day`), then the language's month, weekday and unit names.
- `keyword` tries, in order: empty or `now`; `week [N [year]]` (ISO weeks, `_week_rows`); `<unit> left in <period>` (`_left_rows`); `A - B` (a difference, unless `B` is purely relative such as `3 days`); `<unit> until|since <date>`, where the date may be a start or end (`end of month`) and `workdays` counts Monday to Friday; `start of` / `end of`; a bare number as a Unix timestamp (12 digits or more means milliseconds; 4 digits is a year); anything else through `parse`.
- `parse(text, now, zone, month_first)` consumes tokens left to right: ISO and slash, dot or dash dates; `31 december 2021`; `december 31`; clock times with am/pm; `+N unit`, `N unit` and `in N unit`; `next|last|this <unit|weekday>`; weekdays; `first|last day of`; `now`, `today`, `tomorrow`, `yesterday`, `noon`, `midnight`, `ago`; `@timestamp`; a bare year; zones. It builds the moment in the source zone, applies the steps, and converts to the display zone. Any token it cannot read makes the query invalid.
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
| A unit | Add it to `UNITS` (its size in the base unit); a label in `DISPLAY`, a mixed-row partner in `FRACTION` and a no-target default in `DEFAULTS` if useful; the names people type in `lang/en_EN-keys.json`, "units"; its name in `lang/en_EN.json`, "units"; a test. Regenerate the manual's Appendix B. Prefixed units are listed one by one: lower-cased input makes `MHz` and `mHz` the same word, so a prefix table would collide. |
| A currency | Its name in `lang/en_EN.json`, "currency" (this list also decides which codes are kept from the sources); aliases in `lang/en_EN-keys.json`, "currency"; `flags/<CODE>.png` at 96 × 96. |
| A rate source | A function returning `(rates per USD, updated time)` appended to `CURRENCY_SOURCES`, or one returning a coin dictionary built with `_add_coin`, appended to `CRYPTO_SOURCES`. |
| A language | Copy both `en_EN` files to the new code and translate them; add the code to the Language and Also understand popups in `info.plist`, and to `core.INPUT_LANGUAGES` for Automatic. |
| A no-keyword calculator | A module with `process(ctx, query)`, placed deliberately in the order in `app.auto`. |
| A keyword | A Script Filter in `info.plist` connected to the clipboard output like the others, a flag in `calculate.py`, and a branch in `app.run`. |
