# Changelog

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
