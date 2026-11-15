# Calculate Anything: user manual

For version 5.0.1 on Alfred 5 with the Powerpack. The example results were taken on 15 November 2026; exchange rates and prices change every day.

## Contents

1. [Getting started](#1-getting-started)
2. [Using results](#2-using-results)
3. [Currency](#3-currency)
4. [Cryptocurrency](#4-cryptocurrency)
5. [Units](#5-units)
6. [Data storage](#6-data-storage)
7. [Percentages](#7-percentages)
8. [CSS sizes](#8-css-sizes)
9. [VAT](#9-vat)
10. [Dates and times](#10-dates-and-times)
11. [Colors](#11-colors)
12. [Languages and your own words](#12-languages-and-your-own-words)
13. [Settings](#13-settings)
14. [Maintenance](#14-maintenance)
15. [Troubleshooting](#15-troubleshooting)
16. [Privacy](#16-privacy)

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
| `_caclear` | deleting the cached exchange rates | `_caclear` |

A query without a keyword must start with a number (a leading `.` or `-` works too: `.5 km to m`, `-25f to c`) and be at least three characters long. Everything else is left to Alfred, so ordinary searches such as `1password` are unaffected.

The first currency or crypto query after installing shows **Updating rates...** for a moment while the rates download.

## 2. Using results

| Key | Copies |
| --- | --- |
| Return | the result as shown, for example `1,822,936.37` |
| ⌘ Return | the number without formatting, `1822936.37` (currency, crypto, units, data storage, percentages, VAT) |
| ⌥ Return | currency and crypto: the rate for one unit, `18229.363747`; units and data storage: the result with its unit, `62.13711922 mi` |
| ⌘C | the selected row's value |
| ⌘L | the result in Large Type |
| ⌘1 to ⌘9 | the first to ninth row (an Alfred shortcut) |

Where a result has no ⌘ or ⌥ variant (CSS sizes, dates, colors), those keys copy what the row shows.

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

- Separators: `1,350.50`, `1 350.50` and `.5` all work. If you write decimals with a comma (`1.350,50`), set **Input decimal separator** to Comma.
- Multipliers: `k`, `thousand`, `m`, `mn`, `mio`, `million`, `b`, `bn`, `billion`, `t`, `tn`, `trillion` (`150k`, `2.5m`, `3 billion`). They apply to money only, so `5 m to ft` is five metres.
- Results show 2 decimals (**Currency decimals**). Very small results keep their significant digits instead of showing 0.00: `1 idr to usd` gives 0.000055 USD.

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
| `5' to cm` | 152.4 cm · 152 cm, 4 mm |
| `72 f to c` | 22.22 °C |
| `100 kg to lb` | 220.46226218 lb · 220 lb, 7.4 oz |
| `100 ml to oz` | 3.38140227 fl oz |
| `500 sqft to m2` | 46.45152 m² |
| `1 acre to m2` | 4,046.8564224 m² |
| `60 mph to kmh` | 96.56064 km/h |
| `1 cup to ml` | 236.5882365 ml |
| `3 tsp to tbsp` | 1 tbsp |
| `1 atm to psi` | 14.69594878 psi |
| `1 kwh to j` | 3,600,000 J |
| `2 h to min` | 120 minutes |
| `1 month to days` | 30.41666667 days · 30 days, 10 hours |

There are eleven categories: length, area, volume, weight, speed, rotation, temperature, pressure, time, energy and power. Write a unit as an abbreviation, a name or a plural; [Appendix B](#appendix-b-units) lists every accepted spelling.

- **Second row.** Where it helps, a second row gives the result in mixed units (`8 ft, 4 in`, `1 hour, 40 minutes`).
- **Ambiguous abbreviations** take the meaning that fits the other side: `h` is a hand (`5 h to cm`) or an hour (`2 h to min`); `m` a metre or a minute; `oz` an ounce of weight or a fluid ounce (`100 ml to oz`); `pt` a pint (`12 pt to l`) or a CSS point (`12pt to px`).
- **`in`** works both as a linking word and as inches: `100 cm in in` gives 39.37007874 in.
- **Temperatures** show 2 decimals.
- **Months and years** are averages here: a year is 365 days and a month a twelfth of that, 30.42 days. For calendar arithmetic, use `time`.
- Converting between categories, such as `100 km to kg`, shows an error row.

## 6. Data storage

| Query | Result |
| --- | --- |
| `2 gb to mb` | 2,000 MB |
| `100 gigabytes in megabytes` | 100,000 MB |
| `400 mib to kib` | 409,600 KiB |
| `1 gib to mb` | 1,073.741824 MB |
| `8 bit to b` | 1 B |

Units are `b` (byte), `kb` to `yb`, `kib` to `yib`, and `bit`, or their names (`megabytes`, `megas`, `gibibytes`); [Appendix B](#data-storage) lists them all. Decimal names follow the IEC standard, 1 MB = 1000 kB, while 1 MiB = 1024 KiB. Turn on **Data storage: Binary mode** to make 1 MB = 1024 kB.

## 7. Percentages

| Query | Result | Second row |
| --- | --- | --- |
| `120 + 30%` | 156 | 36, the 30% added |
| `120 - 30%` | 84 | 36, the 30% taken off |
| `15% of 50` | 7.5 | |
| `20% off 150` | 120 | 30, the discount |
| `40 as a % of 50` | 40 is 80% of 50 | the increase from 40 to 50 (25%) and the decrease from 50 to 40 (20%) |
| `30 % 40` | 30 is 75% of 40 | the increase (33.33333333%) and the decrease (25%) |

Words work too: `plus`, `minus`, `percent`, `pct`, `as a percent of`, `as a percentage of`, `is what % of`, `is what percent of`. With the comma decimal settings, `10,5 + 5%` gives 11,025.

## 8. CSS sizes

| Query | Result |
| --- | --- |
| `12px` | 0.75em · 0.75rem · 9pt |
| `2rem to pt` | 24pt |
| `12pt to px` | 16px |
| `12px in em base 17px` | 0.70588em |

The units are `px`, `em`, `rem` and `pt`. The root size is 16px (**Base pixels**); add `base 17px` to a query to use another. em and rem both convert from the root size.

## 9. VAT

The rate is 11% unless you change it: Indonesia's PPN on most goods and services. Luxury goods pay 12%. Set your own rate in **VAT percentage**.

| Query | Result |
| --- | --- |
| `vat 400` (or `vat of 400`) | VAT of 400 = 44 · 400 plus VAT = 444 · 400 minus VAT = 360.36 |
| `vat 400 12%` | the same at 12%, for this query only |
| `400 + vat` | 444 |
| `400 - vat` | 360.36 |

- "Minus VAT" is the price before tax, for when 400 already includes it (400 ÷ 1.11), not 400 less 11%.
- Without the keyword, `ppn`, `tax`, `gst` and `sales tax` work like `vat`, and `plus` and `minus` like `+` and `-`: `400 + ppn`, `400 minus tax`.

## 10. Dates and times

Type `time` and an expression. Each answer is listed in every date format you have set (**Date formats**), then how far away it is, then its Unix timestamp. Return copies a row.

| Kind | Examples |
| --- | --- |
| Now | `time` |
| Unix timestamps | `time 1577836800`, `time 1577836800000` (milliseconds), `time @1577836800` |
| Relative | `time +15 days`, `time 3 days ago`, `time now plus 3 days`, `time now minus 2 weeks`, `time tomorrow`, `time yesterday 9am`, `time next friday 3pm`, `time last monday`, `time next month`, `time +1 week 2 days` |
| Working days | `time today + 3 workdays` (also `business days`, `working days`, `wd`) |
| Counting | `time days until 31 december`, `time weeks until 1 january`, `time hours since yesterday`, in seconds, minutes, hours, days, weeks, months or years |
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

## 11. Colors

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

## 12. Languages and your own words

**Language** (English, Spanish or Swedish) sets the language of the results and adds that language's words to what you can type. English words work whatever the language.

| Language | Examples |
| --- | --- |
| Spanish | `100 euros a dolares`, `10 días a horas`, `120 más 30%`, `400 mas iva`, `time ahora más 3 días`, `time inicio de 2020`, `time dias hasta 31 diciembre` |
| Swedish | `5 kilometer till meter`, `100 kr till usd`, `400 plus moms`, `time början av 2021` |

### Your own words

Add words in a file named `custom-keys.json` in the workflow's data folder, `~/Library/Application Support/Alfred/Workflow Data/com.situmorang.calculateanything/`. It survives updates. For example, Indonesian:

```json
{
  "multipliers": { "ribu": 1000, "rb": 1000, "juta": 1000000, "jt": 1000000, "miliar": 1000000000 },
  "currency": { "stop_words": ["ke", "jadi"] },
  "units": { "stop_words": ["ke", "jadi"] }
}
```

Now `1.5 juta idr ke usd` gives 82.28 USD, `250rb idr ke sgd` gives 17.66 SGD, and `10 km ke m` gives 10,000 m.

| Section | A key is | Its value is |
| --- | --- | --- |
| `currency` | a word for a currency | its code: `"bucks": "USD"` |
| `crypto_currency` | a word for a coin | its ticker: `"sats": "SAT"` |
| `units` | a word for a unit | the unit as written in Appendix B: `"hakunamatata": "year"` |
| `datastorage` | a word for a data unit | `b`, `kb` to `yib`, or `bit` |
| `percentage`, `vat`, `time` | a word | what it stands for: `"plus": "+"` |
| `multipliers` | a word or suffix | a number: `"juta": 1000000` |

Each section can also take `"stop_words"`, the linking words between the two sides (`to`, `in`, `ke`); yours are added to the built-in ones. Where your words and the built-in ones differ, yours win. Changes apply from the next query.

## 13. Settings

Open Alfred Preferences, choose Workflows, select Calculate Anything, and click **Configure Workflow**.

| Setting | Default | What it does |
| --- | --- | --- |
| Language | English | Language of the results and of the words you can type. English words always work. |
| Base currencies | empty | Targets for an amount with no target, separated by commas. Empty means this Mac's currency, then USD, EUR and MYR. |
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
| Time keyword, VAT keyword, Color keyword | `time`, `vat`, `color` | Rename a keyword if another workflow uses it. |
| Fixer API key | empty | Optional; asked first for exchange rates. |
| CoinMarketCap API key | empty | Optional; asked first for coin prices. |

## 14. Maintenance

- **Refresh rates now:** type `_caclear`, press Return, then run any conversion. The rates download again.
- **Where data lives:** `~/Library/Application Support/Alfred/Workflow Data/com.situmorang.calculateanything/` holds the cached rates and prices, the color swatches and your `custom-keys.json`.
- **Update:** download the newest release and double-click it; Alfred offers to replace the old version and keeps your settings. If you installed with `git clone`, run `git pull` in the workflow's folder.
- **Remove:** delete the workflow in Alfred Preferences, and the data folder above if you like.

## 15. Troubleshooting

**Nothing appears.** Start with a number and type at least three characters. Check the spelling of the units or currencies. For a coin outside the 250 largest, name a target (`100 gas to usd`). Check that the workflow is enabled in Alfred Preferences.

**macOS asks to install command line developer tools.** Accept. The workflow runs on the Python 3 they include.

**"Updating rates..." stays, or "Unable to get currencies data" appears.** The rates could not be downloaded. Check the internet connection and try again in a minute. Rates downloaded earlier, if any, keep working.

**A rate looks out of date.** The subtitle shows its age. The free sources publish once a day; lower **Refresh currency rates every** to check more often, or type `_caclear` to download now.

**Every result appears twice.** The original Calculate Anything is still installed. Disable it in Alfred Preferences.

**`time` results are not in the first row.** Another workflow also uses the `time` keyword. Pick this workflow's row (⌘2 for the second), or rename **Time keyword**.

**A date is read the wrong way round.** Set **Dates like 01/02/2026** to day first or month first.

**Decimals typed with a comma give odd results.** Set **Input decimal separator** to Comma, and **Number output format** to `1.234,56` if you also want commas in results.

**VAT is wrong for your country.** Set **VAT percentage**.

**A word isn't recognised.** Add it to `custom-keys.json` ([Your own words](#your-own-words)).

**Anything else.** In Alfred Preferences, open the workflow and click the bug icon to open the debugger, type the query again, and read what the workflow printed.

## 16. Privacy

What you type stays on your Mac. The only network requests are the downloads of rates and prices described above: plain requests to those public services that carry no query, account or personal data. If you add one of the optional API keys, it is sent only to its own service.

## Appendix A: Currencies

Every currency the workflow knows, with its English name and the other ways to type it. The full English name works too (`indonesian rupiah`), as do plurals. Words in Spanish and Swedish are in `lang/es_ES-keys.json` and `lang/sv_SE-keys.json`.

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
| `xcd` | East Caribbean dollar |  |
| `xcg` | Caribbean guilder |  |
| `xdr` | Special drawing rights |  |
| `xof` | West African CFA franc |  |
| `xpf` | CFP franc |  |
| `yer` | Yemeni rial |  |
| `zar` | South African rand | `rand`, `south african rand` |
| `zmw` | Zambian kwacha |  |
| `zwg` | Zimbabwe gold | `Z$` |
| `zwl` | Zimbabwean dollar |  |

## Appendix B: Units

The first column is what results show and what `custom-keys.json` values refer to; any spelling in the last column works too, as does a plural ending in `s`. `h`, `m`, `d`, `w` and `oz` appear twice because they take the meaning that fits the other side of the conversion. Words in Spanish and Swedish are in `lang/es_ES-keys.json` and `lang/sv_SE-keys.json`.

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
| `h` | hands | `hand`, `hands` |
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

### Volume

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `l` | l | `liter`, `litre`, `liters`, `litres` |
| `dm3` | dm³ |  |
| `ml` | ml | `mililiter`, `mililiters`, `milliliter`, `millilitre`, `milliliters`, `millilitres` |
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
| `tbsp` | tbsp | `tbs`, `tbsps`, `tablespoon`, `tablespoons` |
| `tsp` | tsp | `tsps`, `teaspoon`, `teaspoons` |

### Weight

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `kg` | kg | `kilo`, `kilos`, `kilogram`, `kilograms` |
| `g` | g | `gram`, `grams` |
| `mg` | mg | `miligram`, `miligrams`, `milligram`, `milligrams` |
| `N` | N | `newton`, `newtons` |
| `st` | st | `stone`, `stones` |
| `lb` | lb | `lbs`, `pound`, `pounds` |
| `oz` | oz | `ounce`, `ounces` |
| `t` | t | `ton`, `tons`, `tonne`, `tonnes`, `metric ton`, `metric tons` |
| `ukt` | UK long tons | `long ton`, `long tons` |
| `ust` | US short tons | `short ton`, `short tons` |

### Speed

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `mps` | m/s | `m/s`, `meter per second`, `meters per second`, `metres per second` |
| `kph` | km/h | `kmh`, `km/h`, `kmph`, `km per hour`, `kilometer per hour`, `kilometers per hour`, `kilometres per hour` |
| `mph` | mph | `mi/h`, `mile hour`, `mile per hour`, `miles per hour` |
| `fps` | ft/s | `ft/s`, `feet per second`, `foot per second` |
| `knot` | kn | `kn`, `kt`, `kts`, `knots` |

### Rotation

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `deg` | deg | `°`, `degree`, `degrees` |
| `rad` | rad | `radian`, `radians` |

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

### Time

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `s` | s | `sec`, `secs`, `second`, `seconds` |
| `year` | year | `y`, `yr`, `yrs`, `years` |
| `month` | month | `mo`, `mos`, `months` |
| `week` | week | `wk`, `wks`, `weeks`, `w` |
| `day` | day | `days`, `d` |
| `hr` | hr | `hrs`, `hour`, `hours`, `h` |
| `min` | min | `mins`, `minute`, `minutes`, `m` |
| `ms` | ms | `millisecond`, `milliseconds` |
| `μs` | μs | `microsecond`, `microseconds` |
| `ns` | ns | `nanosecond`, `nanoseconds` |
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
| `mev` | MeV |  |
| `btu` | BTU | `btus`, `british thermal unit`, `british thermal units` |

### Power

| Unit | Shown as | Also typed as |
| --- | --- | --- |
| `w` | W | `watt`, `watts` |
| `kw` | kW | `kilowatt`, `kilowatts` |
| `ps` | PS | `metric horsepower` |
| `hp` | hp | `horsepower`, `mechanical horsepower` |

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
