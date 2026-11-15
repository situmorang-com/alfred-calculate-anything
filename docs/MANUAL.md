# Calculate Anything: user manual

For version 5.1 on Alfred 5 with the Powerpack. The example results were taken on 15 and 16 November 2026; exchange rates and prices change every day.

## Contents

1. [Getting started](#1-getting-started)
2. [Using results](#2-using-results)
3. [Currency](#3-currency)
4. [Cryptocurrency](#4-cryptocurrency)
5. [Units](#5-units)
6. [Data storage](#6-data-storage)
7. [Percentages](#7-percentages)
8. [CSS sizes](#8-css-sizes)
9. [Number bases](#9-number-bases)
10. [VAT](#10-vat)
11. [Dates and times](#11-dates-and-times)
12. [Colors](#12-colors)
13. [Languages and your own words](#13-languages-and-your-own-words)
14. [Settings](#14-settings)
15. [Maintenance](#15-maintenance)
16. [Troubleshooting](#16-troubleshooting)
17. [Privacy](#17-privacy)

Appendices: [A. Currencies](#appendix-a-currencies) · [B. Units](#appendix-b-units) · [C. Time zone names](#appendix-c-time-zone-names) · [D. Date format letters](#appendix-d-date-format-letters)

## 1. Getting started

**Install.** Download `Calculate.Anything.alfredworkflow` from the [latest release](https://github.com/situmorang-com/alfred-calculate-anything/releases/latest) and double-click it. The workflow runs on the Python 3 in Apple's command line developer tools: if macOS offers to install them the first time, accept, or run `xcode-select --install`.

**Use.** Open Alfred and start typing a number. A result appears as soon as the query makes sense; no keyword needed.

```
100 usd to idr      →  1,822,936.37 IDR
100 km to miles     →  62.13711922 mi
120 + 30%           →  156
```

Four keywords cover the rest:

| Keyword | For | Example |
| --- | --- | --- |
| `time` | dates, times and time zones | `time +15 days` |
| `vat` | a VAT breakdown | `vat 400` |
| `color` | color formats | `color #ff6600` |
| `calc` | text that doesn't start with a number, and text sent from other apps | `calc Rp 1.500.000`, `calc transfer 1 tb at 100 mbps` |
| `_caclear` | deleting the cached exchange rates | `_caclear` |

A query without a keyword must start with a number (a leading `.` or `-` works too: `.5 km to m`, `-25f to c`) or with `$`, `€`, `£` or `¥` (`$100 to idr`), and be at least three characters long. Everything else is left to Alfred, so ordinary searches such as `1password` are unaffected.

The first currency or crypto query after installing shows **Updating rates...** for a moment while the rates download.

## 2. Using results

| Key | Copies |
| --- | --- |
| Return | the result as shown, for example `1,822,936.37` |
| ⌘ Return | the number without formatting, `1822936.37` (currency, crypto, units, data storage, percentages, VAT) |
| ⌥ Return | currency and crypto: the rate for one unit, `18229.363747`; units and data storage: the result with its unit, `62.13711922 mi` |
| ⌃ Return | the result as shown, and pastes it into the app you were using |
| ⌘C | the selected row's value |
| ⌘L | the result in Large Type |
| ⌘1 to ⌘9 | the first to ninth row (an Alfred shortcut) |

Where a result has no ⌘ or ⌥ variant (CSS sizes, dates, colors), those keys copy what the row shows.

### Converting text from other apps

Select an amount anywhere, such as `$25`, `Rp 1.500.000` or `USD 100 to IDR` in a web page or an email, open Alfred's Universal Actions for the selection (⌥⌘\\ by default), and choose **Calculate Anything**. Alfred opens the `calc` keyword with the text, so you can still add to it, for example a target currency.

- To skip the actions list, give the workflow's **Hotkey** a key: in Alfred Preferences, open the workflow and double-click the hotkey object. It sends the selected text the same way.
- `calc` reads amounts written symbol first (`$25`, `RM 50`, `US$ 1,234.50`), ignores words before the amount (`costs about $25.`), converts a color (`#ff6600`), and shows the date for a Unix timestamp (`1577836800`).
- A number alone (`1.500.000`) asks for a unit: type it after the number, as in `calc 1.500.000 idr`.

## 3. Currency

### Typing a conversion

`<amount> <currency> [to | in | as | =] <currency>`, with or without spaces, in any case.

| Query | Result |
| --- | --- |
| `100 usd to idr` | 1,822,936.37 IDR |
| `100usd idr` | 1,822,936.37 IDR |
| `100€ to $` | 110.38 USD |
| `100 euros in dollars` | 110.38 USD |
| `45 rm to usd` | 11.01 USD |
| `100 pounds to euros` | 119.78 EUR |
| `150k idr to usd` | 8.23 USD |
| `2.5 million yen to eur` | 14,175.58 EUR |
| `1 500 000 idr to usd` | 82.28 USD |
| `$100 to idr` | 1,822,936.37 IDR |
| `100 usd to idr eur myr` | 1,822,936.37 IDR · 90.60 EUR · 408.58 MYR |

`$`, `€`, `£` and `¥` can come first without a keyword: `$100 to idr`, `€50`. For any other symbol written first (`Rp 150.000`, `RM 50`), use `calc`.

### Several targets

List the targets after the amount, with spaces, commas or `and`: `100 usd to idr eur myr` and `100 usd to idr, eur and myr` both give one row per currency.

### No target: base currencies

Leave out the target and the amount converts to your base currencies, one row each:

| Query | Result |
| --- | --- |
| `100 sgd` | 1,415,861.92 IDR · 77.67 USD · 70.37 EUR · 317.34 MYR |

Set them in **Base currencies**, for example `IDR, SGD, USD`. Left empty, they are this Mac's local currency (from the region in System Settings) followed by USD, EUR and MYR. A currency is never converted to itself.

### Naming a currency

- **Code:** `idr`, `usd`, `myr`, for about 175 currencies ([Appendix A](#appendix-a-currencies)).
- **Symbol:** `Rp`, `$`, `€`, `£`, `¥`, `RM`, `S$`, `฿`, `₱`, `₩`, `₹`, `₫`, `HK$`, `A$`, `R$` and more ([Appendix A](#appendix-a-currencies)).
- **Name:** `rupiah`, `ringgit`, `dollars`, `euros`, `pounds`, `yen`, `yuan`, `baht`, `won`, `rupees`, `swiss francs`, `singapore dollars`, and each currency's full English name (`indonesian rupiah`, `malaysian ringgit`). Plurals work.

`$` and `dollars` mean US dollars. `pounds` means pounds sterling unless the other side is a weight: `100 pounds to kg` gives kilograms.

### Amounts

- Separators: `1,350.50`, `1 350.50`, `1.500.000`, `1.350,50`, `1,5` and `.5` all work. Only a number that reads two ways, such as `1,500`, depends on **Input decimal separator**: Dot reads it as 1500, Comma as 1.5. A single comma or dot not followed by exactly three digits is always the decimal mark, so `1,5` is one and a half.
- Multipliers: `k`, `thousand`, `m`, `mn`, `mio`, `million`, `b`, `bn`, `billion`, `t`, `tn`, `trillion`, `lakh`, `crore` (`150k`, `2.5m`, `3 billion`, `1 crore inr`). They apply to money only, so `5 m to ft` is five metres. `m` is always a million; for Indonesian billions write `miliar`.
- Scientific notation: `1e6 idr to usd` gives 54.86 USD.
- Indonesian amounts, when Indonesian is understood ([section 13](#13-languages-and-your-own-words)): `500rb`, `1,5jt ke usd`, `2 juta rupiah`, `1 miliar idr to usd`. A shorthand with no currency after it, such as `500rb`, is in this Mac's local currency.
- Results show 2 decimals (**Currency decimals**). Very small results keep their significant digits instead of showing 0.00: `1 idr to usd` gives 0.000055 USD.

### Gold and silver

`xau`, `xag`, `xpt` and `xpd`, or `gold`, `silver`, `platinum` and `palladium`, are priced per troy ounce. Put a weight in front to price that much metal; an ounce of gold is a troy ounce.

| Query | Result |
| --- | --- |
| `1 gold to usd` | 3,874.43 USD |
| `10 g gold to idr` | 22,707,580.72 IDR |
| `1 oz gold to idr` | 70,628,471.00 IDR |
| `1 kg silver to usd` | 1,570.08 USD |

These are spot prices from the same sources as the currencies, not what a shop charges.

### Where the rates come from

Rates are daily mid-market reference rates, not what a bank or card charges. They come from free public services, tried in this order: [exchangerate-api.com](https://www.exchangerate-api.com), the [fawazahmed0 currency API](https://github.com/fawazahmed0/exchange-api), [frankfurter.dev](https://frankfurter.dev) and the [European Central Bank](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html).

- They refresh in the background every 6 hours (**Refresh currency rates every**). A query never waits for the download.
- Each row's subtitle shows the rate and its age: `1 USD = 18,229.363747 IDR · updated 2h ago`.
- Offline, the last downloaded rates keep working.
- A [fixer.io](https://fixer.io) key is optional. With one in **Fixer API key**, Fixer is asked first.

## 4. Cryptocurrency

| Query | Result |
| --- | --- |
| `1 btc` | one row per base currency |
| `1 btc to usd` | 65,383.60 USD |
| `0.5 eth to idr` | 16,664,993.97 IDR |
| `100 usd to btc` | 0.0015294355 BTC |
| `1000 sats to usd` | 0.65 USD |
| `100 gas to usd` | 95.81 USD |

- About 1,900 coins, by ticker (`btc`, `eth`, `sol`) or name (`bitcoin`, `ether`, `dogecoin`, `solana`, `ripple`, `cardano`, `tether`). `sat`, `sats` and `satoshi` are hundred-millionths of a bitcoin.
- A currency code wins over a coin with the same ticker: `pln` is the Polish złoty.
- Hundreds of tickers are ordinary words, so an amount with no target converts only for the 250 largest coins. For any other coin, name a target: `100 gas` shows nothing, `100 gas to usd` converts.
- Prices come from [CoinPaprika](https://coinpaprika.com), then [CoinGecko](https://www.coingecko.com), then [CoinLore](https://www.coinlore.net), and refresh every 15 minutes (**Refresh crypto prices every**). The subtitle names the coin and shows the price's age.
- Amounts in a coin show every meaningful decimal (**Cryptocurrency decimals**, default -1).
- A [CoinMarketCap](https://coinmarketcap.com/api/) key is optional and, if set, asked first.

## 5. Units

`<amount> <unit> [to | in | as | =] <unit>`

| Query | Result |
| --- | --- |
| `100 km to miles` | 62.13711922 mi · 62 mi, 723.99 ft |
| `72 f to c` | 22.22 °C |
| `100 kg to lb` | 220.46226218 lb · 220 lb, 7.4 oz |
| `100 ml to oz` | 3.38140227 fl oz |
| `500 sqft to m2` | 46.45152 m² |
| `60 mph to kmh` | 96.56064 km/h |
| `1 cup to ml` | 236.5882365 ml |
| `1 atm to psi` | 14.69594878 psi |
| `1 kwh to j` | 3,600,000 J |
| `2 h to min` | 120 minutes |
| `15 km/l to mpg` | 35.2821875 mpg |
| `100 mbps to mb/s` | 12.5 MB/s |
| `1 ghz to mhz` | 1,000 MHz |
| `3000 rpm to rad/s` | 314.15926536 rad/s |
| `100 kn to lbf` | 22,480.89430997 lbf |
| `9.81 m/s2 to g` | 1.00034160 g |
| `1 ozt to g` | 31.1034768 g |
| `5 ct to g` | 1 g |

There are seventeen kinds: length, area, volume, weight, speed, angles, temperature, pressure, time, energy, power, frequency and rotation speed, force, acceleration, fuel economy, data rates and screen density. Write a unit as an abbreviation, a name or a plural; [Appendix B](#appendix-b-units) lists every accepted spelling.

### No target

Type a unit without a target and it converts to the other measurement system:

| Query | Result |
| --- | --- |
| `100 kg` | 220.46226218 lb · 220 lb, 7.4 oz |
| `72 f` | 22.22 °C |
| `180 cm` | 70.86614173 in · 5.90551181 ft · 5 ft, 10.87 in |
| `100 km` | 62.13711922 mi |
| `2 cups` | 473.176473 ml |
| `12 oz` | 340.1942775 g · 354.88235475 ml |
| `100 mbps` | 12.5 MB/s |

- To choose your own targets, list them in **Default units**, for example `kg, km, °C`. A kind of unit you leave out keeps the other system, and so does a unit you typed that is already your choice (`100 kg` with `kg` listed gives pounds).
- Time, angles, frequencies and small metric units (`mg`) have no default, so `365 days` stays an ordinary search unless you list a time unit.
- A few abbreviations are left alone when typed with no target because they usually mean something else: `k` (`10k`, ten thousand), `t`, `st` (`1st`), `pt` (`12pt` is a font size) and `n`. Their full names work: `300 kelvin`, `1 ton`, `2 pints`.

### Several parts and fractions

- Parts of one kind are added up: `5'11"`, `5' 11"`, `5 ft 11 in` and `5ft11in` all mean 71 inches, and `5'11"` gives 1.8034 m · 180.34 cm. More: `2 h 30 min to min` gives 150 minutes, `5 lb 3 oz to kg` gives 2.35301042 kg. A last number without a unit takes the next smaller one: `5'11` is 5 ft 11 in.
- Fractions work as amounts: `1/8 in to mm` gives 3.175 mm, `1 1/2 cups to ml` 354.88235475 ml, and `¾ cup to ml` 177.44117738 ml.

### Durations

Convert time to `timespan` (or `duration`) to have it written out: `145 min to timespan` gives 2 hours, 25 minutes · 2:25:00. Converting to a larger unit adds a mixed row too: `100 months to years` gives 8.33333333 years · 8 years, 4 months.

### Bits and bytes

`mbps` is megabits per second, the speed internet plans quote, and `mb/s` megabytes per second, as `mb` is a megabyte elsewhere. With capitals, the letter decides: `Mb/s` and `Mbps` are megabits, `MB/s` and `MBps` megabytes. `100 mbps to mb/s` gives 12.5 MB/s.

### Good to know

- **Second row.** Where it helps, a second row gives the result in mixed units (`8 ft, 4 in`, `1 hour, 40 minutes`).
- **Ambiguous abbreviations** take the meaning that fits the other side: `m` is a metre or a minute (`90 m to h`); `oz` an ounce of weight or a fluid ounce (`100 ml to oz`); `pt` a pint (`12 pt to l`) or a CSS point (`12pt to px`); `tb` a terabyte or a tablespoon (`1 tb to tsp`); `kn` a kilonewton or a knot; `g` a gram or standard gravity (`9.81 m/s2 to g`). `h` is always an hour; hands, for horses, are `hh`.
- **`in`** works both as a linking word and as inches: `100 cm in in` gives 39.37007874 in.
- **Temperatures** show 2 decimals.
- **Months and years** are averages here: a year is 365 days and a month a twelfth of that, 30.42 days. For calendar arithmetic, use `time`.
- **Indonesian units:** `ons` (100 g), `kuintal` (100 kg), `are` (100 m²) and `tumbak` work in any language; with Indonesian understood, so do `hektar`, `bata` and `ru`. A tumbak (bata, ru) is taken as 14 m², the most common value; it varies by region, and land certificates use m².
- Converting between kinds, such as `100 km to kg`, shows an error row.

## 6. Data storage

| Query | Result |
| --- | --- |
| `2 gb to mb` | 2,000 MB |
| `100 gigabytes in megabytes` | 100,000 MB |
| `400 mib to kib` | 409,600 KiB |
| `1 gib to mb` | 1,073.741824 MB |
| `8 bit to b` | 1 B |

Units are `b` (byte), `kb` to `yb`, `kib` to `yib`, and `bit`, or their names (`megabytes`, `megas`, `gibibytes`); [Appendix B](#data-storage) lists them all. Decimal names follow the IEC standard, 1 MB = 1000 kB, while 1 MiB = 1024 KiB. Turn on **Data storage: Binary mode** to make 1 MB = 1024 kB.

### Transfer time

`<size> at <speed>` gives how long a download or copy takes; `over` and `@` work too.

| Query | Result |
| --- | --- |
| `4 gb at 50 mbps` | 10 minutes, 40 seconds · 0:10:40 |
| `1 tb over 100 mbps` | 22 hours, 13 minutes, 20 seconds · 22:13:20 |
| `700 mb @ 1 mb/s` | 11 minutes, 40 seconds · 0:11:40 |

Speeds follow [Bits and bytes](#bits-and-bytes).

## 7. Percentages

| Query | Result | Second row |
| --- | --- | --- |
| `120 + 30%` | 156 | 36, the 30% added |
| `120 - 30%` | 84 | 36, the 30% taken off |
| `15% of 50` | 7.5 | |
| `20% off 150` | 120 | 30, the discount |
| `40 as a % of 50` | 40 is 80% of 50 | the increase from 40 to 50 (25%) and the decrease from 50 to 40 (20%) |
| `30 % 40` | 30 is 75% of 40 | the increase (33.33333333%) and the decrease (25%) |
| `15% tip on 80` | 12 | 92, the bill with the tip |
| `15% increase from 813` | 934.95 | 121.95, the increase |
| `15% decrease from 813` | 691.05 | 121.95, the decrease |

Words work too: `plus`, `minus`, `percent`, `pct`, `as a percent of`, `as a percentage of`, `is what % of`, `is what percent of`, `discount` (like `off`), `tip for`, `increase on`, `decrease on`. With the comma decimal settings, `10,5 + 5%` gives 11,025.

## 8. CSS sizes

| Query | Result |
| --- | --- |
| `12px` | 0.75em · 0.75rem · 9pt |
| `2rem to pt` | 24pt |
| `12pt to px` | 16px |
| `12px in em base 17px` | 0.70588em |

The units are `px`, `em`, `rem` and `pt`. The root size is 16px (**Base pixels**); add `base 17px` to a query to use another. em and rem both convert from the root size.

## 9. Number bases

| Query | Result |
| --- | --- |
| `255 to hex` | FF |
| `255 to binary` | 11111111 |
| `255 to octal` | 377 |
| `255 to base 7` | 513 |
| `0xff` | 255 · 11111111 · 377 |
| `0b1010 to decimal` | 10 |

- Targets: `hex` or `hexadecimal`, `binary` or `bin`, `octal` or `oct`, `decimal` or `dec`, and `base 2` to `base 36`.
- A number written with `0x`, `0b` or `0o` needs no target: it shows the other three bases.
- ⌘ Return copies the result with its prefix, `0xFF`.
- A plain number with no target, such as `255`, is left to Alfred.

## 10. VAT

The rate is 11% unless you change it: Indonesia's PPN on most goods and services. Luxury goods pay 12%. Set your own rate in **VAT percentage**.

| Query | Result |
| --- | --- |
| `vat 400` (or `vat of 400`) | VAT of 400 = 44 · 400 plus VAT = 444 · 400 minus VAT = 360.36 |
| `vat 400 12%` | the same at 12%, for this query only |
| `400 + vat` | 444 |
| `400 - vat` | 360.36 |

- "Minus VAT" is the price before tax, for when 400 already includes it (400 ÷ 1.11), not 400 less 11%.
- Without the keyword, `ppn`, `tax`, `gst` and `sales tax` work like `vat`, and `plus` and `minus` like `+` and `-`: `400 + ppn`, `400 minus tax`.

## 11. Dates and times

Type `time` and an expression. Each answer is listed in every date format you have set (**Date formats**), then how far away it is, then its Unix timestamp. Return copies a row.

| Kind | Examples |
| --- | --- |
| Now | `time` |
| Unix timestamps | `time 1577836800`, `time 1577836800000` (milliseconds), `time @1577836800` |
| Relative | `time +15 days`, `time 3 days ago`, `time now plus 3 days`, `time now minus 2 weeks`, `time tomorrow`, `time yesterday 9am`, `time next friday 3pm`, `time last monday`, `time next month`, `time +1 week 2 days` |
| Working days | `time today + 3 workdays` (also `business days`, `working days`, `wd`) |
| Counting | `time days until 31 december`, `time weeks until 1 january`, `time hours since yesterday`, `time days until end of month`, `time workdays until 31 december`, in seconds, minutes, hours, days, workdays, weeks, months or years |
| Time left | `time days left in this month`, `time workdays left in this month`, `time hours left in this day`, `time weeks left in the year`: whole days after today, up to the end of the day, week, month or year |
| From now | `time in 3 days`, `time in 2 hours`, `time monday in 3 weeks` (the coming Monday, then three weeks on) |
| Weeks | `time week` (this week), `time week 44`, `time week 44 2026`: the Monday-to-Sunday range of an ISO week, then its Monday |
| Start and end | `time start of year`, `time end of 2021`, `time end of month`, `time start of next month`, `time end of week`, `time start of march`, `time first day of next month` |
| A date | `time 31 December, 2021 18:00:00`, `time 31/12/2021 18:00`, `time 2021-12-31 18:00`, `time december 31 2021 6pm`, `time 31st of december 2021 at 6:00 pm`, `time 2021`, `time noon` |
| Between two dates | `time 25 december 2021 - 31 december 2021` gives 6 days; `time 1 january 2020 - 15 march 2021` gives 1 year, 2 months, 2 weeks, and 439 days |

- **No year** means this year, except when counting: `days until 1 january` counts to the coming 1 January, and `days since 25 december` from the last one.
- **Weeks** run Monday to Sunday.
- **Slash dates** such as `01/02/2026` put the day first unless your Mac's region writes the month first, as in the US. **Dates like 01/02/2026** overrides that. A date that can only be read one way, such as `12/31/2021`, is read that way. Dashes and dots (`31-12-2021`, `31.12.2021`) always put the day first.

### Time zones

| Query | Meaning |
| --- | --- |
| `time 3pm utc` | 3 pm UTC, shown in your time |
| `time 10:00 est` | 10 am in New York, shown in your time |
| `time 09:00 +09:00` | 9 am at UTC+9, shown in your time |
| `time 2021-12-31T18:00:00Z` | an ISO 8601 time in UTC, shown in your time |
| `time now in tokyo` or `time tokyo` | the time in Tokyo now |
| `time 9am in new york` | 9 am your time, shown in New York |

A zone can be an abbreviation (`utc`, `gmt`, `wib`, `wita`, `wit`, `sgt`, `myt`, `jst`, `est`, `pst`, `cet` and more), a city or country from [Appendix C](#appendix-c-time-zone-names), any city in the world time zone database (`kuala lumpur`, `london`, `sydney`), or an offset (`+07:00`, `utc+7`, `gmt-5`). Your own zone is **Time zone**, or this Mac's when that is Automatic.

### Date formats

**Date formats** takes PHP `date()` letters; separate several formats with `|`, as in `j F, Y, g:i:s a | Y-m-d H:i:s`. [Appendix D](#appendix-d-date-format-letters) lists the letters. A backslash prints the next letter as it is: `\a\t` prints "at".

## 12. Colors

Type `color`, a color, and optionally the format to convert to.

| Query | Result |
| --- | --- |
| `color #ff6600` | #ff6600 · rgb(255, 102, 0) · hsl(24, 100%, 50%) · hwb(24 0% 0%) · hsv(24, 100%, 100%) · cmyk(0%, 60%, 100%, 0%) · lab(62.31% 55 71.33) · oklch(69.58% 0.2043 43.49) |
| `color #ff6600 to hsl` | hsl(24, 100%, 50%) |
| `color tomato to hex` | #ff6347 |
| `color rgb(255 102 0 / 50%) to hex` | #ff660080 |
| `color 255, 102, 0 to hex` | #ff6600 |
| `color hsl(24, 100%, 50%) to oklch` | oklch(69.58% 0.2043 43.49) |

- **Reads** hex (`#f60`, `#ff6600`, `#ff660080`, with or without `#`), `rgb()` and `rgba()` (commas or spaces, `/` for alpha, percentages), `hsl()` and `hsla()`, `hwb()`, `hsv()` and `hsb()`, `cmyk()`, `lab()`, `oklch()`, three bare numbers, and the 148 CSS color names.
- **Writes** hex, rgb, hsl, hwb, hsv, cmyk, lab and oklch, plus `xyz` and `yuv` when you ask for them by name.
- Each row shows a swatch of the color.

## 13. Languages and your own words

**Language** (English, Indonesian, Spanish or Swedish) sets the language of the results and adds that language's words to what you can type. English words work whatever the language.

**Also understand** adds the words of one more language without changing the results' language. On Automatic it follows this Mac: a Mac whose language or region is Indonesian understands Indonesian, and one whose language is Spanish or Swedish understands that language.

| Language | Examples |
| --- | --- |
| Indonesian | `500rb`, `1,5jt ke usd`, `2 juta rupiah`, `100 usd ke idr`, `10 gram emas ke idr`, `5 ons`, `1 tumbak`, `2 hektar ke m2`, `5 km ke m`, `15% dari 50`, `20% diskon 150`, `400 + ppn`, `time besok`, `time 3 hari lalu`, `time 31 desember 2026`, `time hari sampai 31 desember`, `time minggu depan` |
| Spanish | `100 euros a dolares`, `10 días a horas`, `120 más 30%`, `400 mas iva`, `time ahora más 3 días`, `time inicio de 2020`, `time dias hasta 31 diciembre` |
| Swedish | `5 kilometer till meter`, `100 kr till usd`, `400 plus moms`, `time början av 2021` |

In Indonesian, `minggu` is a week; Sunday is `hari minggu`.

### Your own words

Add words in a file named `custom-keys.json` in the workflow's data folder, `~/Library/Application Support/Alfred/Workflow Data/com.situmorang.calculateanything/`. It survives updates. For example, a few Malay words:

```json
{
  "multipliers": { "ribu": 1000, "juta": 1000000, "bilion": 1000000000 },
  "currency": { "stop_words": ["kepada"] },
  "units": { "stop_words": ["kepada"] }
}
```

Now `1.5 bilion idr kepada myr` and `10 km kepada m` work.

| Section | A key is | Its value is |
| --- | --- | --- |
| `currency` | a word for a currency | its code: `"bucks": "USD"` |
| `crypto_currency` | a word for a coin | its ticker: `"sats": "SAT"` |
| `units` | a word for a unit | the unit as written in Appendix B: `"hakunamatata": "year"` |
| `datastorage` | a word for a data unit | `b`, `kb` to `yib`, or `bit` |
| `percentage`, `vat`, `time` | a word | what it stands for: `"plus": "+"` |
| `multipliers` | a word or suffix | a number: `"bilion": 1000000000` |

Each section can also take `"stop_words"`, the linking words between the two sides (`to`, `in`, `ke`); yours are added to the built-in ones. Where your words and the built-in ones differ, yours win. Changes apply from the next query.

## 14. Settings

Open Alfred Preferences, choose Workflows, select Calculate Anything, and click **Configure Workflow**.

| Setting | Default | What it does |
| --- | --- | --- |
| Language | English | Language of the results and of the words you can type. English words always work. |
| Also understand | Automatic | One more language's words you can type, such as Indonesian `500rb` and `ke`. Automatic follows this Mac's language and region. |
| Base currencies | empty | Targets for an amount with no target, separated by commas. Empty means this Mac's currency, then USD, EUR and MYR. |
| Default units | empty | Targets for a unit with no target, such as `kg, km, °C`. Kinds left out convert to the other measurement system. |
| Currency decimals | 2 | Decimals for currency amounts. -1 shows every decimal. |
| Cryptocurrency decimals | -1 | Decimals for amounts in a coin. |
| Input decimal separator | Dot | Whether you type `23.51` or `23,51`. |
| Number output format | 1,234.56 | Or `1 234,56`, or `1.234,56`. |
| Time zone | Automatic | The zone for the `time` keyword. |
| Date formats | `j F, Y, g:i:s a` | How `time` writes dates ([Appendix D](#appendix-d-date-format-letters)). |
| Dates like 01/02/2026 | Automatic | Day first or month first for slash dates. |
| VAT percentage | 11% | The rate for `vat` and `+ vat`. |
| Base pixels | 16px | The root font size for em and rem. |
| Data storage: Binary mode | off | On: 1 MB = 1024 kB. |
| Refresh currency rates every | 6 hours | How often rates download. |
| Refresh crypto prices every | 0.25 hours | How often coin prices download. |
| Time keyword, VAT keyword, Color keyword, Calc keyword | `time`, `vat`, `color`, `calc` | Rename a keyword if another workflow uses it. |
| Fixer API key | empty | Optional; asked first for exchange rates. |
| CoinMarketCap API key | empty | Optional; asked first for coin prices. |

## 15. Maintenance

- **Refresh rates now:** type `_caclear`, press Return, then run any conversion. The rates download again.
- **Where data lives:** `~/Library/Application Support/Alfred/Workflow Data/com.situmorang.calculateanything/` holds the cached rates and prices, the color swatches and your `custom-keys.json`.
- **Update:** download the newest release and double-click it; Alfred offers to replace the old version and keeps your settings. If you installed with `git clone`, run `git pull` in the workflow's folder.
- **Remove:** delete the workflow in Alfred Preferences, and the data folder above if you like.

## 16. Troubleshooting

**Nothing appears.** Start with a number (or `$`, `€`, `£`, `¥`) and type at least three characters. Check the spelling of the units or currencies. For a coin outside the 250 largest, name a target (`100 gas to usd`). Check that the workflow is enabled in Alfred Preferences.

**macOS asks to install command line developer tools.** Accept. The workflow runs on the Python 3 they include.

**"Updating rates..." stays, or "Unable to get currencies data" appears.** The rates could not be downloaded. Check the internet connection and try again in a minute. Rates downloaded earlier, if any, keep working.

**A rate looks out of date.** The subtitle shows its age. The free sources publish once a day; lower **Refresh currency rates every** to check more often, or type `_caclear` to download now.

**⌃ Return copies but doesn't paste.** Alfred needs permission to paste: in System Settings, open Privacy & Security, then Accessibility, and turn Alfred on.

**Every result appears twice.** The original Calculate Anything is still installed. Disable it in Alfred Preferences.

**`time` results are not in the first row.** Another workflow also uses the `time` keyword. Pick this workflow's row (⌘2 for the second), or rename **Time keyword**.

**A date is read the wrong way round.** Set **Dates like 01/02/2026** to day first or month first.

**Decimals typed with a comma give odd results.** Set **Input decimal separator** to Comma, and **Number output format** to `1.234,56` if you also want commas in results.

**VAT is wrong for your country.** Set **VAT percentage**.

**A word isn't recognised.** Add it to `custom-keys.json` ([Your own words](#your-own-words)).

**A unit typed alone converts to the wrong unit.** List the units you want in **Default units** ([No target](#no-target)).

**`5 h` used to mean hands.** `h` is always an hour now; type `hh` or `hands`.

**Anything else.** In Alfred Preferences, open the workflow and click the bug icon to open the debugger, type the query again, and read what the workflow printed.

## 17. Privacy

What you type stays on your Mac. The only network requests are the downloads of rates and prices described above: plain requests to those public services that carry no query, account or personal data. If you add one of the optional API keys, it is sent only to its own service.

## Appendix A: Currencies

Every currency the workflow knows, with its English name and the other ways to type it. The full English name works too (`indonesian rupiah`), as do plurals. Gold, silver, platinum and palladium are priced per troy ounce. Words in Indonesian, Spanish and Swedish are in `lang/id_ID-keys.json`, `lang/es_ES-keys.json` and `lang/sv_SE-keys.json`.

| Code | Name | Also typed as |
| --- | --- | --- |
| `aed` | United Arab Emirates dirham | `dirham`, `dirhams`, `emirati dirham` |
| `afn` | Afghan afghani |  |
| `all` | Albanian lek |  |
| `amd` | Armenian dram |  |
| `ang` | Netherlands Antillean guilder | `ƒ` |
| `aoa` | Angolan kwanza |  |
| `ars` | Argentine peso | `argentinian`, `argentinian peso`, `argentinian pesos` |
| `aud` | Australian dollar | `a$`, `au$`, `aussie dollars`, `australian dollar`, `australian dollars` |
| `awg` | Aruban florin |  |
| `azn` | Azerbaijani manat |  |
| `bam` | Bosnia and Herzegovina convertible mark |  |
| `bbd` | Barbados dollar |  |
| `bdt` | Bangladeshi taka |  |
| `bgn` | Bulgarian lev | `лв` |
| `bhd` | Bahraini dinar |  |
| `bif` | Burundian franc |  |
| `bmd` | Bermudian dollar |  |
| `bnd` | Brunei dollar |  |
| `bob` | Boliviano |  |
| `brl` | Brazilian real | `R$`, `reais`, `brazilian real`, `brazilian reais` |
| `bsd` | Bahamian dollar |  |
| `btn` | Bhutanese ngultrum |  |
| `bwp` | Botswana pula |  |
| `byn` | New Belarusian ruble |  |
| `byr` | Belarusian ruble |  |
| `bzd` | Belize dollar |  |
| `cad` | Canadian dollar | `ca$`, `cad$`, `canadian`, `canadian dollar`, `canadian dollars` |
| `cdf` | Congolese franc |  |
| `chf` | Swiss franc | `franc`, `francs`, `swiss franc`, `swiss francs` |
| `clf` | Unidad de Fomento |  |
| `clp` | Chilean peso | `chilean peso`, `chilean pesos` |
| `cnh` | Chinese yuan (offshore) |  |
| `cny` | Renminbi / Chinese yuan | `元`, `C¥`, `RMB`, `yuan`, `renminbi`, `chinese yuan` |
| `cop` | Colombian peso | `colombian peso`, `colombian pesos` |
| `crc` | Costa Rican colon | `₡` |
| `cuc` | Cuban convertible peso |  |
| `cup` | Cuban peso |  |
| `cve` | Cape Verde escudo |  |
| `czk` | Czech koruna | `Kč` |
| `djf` | Djiboutian franc |  |
| `dkk` | Danish krone | `kr`, `danish krone`, `danish kroner` |
| `dop` | Dominican peso | `RD$` |
| `dzd` | Algerian dinar |  |
| `egp` | Egyptian pound | `egyptian pound`, `egyptian pounds` |
| `ern` | Eritrean nakfa |  |
| `etb` | Ethiopian birr |  |
| `eur` | Euro | `€`, `euro`, `eurs`, `euros` |
| `fjd` | Fiji dollar |  |
| `fkp` | Falkland Islands pound |  |
| `fok` | Faroese króna |  |
| `gbp` | Pound sterling | `£`, `quid`, `pound`, `pounds`, `sterling`, `british pound`, `british pounds`, `pound sterling`, `pounds sterling` |
| `gel` | Georgian lari |  |
| `ggp` | Guernsey pound |  |
| `ghs` | Ghanaian cedi | `¢` |
| `gip` | Gibraltar pound |  |
| `gmd` | Gambian dalasi |  |
| `gnf` | Guinean franc |  |
| `gtq` | Guatemalan quetzal | `Q` |
| `gyd` | Guyanese dollar |  |
| `hkd` | Hong Kong dollar | `hk$`, `hong kong dollar`, `hong kong dollars` |
| `hnl` | Honduran lempira | `L` |
| `hrk` | Croatian kuna |  |
| `htg` | Haitian gourde |  |
| `huf` | Hungarian forint | `Ft` |
| `idr` | Indonesian rupiah | `Rp`, `rupiah`, `rupiahs`, `indonesian rupiah` |
| `ils` | Israeli new shekel | `₪`, `shekel`, `shekels` |
| `imp` | Manx pound |  |
| `inr` | Indian rupee | `₹`, `rs`, `rupe`, `rupee`, `rupees`, `indian rupee`, `indian rupees` |
| `iqd` | Iraqi dinar |  |
| `irr` | Iranian rial |  |
| `isk` | Icelandic króna |  |
| `jep` | Jersey pound |  |
| `jmd` | Jamaican dollar | `J$` |
| `jod` | Jordanian dinar |  |
| `jpy` | Japanese yen | `¥`, `円`, `yen`, `yens`, `japanese yen` |
| `kes` | Kenyan shilling |  |
| `kgs` | Kyrgyzstani som |  |
| `khr` | Cambodian riel | `៛` |
| `kid` | Kiribati dollar |  |
| `kmf` | Comoro franc |  |
| `kpw` | North Korean won |  |
| `krw` | South Korean won | `₩`, `won`, `korean won` |
| `kwd` | Kuwaiti dinar |  |
| `kyd` | Cayman Islands dollar |  |
| `kzt` | Kazakhstani tenge |  |
| `lak` | Lao kip |  |
| `lbp` | Lebanese pound |  |
| `lkr` | Sri Lankan rupee |  |
| `lrd` | Liberian dollar |  |
| `lsl` | Lesotho loti |  |
| `lyd` | Libyan dinar |  |
| `mad` | Moroccan dirham |  |
| `mdl` | Moldovan leu |  |
| `mga` | Malagasy ariary |  |
| `mkd` | Macedonian denar | `ден` |
| `mmk` | Myanmar kyat |  |
| `mnt` | Mongolian tögrög |  |
| `mop` | Macanese pataca |  |
| `mro` | Mauritanian ouguiya |  |
| `mru` | Mauritanian ouguiya |  |
| `mur` | Mauritian rupee |  |
| `mvr` | Maldivian rufiyaa |  |
| `mwk` | Malawian kwacha |  |
| `mxn` | Mexican peso | `mexican peso`, `mexican pesos` |
| `mxv` | Mexican Unidad de Inversion |  |
| `myr` | Malaysian ringgit | `RM`, `ringgit`, `ringgits`, `malaysian ringgit` |
| `mzn` | Mozambican metical | `MT` |
| `nad` | Namibian dollar |  |
| `ngn` | Nigerian naira | `₦` |
| `nio` | Nicaraguan córdoba | `C$` |
| `nok` | Norwegian krone | `norwegian krone`, `norwegian kroner` |
| `npr` | Nepalese rupee |  |
| `nzd` | New Zealand dollar | `nz$`, `new zealand dollar`, `new zealand dollars` |
| `omr` | Omani rial |  |
| `pab` | Panamanian balboa | `B/.` |
| `pen` | Peruvian Sol | `S/.` |
| `pgk` | Papua New Guinean kina |  |
| `php` | Philippine peso | `₱`, `philippine peso`, `philippine pesos` |
| `pkr` | Pakistani rupee |  |
| `pln` | Polish złoty | `zł`, `zloty`, `złoty` |
| `pyg` | Paraguayan guaraní | `Gs` |
| `qar` | Qatari riyal |  |
| `ron` | Romanian leu |  |
| `rsd` | Serbian dinar |  |
| `rub` | Russian ruble | `₽`, `ruble`, `rouble`, `rubles`, `roubles` |
| `rwf` | Rwandan franc |  |
| `sar` | Saudi riyal | `riyal`, `riyals`, `saudi riyal` |
| `sbd` | Solomon Islands dollar |  |
| `scr` | Seychelles rupee |  |
| `sdg` | Sudanese pound |  |
| `sek` | Swedish krona | `krona`, `kronor`, `swedish krona`, `swedish kronor` |
| `sgd` | Singapore dollar | `s$`, `sing dollars`, `singapore dollar`, `singapore dollars` |
| `shp` | Saint Helena pound |  |
| `sle` | Sierra Leonean leone |  |
| `sll` | Sierra Leonean leone |  |
| `sos` | Somali shilling |  |
| `srd` | Surinamese dollar |  |
| `ssp` | South Sudanese pound |  |
| `std` | São Tomé and Príncipe dobra |  |
| `stn` | São Tomé and Príncipe dobra |  |
| `svc` | Salvadoran colón |  |
| `syp` | Syrian pound |  |
| `szl` | Swazi lilangeni |  |
| `thb` | Thai baht | `฿`, `baht`, `thai baht` |
| `tjs` | Tajikistani somoni |  |
| `tmt` | Turkmenistani manat |  |
| `tnd` | Tunisian dinar |  |
| `top` | Tongan paʻanga |  |
| `try` | Turkish lira | `₺`, `lira`, `turkish lira` |
| `ttd` | Trinidad and Tobago dollar | `TT$` |
| `tvd` | Tuvaluan dollar |  |
| `twd` | New Taiwan dollar | `nt$`, `taiwan dollar`, `taiwan dollars` |
| `tzs` | Tanzanian shilling |  |
| `uah` | Ukrainian hryvnia | `₴` |
| `ugx` | Ugandan shilling |  |
| `usd` | United States dollar | `$`, `us$`, `buck`, `usd$`, `bucks`, `dollar`, `dollars`, `us dollar`, `us dollars`, `american dollar`, `american dollars` |
| `uyi` | Uruguay Peso en Unidades Indexadas |  |
| `uyu` | Uruguayan peso |  |
| `uzs` | Uzbekistan som |  |
| `vef` | Venezuelan bolívar |  |
| `ves` | Venezuelan bolívar |  |
| `vnd` | Vietnamese đồng | `₫`, `dong`, `vietnamese dong` |
| `vuv` | Vanuatu vatu |  |
| `wst` | Samoan tala |  |
| `xaf` | Central African CFA franc |  |
| `xag` | Silver (troy ounce) | `silver` |
| `xau` | Gold (troy ounce) | `gold` |
| `xcd` | East Caribbean dollar |  |
| `xcg` | Caribbean guilder |  |
| `xdr` | Special drawing rights |  |
| `xof` | West African CFA franc |  |
| `xpd` | Palladium (troy ounce) | `palladium` |
| `xpf` | CFP franc |  |
| `xpt` | Platinum (troy ounce) | `platinum` |
| `yer` | Yemeni rial |  |
| `zar` | South African rand | `rand`, `south african rand` |
| `zmw` | Zambian kwacha |  |
| `zwg` | Zimbabwe gold | `Z$` |
| `zwl` | Zimbabwean dollar |  |

## Appendix B: Units

The first column is what `custom-keys.json` values and the **Default units** setting refer to; any spelling in the last column works too, as does a plural ending in `s`. `m`, `d`, `w`, `oz` and `tb` appear twice because they take the meaning that fits the other side of the conversion, and `N` is both a weight and a force. Words in Indonesian, Spanish and Swedish are in `lang/id_ID-keys.json`, `lang/es_ES-keys.json` and `lang/sv_SE-keys.json`.

### Length

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `m` | m | `meter`, `metre`, `meters`, `metres` |
| `km` | km | `kilometer`, `kilometre`, `kilometers`, `kilometres` |
| `dm` | dm | `decimeter`, `decimetre`, `decimeters`, `decimetres` |
| `cm` | cm | `centimeter`, `centimetre`, `centimeters`, `centimetres` |
| `mm` | mm | `milimeter`, `milimeters`, `millimeter`, `millimetre`, `millimeters`, `millimetres` |
| `μm` | μm | `um`, `micron`, `microns`, `micrometer`, `micrometre`, `micrometers`, `micrometres` |
| `nm` | nm | `nanometer`, `nanometre`, `nanometers`, `nanometres` |
| `pm` | pm | `picometer`, `picometers` |
| `in` | in | `"`, `″`, `inch`, `inches` |
| `ft` | ft | `'`, `′`, `feet`, `foot`, `feets`, `foots` |
| `yd` | yd | `yard`, `yards` |
| `mi` | mi | `mile`, `miles` |
| `nmi` | nmi | `nautical mile`, `nautical miles` |
| `fur` | fur | `furlong`, `furlongs` |
| `ftm` | ftm | `fathom`, `fathoms` |
| `hh` | hands | `hand`, `hands` |
| `ly` | ly | `lightyear`, `light year`, `lightyears`, `light years` |
| `au` | au | `astronomical unit`, `astronomical units` |
| `pc` | pc | `parsec`, `parsecs` |

### Area

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `m2` | m² | `m^2`, `sqm`, `sq m`, `square meter`, `square metre`, `square meters`, `square metres` |
| `km2` | km² | `km^2`, `sqkm`, `sq km`, `square kilometer`, `square kilometre`, `square kilometers`, `square kilometres` |
| `cm2` | cm² | `cm^2`, `sq cm`, `square centimeter`, `square centimeters` |
| `mm2` | mm² | `mm^2`, `sq mm`, `square millimeter`, `square millimeters` |
| `in2` | in² | `in^2`, `sqin`, `sq in`, `square inch`, `square inches` |
| `ft2` | ft² | `ft^2`, `sqft`, `sq ft`, `square feet`, `square foot` |
| `yd2` | yd² | `sqyd`, `yd^2`, `sq yd`, `square yard`, `square yards` |
| `mi2` | mi² | `mi^2`, `sqmi`, `sq mi`, `square mile`, `square miles` |
| `ac` | ac | `acre`, `acres` |
| `ha` | ha | `hectare`, `hectares` |
| `are` | are | `ares` |
| `tumbak` | tumbak |  |

### Volume

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `l` | l | `liter`, `litre`, `liters`, `litres` |
| `dm3` | dm³ |  |
| `ml` | ml | `mililiter`, `mililiters`, `milliliter`, `millilitre`, `milliliters`, `millilitres` |
| `cl` | cl | `centiliter`, `centilitre`, `centiliters`, `centilitres` |
| `dl` | dl | `deciliter`, `decilitre`, `deciliters`, `decilitres` |
| `cm3` | cm³ | `cc`, `cm^3`, `cubic centimeter`, `cubic centimeters` |
| `hl` | hl | `hectoliters`, `hectolitres` |
| `kl` | kl | `kiloliters`, `kilolitres` |
| `m3` | m³ | `cbm`, `m^3`, `cubic meter`, `cubic metre`, `cubic meters`, `cubic metres` |
| `pt` | pt | `pint`, `pints` |
| `uspt` | US pt | `uspint`, `us pint`, `us-pint`, `uspints`, `us pints`, `us-pints` |
| `ukpt` | UK pt | `uk pt`, `ukpint`, `uk pint`, `uk-pint`, `ukpints`, `uk pints`, `uk-pints`, `imperial pint`, `imperial pints` |
| `gal` | gal | `gallon`, `gallons` |
| `usgal` | US gal | `us gal`, `us-gal`, `usgallon`, `us gallon`, `us-gallon`, `us gallons` |
| `ukgal` | UK gal | `uk gal`, `uk-gal`, `ukgallon`, `uk gallon`, `uk-gallon`, `uk gallons`, `imperial gallon`, `imperial gallons` |
| `qt` | qt | `quart`, `quarts` |
| `usqt` | US qt | `us qt`, `us-qt`, `usquart`, `us quart`, `us-quart`, `us quarts` |
| `ukqt` | UK qt | `uk qt`, `uk-qt`, `ukquart`, `uk quart`, `uk-quart`, `uk quarts`, `imperial quart`, `imperial quarts` |
| `yd3` | yd³ | `yd^3`, `cu yd`, `cubic yard`, `cubic yards` |
| `ft3` | ft³ | `ft^3`, `cu ft`, `cubic feet`, `cubic foot` |
| `in3` | in³ | `in^3`, `cu in`, `cubic inch`, `cubic inches` |
| `floz` | fl oz | `fl oz`, `fl.oz`, `fl. oz`, `us floz`, `us-floz`, `fluid oz`, `us fl oz`, `fluid ounce`, `fluid ounces`, `us fluid ounce`, `us fluid ounces`, `oz` |
| `ukfloz` | UK fl oz | `uk floz`, `uk fl oz`, `uk fluid ounce`, `uk fluid ounces`, `imperial fluid ounce`, `imperial fluid ounces` |
| `cup` | cup | `cups` |
| `tbsp` | tbsp | `tbs`, `tbsps`, `tablespoon`, `tablespoons`, `tb` |
| `tsp` | tsp | `tsps`, `teaspoon`, `teaspoons` |

### Weight

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `kg` | kg | `kilo`, `kilos`, `kilogram`, `kilograms` |
| `g` | g | `gram`, `grams` |
| `mg` | mg | `miligram`, `miligrams`, `milligram`, `milligrams` |
| `μg` | μg | `ug`, `mcg`, `microgram`, `micrograms` |
| `N` | N | `newton`, `newtons` |
| `st` | st | `stone`, `stones` |
| `lb` | lb | `lbs`, `pound`, `pounds` |
| `oz` | oz | `ounce`, `ounces` |
| `ozt` | oz t | `toz`, `oz t`, `troy oz`, `troy ounce`, `troy ounces` |
| `ct` | ct | `carat`, `carats` |
| `t` | t | `ton`, `tons`, `tonne`, `tonnes`, `metric ton`, `metric tons` |
| `ukt` | UK long tons | `long ton`, `long tons` |
| `ust` | US short tons | `short ton`, `short tons` |
| `ons` | ons |  |
| `kuintal` | kuintal | `quintal`, `quintals` |

### Speed

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `mps` | m/s | `m/s`, `meter per second`, `meters per second`, `metres per second` |
| `kph` | km/h | `kmh`, `km/h`, `kmph`, `km per hour`, `kilometer per hour`, `kilometers per hour`, `kilometres per hour` |
| `mph` | mph | `mi/h`, `mile hour`, `mile per hour`, `miles per hour` |
| `fps` | ft/s | `ft/s`, `feet per second`, `foot per second` |
| `knot` | kn | `kn`, `kt`, `kts`, `knots` |

### Angles

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `deg` | deg | `°`, `degree`, `degrees` |
| `rad` | rad | `radian`, `radians` |
| `arcmin` | arcmin | `arcminute`, `arc minute`, `arcminutes`, `arc minutes` |
| `arcsec` | arcsec | `arcsecond`, `arc second`, `arcseconds`, `arc seconds` |
| `rev` | rev | `turn`, `turns`, `revolution`, `revolutions` |
| `grad` | grad | `gon`, `gons`, `gradian`, `gradians` |

### Temperature

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `k` | K | `°k`, `kelvin`, `kelvins` |
| `c` | °C | `°c`, `degc`, `deg c`, `celsius`, `centigrade`, `degree celsius`, `degrees celsius` |
| `f` | °F | `°f`, `degf`, `deg f`, `fahrenheit`, `fahrenheits`, `degree fahrenheit`, `degrees fahrenheit` |

### Pressure

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `pa` | Pa | `pascal`, `pascals` |
| `hpa` | hPa | `hectopascals` |
| `kpa` | kPa | `kilopascals` |
| `mpa` | MPa | `megapascals` |
| `bar` | bar | `bars` |
| `mbar` | mbar | `millibar`, `millibars` |
| `psi` | psi |  |
| `atm` | atm | `atmosphere`, `atmospheres` |
| `torr` | torr |  |
| `mmhg` | mmHg | `mm hg` |
| `inhg` | inHg | `in hg`, `inch of mercury`, `inches of mercury` |

### Time

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `s` | s | `sec`, `secs`, `second`, `seconds` |
| `year` | year | `y`, `yr`, `yrs`, `years` |
| `month` | month | `mo`, `mos`, `months` |
| `week` | week | `wk`, `wks`, `weeks`, `w` |
| `day` | day | `days`, `d` |
| `hr` | hr | `h`, `hrs`, `hour`, `hours` |
| `min` | min | `mins`, `minute`, `minutes`, `m` |
| `ms` | ms | `millisecond`, `milliseconds` |
| `μs` | μs | `microsecond`, `microseconds` |
| `ns` | ns | `nanosecond`, `nanoseconds` |
| `fortnight` | fortnight | `fortnights` |
| `decade` | decade | `decades` |
| `century` | century | `centuries` |

### Energy

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `j` | J | `joule`, `joules` |
| `kj` | kJ | `kilojoule`, `kilojoules` |
| `mj` | MJ | `megajoule`, `megajoules` |
| `cal` | cal | `calorie`, `calories` |
| `kcal` | kcal | `kilocalorie`, `kilocalories` |
| `Nm` | Nm | `newton meter`, `newton meters`, `newton metres` |
| `ftlb` | ft⋅lb | `ft lb`, `ft-lb`, `ft lbs`, `foot pound`, `foot pounds` |
| `whr` | Wh | `wh`, `watt hour`, `watt hours` |
| `kwhr` | kWh | `kwh`, `kilowatt hour`, `kilowatt hours` |
| `mwhr` | MWh | `mwh`, `megawatt hour`, `megawatt hours` |
| `gwhr` | GWh | `gwh`, `gigawatt hour`, `gigawatt hours` |
| `twhr` | TWh | `twh`, `terawatt hour`, `terawatt hours` |
| `ev` | eV | `electronvolt`, `electron volt`, `electronvolts`, `electron volts` |
| `mev` | MeV |  |
| `btu` | BTU | `btus`, `british thermal unit`, `british thermal units` |

### Power

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `w` | W | `watt`, `watts` |
| `kw` | kW | `kilowatt`, `kilowatts` |
| `MW` | MW | `megawatt`, `megawatts` |
| `GW` | GW | `gigawatt`, `gigawatts` |
| `ps` | PS | `metric horsepower` |
| `hp` | hp | `horsepower`, `mechanical horsepower` |
| `btu/h` | BTU/h | `btuh`, `btu/hr`, `btu per hour`, `btus per hour` |

### Frequency and rotation speed

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `Hz` | Hz | `hertz` |
| `kHz` | kHz | `kilohertz` |
| `MHz` | MHz | `megahertz` |
| `GHz` | GHz | `gigahertz` |
| `THz` | THz | `terahertz` |
| `rpm` | rpm | `r/min`, `rev/min`, `revolutions per minute` |
| `rps` | rps | `revolutions per second` |
| `rad/s` | rad/s | `radians per second` |

### Force

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `N` | N | `newton`, `newtons` |
| `kN` | kN | `kilonewton`, `kilonewtons` |
| `lbf` | lbf | `lbs force`, `pound force`, `pound-force`, `pounds force`, `pounds-force` |
| `kgf` | kgf | `kp`, `kilogram force`, `kilogram-force`, `kilograms force`, `kilograms-force` |

### Acceleration

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `m/s2` | m/s² | `m/s/s`, `m/s^2`, `meters per second squared`, `metres per second squared` |
| `ft/s2` | ft/s² | `ft/s/s`, `ft/s^2`, `feet per second squared` |
| `gn` | g | `g`, `gee`, `g force`, `g-force`, `standard gravity` |

### Fuel economy

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `km/l` | km/l | `kpl`, `kmpl`, `km/liter`, `km/litre`, `km per liter`, `km per litre`, `kilometers per liter`, `kilometres per litre` |
| `l/100km` | l/100 km | `lp100km`, `l/100 km`, `l per 100 km`, `liters per 100km`, `litres per 100km`, `liters per 100 km`, `litres per 100 km` |
| `mpg` | mpg | `mpg us`, `us mpg`, `miles per gallon` |
| `ukmpg` | UK mpg | `mpg uk`, `uk mpg`, `imperial mpg`, `miles per imperial gallon` |

### Data rates

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `bit/s` | bit/s | `bits/s`, `bit per second`, `bits per second` |
| `kbit/s` | kbit/s | `kbits/s`, `kilobit per second`, `kilobits per second` |
| `Mbit/s` | Mbit/s | `mbits/s`, `megabit per second`, `megabits per second` |
| `Gbit/s` | Gbit/s | `gbits/s`, `gigabit per second`, `gigabits per second` |
| `Tbit/s` | Tbit/s | `terabit per second`, `terabits per second` |
| `B/s` | B/s | `byte per second`, `bytes per second` |
| `kB/s` | kB/s | `kilobyte per second`, `kilobytes per second` |
| `MB/s` | MB/s | `megabyte per second`, `megabytes per second` |
| `GB/s` | GB/s | `gigabyte per second`, `gigabytes per second` |
| `TB/s` | TB/s | `terabyte per second`, `terabytes per second` |
| `KiB/s` | KiB/s | `kibibytes per second` |
| `MiB/s` | MiB/s | `mebibytes per second` |
| `GiB/s` | GiB/s | `gibibytes per second` |

`bps`, `kbps`, `mbps`, `gbps` and `tbps` are bits per second. Typed in lower case, `kb/s` to `tb/s` are bytes per second, as `mb` is a megabyte everywhere else. With capitals the letter decides: `Mb/s` and `Mbps` are megabits, `MB/s` and `MBps` megabytes.

### Screen density

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `ppi` | ppi | `dpi`, `dots per inch`, `pixels per inch` |
| `ppcm` | ppcm | `dpcm`, `dots per centimeter`, `pixels per centimeter`, `pixels per centimetre` |

### Data storage

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `bit` | bit | `bits` |
| `b` | B | `byte`, `bytes` |
| `kb` | kB | `kilobyte`, `kilobytes` |
| `mb` | MB | `mega`, `megas`, `megabyte`, `megabytes` |
| `gb` | GB | `giga`, `gigas`, `gigabyte`, `gigabytes` |
| `tb` | TB | `tera`, `teras`, `terabyte`, `terabytes` |
| `pb` | PB | `peta`, `petas`, `petabyte`, `petabytes` |
| `eb` | EB | `exa`, `exas`, `exabyte`, `exabytes` |
| `zb` | ZB | `z`, `zetta`, `zettabyte`, `zettabytes` |
| `yb` | YB | `y`, `yotta`, `yottas`, `yottabyte`, `yottabytes` |
| `kib` | KiB | `kibibyte`, `kibibytes` |
| `mib` | MiB | `mebi`, `mebis`, `mebibyte`, `mebibytes` |
| `gib` | GiB | `gibi`, `gibis`, `gibibyte`, `gibibytes` |
| `tib` | TiB | `tebi`, `tebis`, `tebibyte`, `tebibytes` |
| `pib` | PiB | `pebi`, `pebis`, `pebibyte`, `pebibytes` |
| `eib` | EiB | `exbi`, `exbis`, `exbibyte`, `exbibytes` |
| `zib` | ZiB | `zebi`, `zebis`, `zebibyte`, `zebibytes` |
| `yib` | YiB | `yobi`, `yobis`, `yobibyte`, `yobibytes` |

## Appendix C: Time zone names

These names are built in. Any city in the world time zone database works as well (`kuala lumpur`, `london`, `sydney`), as does an offset (`+07:00`, `utc+7`, `gmt-5`).

| Zone | Names |
| --- | --- |
| Africa/Johannesburg | `sast` |
| Africa/Lagos | `wat` |
| Africa/Nairobi | `eat` |
| America/Anchorage | `akst`, `akdt` |
| America/Argentina/Buenos Aires | `art` |
| America/Chicago | `cst`, `cdt`, `ct`, `central`, `dallas`, `houston` |
| America/Denver | `mst`, `mdt`, `mt`, `mountain` |
| America/Los Angeles | `pst`, `pdt`, `pt`, `pacific`, `san francisco`, `seattle` |
| America/Mexico City | `mexico` |
| America/New York | `est`, `edt`, `et`, `eastern`, `washington`, `boston`, `miami` |
| America/Sao Paulo | `brt` |
| Asia/Bangkok | `ict`, `thailand` |
| Asia/Dubai | `gst`, `uae` |
| Asia/Ho Chi Minh | `vietnam` |
| Asia/Hong Kong | `hkt` |
| Asia/Jakarta | `wib`, `indonesia` |
| Asia/Jayapura | `wit` |
| Asia/Karachi | `pkt` |
| Asia/Kolkata | `ist`, `india` |
| Asia/Kuala Lumpur | `myt`, `malaysia` |
| Asia/Makassar | `wita`, `bali` |
| Asia/Manila | `pht`, `philippines` |
| Asia/Seoul | `kst`, `korea` |
| Asia/Shanghai | `china`, `beijing` |
| Asia/Singapore | `sgt` |
| Asia/Tokyo | `jst`, `japan` |
| Australia/Adelaide | `acst`, `acdt` |
| Australia/Perth | `awst` |
| Australia/Sydney | `aest`, `aedt` |
| Europe/Athens | `eet`, `eest` |
| Europe/Berlin | `germany` |
| Europe/Lisbon | `wet` |
| Europe/London | `bst`, `uk` |
| Europe/Madrid | `spain` |
| Europe/Moscow | `msk` |
| Europe/Paris | `cet`, `cest`, `france` |
| Europe/Rome | `italy` |
| Europe/Stockholm | `sweden` |
| Pacific/Auckland | `nzst`, `nzdt`, `new zealand` |
| Pacific/Honolulu | `hst` |
| UTC | `utc`, `gmt`, `z`, `zulu` |

## Appendix D: Date format letters

For **Date formats**. The examples show Thursday 3 December 2026, 18:05:09 in Asia/Jakarta. Month and weekday names follow **Language**. Any other character prints as it is; a backslash prints the next letter as it is.

| Letter | Prints | Example |
| --- | --- | --- |
| `d` | day of the month, 2 digits | 03 |
| `j` | day of the month | 3 |
| `S` | English ordinal suffix, used after `j` | rd (in 3rd) |
| `D` | short weekday name | Thu |
| `l` | full weekday name | Thursday |
| `N` | weekday number, Monday 1 to Sunday 7 | 4 |
| `w` | weekday number, Sunday 0 to Saturday 6 | 4 |
| `z` | day of the year, from 0 | 336 |
| `W` | ISO week number | 49 |
| `F` | full month name | December |
| `M` | short month name | Dec |
| `m` | month, 2 digits | 12 |
| `n` | month | 12 |
| `t` | days in the month | 31 |
| `L` | 1 in a leap year, else 0 | 0 |
| `Y` | year | 2026 |
| `y` | year, 2 digits | 26 |
| `o` | ISO week-numbering year | 2026 |
| `a` / `A` | am or pm / AM or PM | pm / PM |
| `g` / `G` | hour, 12-hour / 24-hour | 6 / 18 |
| `h` / `H` | hour, 12-hour / 24-hour, 2 digits | 06 / 18 |
| `i` | minutes | 05 |
| `s` | seconds | 09 |
| `v` / `u` | milliseconds / microseconds | 000 / 000000 |
| `e` | time zone name | Asia/Jakarta |
| `T` | time zone abbreviation | WIB |
| `P` / `O` | UTC offset, with / without a colon | +07:00 / +0700 |
| `p` | like `P`, but `Z` for UTC | +07:00 |
| `Z` | UTC offset in seconds | 25200 |
| `I` | 1 during daylight saving time, else 0 | 0 |
| `c` | ISO 8601 | 2026-12-03T18:05:09+07:00 |
| `r` | RFC 2822 | Thu, 03 Dec 2026 18:05:09 +0700 |
| `U` | Unix timestamp | 1796295909 |
