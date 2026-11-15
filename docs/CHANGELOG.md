# Changelog

## Unreleased

- ⌃ Return pastes a result into the app you were using.
- Convert selected text from any app: the **Calculate Anything** Universal Action, an optional hotkey, and a new `calc` keyword that reads amounts written symbol first (`$25`, `Rp 1.500.000`, `USD 100 to IDR`), colors and Unix timestamps.
- Numbers that can only be read one way are read that way: `1.500.000` is one and a half million and `1.500,50` is 1500.5, whatever the decimal-separator setting. So is a single comma or dot not followed by three digits: `1,5` is one and a half.
- A unit with no target converts to the other measurement system: `100 kg`, `72 f`, `180 cm`, `2 cups`, `12 oz`. Choose your own targets in the new **Default units** setting. Searches such as `10k`, `1st`, `12pt` and `365 days` stay untouched.
- Several parts and fractions: `5'11"`, `5 ft 11 in to cm`, `2 h 30 min to min`, `1/8 in to mm`, `1 1/2 cups to ml`, `¾ cup`.
- Indonesian: results in Bahasa Indonesia, and Indonesian words with English results through the new **Also understand** setting, which a Mac set to Indonesia turns on by itself: `500rb`, `1,5jt ke usd`, `2 juta rupiah`, `5 ons`, `1 tumbak`, `2 hektar ke m2`, `time besok`, `time 31 desember 2026`.
- Several target currencies at once: `100 usd to idr eur myr`.
- Gold, silver, platinum and palladium, per troy ounce or by weight: `1 gold to usd`, `10 g gold to idr`.
- `$`, `€`, `£` and `¥` can start a query typed without a keyword: `$100 to idr`.
- New units: data rates (`100 mbps to mb/s`), fuel economy (`km/l`, `l/100km`, `mpg`), frequency (`Hz` to `THz`, `rpm`), force (`N`, `kN`, `lbf`, `kgf`), acceleration (`m/s²`, `g`), troy ounces, carats, micrograms, centilitres, decilitres, furlongs, fathoms, ares, `MW`, `GW`, `GWh`, `TWh`, `eV`, `BTU/h`, inches of mercury, arcminutes, arcseconds, revolutions, gradians, fortnights, `ppi`, and Indonesia's `ons`, `kuintal` and `tumbak`.
- Transfer times: `4 gb at 50 mbps` gives 10 minutes, 40 seconds.
- Durations written out: `145 min to timespan` gives 2 hours, 25 minutes and 2:25:00; `100 months to years` adds 8 years, 4 months.
- Number bases: `255 to hex`, `255 to binary`, `255 to base 7`, `0xff`.
- Percentages: `15% tip on 80`, `15% increase from 813`, `15% decrease from 813`, `20% discount on 150`.
- Dates: `time monday in 3 weeks`, `time in 2 hours`, `time week 44 2026`, `time days left in this month`, `time workdays until 31 december`, `time days until end of month`.
- Money multipliers `lakh` and `crore`, and scientific notation (`1e6 idr to usd`).
- Fixed: `2 cups` converted Cuban pesos; `90 m to h` converted metres to hands (`h` is now always an hour, and hands are `hh`); `1 ly to km` added a second row of float noise.

## 5.0.2 (2026-11-15)

- Base currencies default to this Mac's currency plus USD, EUR and MYR.
- `time days until 1 january` counts to the coming 1 January, and `days since 25 december` from the last one.
- The "how long ago" row is right when the answer is shown in another time zone (`time 9am in new york`).
- A user manual: `docs/MANUAL.md`.

## 5.0.1 (2026-11-15)

- VAT defaults to 11%, Indonesia's PPN on most goods and services (it was upstream's 16%). Luxury goods pay 12%: `vat 400 12%`.
- `ppn` works as a VAT word: `400 + ppn`.

## 5.0.0 (2026-11-15)

A rebuild of [Calculate Anything 4.0.7 by Biati Digital](https://github.com/biati-digital/alfred-calculate-anything) in Python. What you type is unchanged.

### Changed

- Runs on the Python 3 that comes with Apple's developer tools. No PHP, no packages to install.
- Currency and crypto need no API keys: rates come from free public sources, with fallbacks. A Fixer or CoinMarketCap key still works and is tried first.
- Rates refresh in the background, and each result says how old its rate is.
- With no base currencies set, amounts convert to this Mac's currency plus USD and EUR. The time zone follows this Mac.
- New bundle id `com.situmorang.calculateanything`, so it can sit beside an upstream install.

### Fixed

- Currency and crypto conversion (upstream's fixer.io requests return 401, and rates could get stuck on "Updating rates...").
- The `time` keyword, which had stopped working on macOS 15.
- Area conversions such as `4500 ft2 to m2`, which said they could not be converted.
- The UK gallon was 4.405 litres; it is 4.54609. `uk pints` meant US pints.
- `100 ml to oz` gives fluid ounces instead of an error.
- `84 in ft` no longer adds a "7 ft, 12 in" row.
- Percentages follow the decimal-comma and number-format settings.
- ⌘ Return copies the right number when the number format is not `1,234.56`.
- A calorie is 4.184 J (upstream used 4184, which is a kilocalorie), 1 N weighs 0.102 kg (upstream had 9.8 kg), and 1 MeV is 1.602e-13 J.
- Results are rounded rather than cut off, and very small results no longer show as 0.

### Added

- Time zones in the `time` keyword (`3pm utc`, `now in tokyo`), `since`, and `end of month` or `week`.
- A `color` keyword with swatches.
- Thousands and millions in amounts (`150k`, `2.5 million`), and `20% off 150`.
- Cups, teaspoons, tablespoons, acres, square inches and yards, atmospheres, kilocalories, BTU, and `"` and `'` for inches and feet.
- A second row in mixed units for more units, configurable keywords, and project docs for coding agents (`AGENTS.md`, `docs/`).

### Removed

- The Alfred 4 `ca` configuration menu and the self-updater, both already removed upstream.
