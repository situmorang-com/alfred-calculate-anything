# PRD: Calculate Anything for Alfred

| | |
| --- | --- |
| Status | v5.0.2, installed and in daily use since 2026-11-15 |
| Owner | Edmund Situmorang |
| Based on | [biati-digital/alfred-calculate-anything](https://github.com/biati-digital/alfred-calculate-anything) 4.0.7 (MIT, archived in 2024) |

## Problem

Calculate Anything let you open Alfred, type `100 usd to idr`, and read the answer: no keyword, natural language. Its author archived it in 2024, and on a current Mac it no longer works:

- It runs on PHP, which macOS stopped shipping in macOS 12. Installing PHP and pointing Alfred at it was the most common failure (upstream issue #173).
- Currency conversion needs a fixer.io key and now fails with HTTP 401 (#174); a rate refresh could also hang on "Updating rates..." (#158). Crypto needs a CoinMarketCap key and showed zero values (#169).
- The `time` keyword fails on macOS 15 and later (#172).
- Long-standing conversion bugs: area units never converted (#164), UK pints and gallons were wrong (#129), `ml to oz` gave an error (#152), `84 in ft` added a "7 ft, 12 in" row (#157), and percentages ignored the decimal comma and the number format (#163, #125).

## Goals

1. Every feature of 4.0.7 works again, typed the same way.
2. Currency and crypto conversion work with no API key, account or install, and keep working when one data source disappears.
3. Typing stays instant.
4. Ordinary Alfred searches that start with a digit stay quiet: the workflow adds nothing to them.

## Non-goals

- Alfred 4, the old `ca` configuration menu and the self-updater (upstream had already removed them).
- General arithmetic such as `1+1` or `2^10`: Alfred's built-in calculator handles it.
- Bank, card or historical exchange rates. Rates are daily mid-market reference rates.
- A PHP runtime or any third-party package.

## User

The owner: a daily Alfred user on macOS 27 in Indonesia (locale en_ID, currency IDR, time zone Asia/Jakarta) who converts IDR, USD, EUR, SGD and MYR amounts, crypto, units and dates. The owner maintains the workflow with several LLM coding agents, so everything needed to work on it lives in this folder.

## Requirements

What users type for each feature, with examples, is in `docs/MANUAL.md`. These are the rules behind it.

### Currency (C)

- C1. About 170 ISO currencies, recognised by code (`idr`), symbol (`Rp`, `€`, `RM`), name (`rupiah`, `swiss francs`) or keyword-file word, in English and the configured language.
- C2. `<amount> <from> [to|in|as|=] <to>`, with or without spaces (`100usd yen`). Thousands may be grouped with commas, dots or spaces; only a number that reads two ways (`1,500`) follows the decimal-separator setting.
- C3. With no target, convert to the base-currencies setting; empty means this Mac's local currency, then USD, EUR and MYR (MYR at the owner's request). A currency is never converted to itself.
- C4. Amount multipliers: `k`, `m`, `b`, `t`, `thousand`, `million`, `billion`, `trillion`, and the Spanish and Swedish words.
- C5. Rates come from free public sources tried in order; an optional Fixer key is tried first.
- C6. A query never waits for the network. It answers from the cache, which refreshes in the background, by default every 6 hours. Each row says how old its rate is.
- C7. Rows show a flag. Return copies the formatted total, ⌘ Return the plain number, ⌥ Return the rate for one unit.

### Cryptocurrency (K)

- K1. About 1,900 coins by ticker or name. When coins share a ticker, the largest by market cap wins.
- K2. Fiat to coin, coin to fiat, coin to coin.
- K3. A currency code wins over a coin with the same ticker (`pln` is the złoty).
- K4. A bare `<amount> <coin>` converts only for the 250 largest coins with tickers longer than one letter. With an explicit target (`100 gas to usd`) any listed coin converts. Keyword-file words win over tickers (`sats` means satoshis).
- K5. Prices refresh in the background, by default every 15 minutes. An optional CoinMarketCap key is tried first.

### Units (U)

- U1. Length, area, volume, weight, speed, rotation, temperature, pressure, time, energy and power, by abbreviation, name, plural or keyword-file word.
- U2. An ambiguous abbreviation takes the reading that converts: `2 h to min` is hours, `5 h to cm` is hands, `100 ml to oz` is fluid ounces.
- U3. A second row in mixed units where it helps (`8 ft, 4 in`), and only when the remainder is a real fraction of the larger unit.
- U4. Converting between categories shows an error row.

### Data storage (D)

- D1. Bits, bytes up to yottabytes, and the binary units KiB to YiB.
- D2. IEC by default (1 MB = 1000 kB). A setting makes the decimal names binary.

### Percentages (P)

- P1. `120 + 30%`, `120 - 30%`, `15% of 50`, `40 as a % of 50`, `30 % 40`, `20% off 150`, and their words in each language.
- P2. Input follows the decimal-separator setting; output follows the number-format setting.

### CSS sizes (X)

- X1. px, em, rem and pt. With no target, all three others. The base comes from the settings or from `base 17px` in the query.

### VAT (V)

- V1. The `vat` keyword shows the tax, the amount plus tax, and the amount with the tax taken out. The rate defaults to 11%, Indonesia's PPN on most goods and services; a percentage in the query overrides the configured rate.
- V2. `400 + vat` and `400 - vat` work without the keyword, as do `ppn` and `tax`.

### Time (T)

- T1. The `time` keyword: now; Unix timestamps in seconds or milliseconds; relative expressions (`+15 days`, `3 days ago`, `next friday 3pm`, workdays); `<unit> until|since <date>`; `start of` and `end of` a year, month, week, day, named month or year; absolute dates in common formats; the difference between two dates.
- T2. Time zones. A zone after a time says where that time is (`3pm utc`); `in <zone>` shows the answer there (`now in tokyo`). Accepts abbreviations, IANA city names and UTC offsets.
- T3. Each result in every configured date format (PHP `date()` letters), then the timespan from now, then the Unix timestamp.
- T4. Ambiguous slash dates follow the date-order setting, by default this Mac's region. A reading with an impossible month flips.

### Color (L)

- L1. The `color` keyword reads hex, rgb(a), hsl(a), hwb, hsv/hsb, cmyk, lab, oklch and CSS color names, and writes those plus xyz and yuv. With no target it shows the common formats. Each row carries a swatch of the color.

### General (G)

- G1. English, Spanish and Swedish for results and typed words; English words work in every language. Personal words in `custom-keys.json` in the workflow's data folder survive updates.
- G2. Settings live in Alfred's Configure Workflow panel (see `docs/MANUAL.md`), including the four keywords.
- G3. `_caclear` deletes the cached rates.
- G4. ⌃ Return pastes a result into the app the user was in.
- G5. Text from other apps: a Universal Action, an optional hotkey and the `calc` keyword read selected text, including amounts written symbol first (`$25`, `Rp 1.500.000`, `USD 100 to IDR`), colors and Unix timestamps.

## Non-functional requirements

- N1. Runs on `/usr/bin/python3` (3.9.6 on this Mac) with the standard library only, and on newer Pythons. On a Mac without Xcode or the Command Line Tools, `/usr/bin/python3` is an installer stub, so the tools are a prerequisite.
- N2. Speed: under 50 ms per keystroke end to end (measured about 40 ms, nearly all of it interpreter start-up), and under 20 ms per query in process (asserted by the tests).
- N3. Resilience: a failing source falls through to the next. When all fail, the last downloaded rates stay in use, or a clear message shows when there are none. A failed refresh waits 20 seconds before trying again; a refresh lock older than 90 seconds is ignored.
- N4. Output is always valid Script Filter JSON. Errors go to stderr; keyword queries show an error row.
- N5. Privacy: no API key needed; requests carry a generic user agent and no personal data.
- N6. Runtime writes go only to Alfred's data and cache folders for this workflow.
- N7. The query reaches the script as an argument, never as shell text.

## Acceptance

- `tests/test_calculate.py` passes on `/usr/bin/python3` and on Homebrew's `python3`. It covers every example in the 4.0.7 README, the upstream `tests.txt`, the reported bugs above, the rate-cache states, dates against a pinned clock, and colors.
- Each feature has been checked once in Alfred itself; the latest results are in `docs/MEMORY.md`, "Status".

## Open questions

- `time` is shared with DevToys, whose row sorts first. The owner kept `time` (2026-11-15).

## Backlog

Ranked on 2026-11-16, most useful first, from the requests in the original's issue tracker (`#` numbers are issues at github.com/biati-digital/alfred-calculate-anything), what Dean Jackson's Convert, Soulver, Raycast and other Alfred converters do, and each request run against this workflow. `docs/MEMORY.md`, "What other converters do", has the sources.

Bugs:

- `2 cups` (and `2 cup`) with no target converts Cuban pesos: units answer nothing without a target, so the currency code CUP matches. Item 1 fixes it; a unit word should beat a currency code when nothing else says money.
- `90 m to h` converts metres to hands, because `h` is the hand's symbol and `m` never falls back to minutes (#81). Keep `hand` and `hands` as words and let `h` mean hour.

Features:

1. Units with no target: `100 kg`, `72 f` and `1.3 km` give nothing. Convert to the other measurement system by default (kg to lb, °F to °C, km to mi) and let the user choose their own defaults. Convert, the tinkertrain fork and alijanah's workflow all do this; Convert saves a default when you press ⌘ on a result.
2. Indonesian: an `id_ID` language with `ke` for "to"; number words and their shorthand, `ribu`/`rb`, `juta`/`jt`, `miliar`, `triliun` (`500rb`, `1,5jt idr ke usd`, `2 juta rupiah`); and the units still in daily use: `ons` (100 g), `kuintal` (100 kg), `are` (100 m²), `hektar`, and `tumbak`, `bata` and `ru` for land (about 14 m², varying by region; certificates use m²).
3. Several targets at once: `100 usd to idr eur myr` gives nothing. It is the original's most discussed request (#1).
4. Everyday units that Soulver has and this lacks: data rates and download time (`100 Mbps to MB/s`, `4 GB at 50 Mbps`; #24), fuel economy (`km/l`, `l/100km`, `mpg`), frequency (`Hz` to `GHz`), force (`N`, `kN`, `lbf`), acceleration (`m/s²`, `g`), `rpm`, troy ounces and carats, `MW` and `GW`, `ppi`. Generate the SI prefixes once instead of listing each prefixed unit.
5. Feet and inches, and fractions, as input: `5'11"`, `5 ft 11 in to cm`, `1/8 in to mm`, `1 1/2 cups to ml` (#8, #79). Output already gives `5 ft, 10.87 in`.
6. A `ca` menu inside Alfred, like Convert's `convinfo`: rates status and refresh, searchable lists of currencies and units, edit your own words, open the manual, check for a newer release.
7. Smaller requests: number bases (`255 to hex`, #121); scientific notation (`1e6 usd to idr`, #110); Indian `lakh` and `crore` (#61); `tb` as tablespoon next to a volume (#170); `fortnight`; `145 min to timespan`; gold and silver (`xau`, `xag`: fawazahmed0 has them, open.er-api does not); `$100` typed with no keyword, through `$ € £ ¥` triggers as alijanah's workflow has; Raycast's `15% tip on 80` and `15% decrease from 813`; and the dates `monday in 3 weeks`, `week 44 2026` and `days left in this month`.
8. Custom units, not only custom words, in `custom-keys.json`.
9. A clear row instead of silence when `/usr/bin/python3` is missing: the launcher can check `xcode-select -p` first.
10. Leave out the mixed-units row when floating point can't support it: `1 ly km` adds "9,460,730,472,580 km, 800.78 m".
