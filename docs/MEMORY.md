# Project memory

Shared memory for everyone who works on this workflow, person or agent, whichever tool they use. Add an entry when you learn something the next one would otherwise rediscover the hard way: a decision and its reason, a verified behaviour, an environment fact, a trap. Date every entry (YYYY-MM-DD), and delete entries that stop being true.

## Status (2026-11-15)

- v5.0.1, public at https://github.com/situmorang-com/alfred-calculate-anything, released as `v5.0.1` with `Calculate.Anything.alfredworkflow` attached, and installed on the owner's Mac (where: `docs/LOCAL.md`).
- Verified in Alfred: `100 usd to idr` (flag, rate age), `1 btc` (IDR, USD and EUR rows), `100 km to miles` (two rows), `time +15 days`, `vat 400`, `color #ff6600` (swatches), and `1password` (no rows from this workflow). Return copied `1,822,936.37`, ⌘ Return `1822936.37`, ⌥ Return `18229.363747`.
- Verified offline: the 66 tests on Python 3.9.6 and 3.15; a fuzz run of 12,000 random queries (numbers, units, keywords, junk, odd settings) with no crash after fixing the one it found.
- Not verified yet: the Configure Workflow panel in Alfred, `_caclear` inside Alfred, the Fixer and CoinMarketCap key paths (no keys to test with), Spanish and Swedish inside Alfred.

## Decisions

### Python instead of PHP (2026-11-13)

macOS has shipped no PHP since macOS 12, and installing it was upstream's most common failure. `/usr/bin/python3` is present wherever Xcode or the Command Line Tools are, starts in about 40 ms, and with the standard library only there is nothing to install. The trade-off: on a Mac without the developer tools, `/usr/bin/python3` is only an installer stub.

### Free rate sources with fallbacks (2026-11-13)

Fixer's free tier now answers 401 and exchangerate.host wants a key. The probe results that set the source order are under "Rate sources" below. A Fixer or CoinMarketCap key, if the owner adds one, is tried first.

### Rates are never fetched while typing (2026-11-13)

Alfred runs the script on every keystroke, and a download takes 0.1 to 1.7 s. Upstream fetched in that path and could hang on "Updating rates..." (#158). A query answers from the cache and starts a detached refresh; Alfred's `rerun` picks up the result.

### Refresh intervals (2026-11-13)

Currency every 6 hours, because the free sources publish daily. Crypto every 15 minutes.

### Coins versus ordinary words (2026-11-13)

Hundreds of tickers are ordinary words (`ONE`, `WHY`, `A`, `GAS`). Fuzzing everyday searches produced false answers for `1 a`, `3 in one` and `20 20 vision`. The rule: a bare `<n> <ticker>` answers only for the 250 largest coins with tickers longer than one letter; an explicit target allows any coin; a currency code beats a ticker; a keyword-file word beats a ticker (`sats`). `real` is deliberately not a keyword for the Brazilian real.

### Spaces in numbers (2026-11-13)

A space is a thousands separator only between real groups of three (`1 000 000`), so `20 20 vision` is not 2020.

### Defaults come from the Mac (2026-11-13)

Base currencies default to the region's currency plus USD and EUR (IDR, USD, EUR on a Mac set to Indonesia), the time zone to `/etc/localtime`, and slash dates to the region's order (month first only in US-style regions).

### Own bundle id (2026-11-13)

`com.situmorang.calculateanything`, not upstream's `com.alfred.calculateanything`, so an upstream install and its data folder are never touched.

### No bytecode in the folder (2026-11-15)

The folder sits inside the Alfred preferences, which are backed up as a whole. Alfred's triggers point `PYTHONPYCACHEPREFIX` at the workflow cache, and `calculate.py` and the tests write no bytecode otherwise.

### Keep the `time` keyword (2026-11-15, owner)

DevToys also uses `time`, and its row sorts first, so this workflow's results start on row 2 (⌘2). The owner chose to keep `time`.

### VAT defaults to Indonesia's 11% (2026-11-15, owner)

The owner asked for Indonesian VAT. Indonesia's PPN has been 12% by law since 2025-01-01, but under PMK 131/2024 everything except luxury goods (those subject to PPnBM) is taxed on a base of 11/12 of the price, so the effective rate is 11%; luxury goods pay 12%. The Ministry of Finance confirmed the same arrangement for 2026 ([Kontan](https://nasional.kontan.co.id/news/kemenkeu-pastikan-tarif-ppn-12-tetap-berlaku-untuk-barang-mewah-pada-2026), [DDTCNews](https://news.ddtc.co.id/berita/nasional/1812992/tak-berubah-tarif-ppn-12-tetap-berlaku-untuk-barang-mewah-di-2026)). Check again each January. The default lives in `info.plist` (the `vat_value` field) and in `Settings`; `ppn` is accepted as a VAT word.

### Docs live in this folder (2026-11-15, owner)

So any LLM tool can continue the work from the folder. `AGENTS.md` is canonical; `CLAUDE.md` and `GEMINI.md` import it. Project knowledge goes here rather than into one tool's private memory.

### Public repository (2026-11-15, owner)

The folder is a git repository, published at https://github.com/situmorang-com/alfred-calculate-anything. Notes about the owner's Mac live in `docs/LOCAL.md`, which git ignores, and so is `prefs.plist` (the owner's settings, which can hold API keys).

## Alfred behaviour (verified on Alfred 5.8.1)

- A Script Filter must print Script Filter JSON; anything else shows nothing.
- `rerun` makes Alfred run the script again with the same argument, until a reply comes back without `rerun`.
- Typing `1password` runs this workflow's `1` filter; its empty `items` list leaves Alfred's other results as they are.
- Two workflows with the same keyword both show rows. DevToys' `time` row sorts above this workflow's.
- A PNG named after an object's UID is that object's icon, and rows without their own icon inherit it (the clock on `time` rows).
- Alfred reads held modifiers from the login session's keyboard state. A Return posted to Alfred's process with modifier flags acts as a plain Return.

## Live testing in Alfred

Test from the command line first. Open Alfred only to see the rows or to check what a key copies.

1. Make sure nobody is using the Mac: ask for a couple of hands-off minutes, and stay on the command line during video calls. On the owner's Mac, follow `docs/LOCAL.md`, "Live testing here".
2. Build the helper outside this folder: `swiftc -O -o "$TMPDIR/alfredctl" tools/alfredctl.swift`.
3. Wait until `alfredctl window` exits 1, meaning no Alfred window is open. Another agent session may be testing another workflow.
4. Save the clipboard: `alfredctl pbsave "$TMPDIR/clip.plist"`. It keeps every item in every type, which `pbpaste` and `pbcopy` would flatten.
5. Open a query: `osascript -e 'tell application id "com.runningwithcrayons.Alfred" to search "100 usd to idr"'`, then wait about a second, since the rates may need a rerun.
6. Guard: press nothing unless `alfredctl field` prints exactly your query and `alfredctl window` lists a window.
7. Look: `screencapture -x -o -l <window id> out.png`, with the id from `alfredctl window`.
8. Act: `alfredctl key 36` (Return), `alfredctl modreturn cmd` or `alfredctl modreturn alt`, then read `pbpaste`.
9. Close with `alfredctl key 53` (Escape), then restore: `alfredctl pbrestore "$TMPDIR/clip.plist"`.

Run steps 5 to 9 in one shell command, because Alfred's window can close when focus moves.

Traps seen on 2026-11-15:

- Another agent session was driving Alfred at the same time, and its typed text landed in a test window. That is what the step 6 guard is for.
- In Swift, `exit()` skips `defer`. An earlier helper released the held modifier in a `defer` and so never released it; `modreturn` now releases it explicitly.
- Another session found that System Events `key down <modifier>`, `key code 36`, `key up <modifier>` also works for modifier keys.

## Tested with (2026-11-15)

macOS 27.2 on Apple silicon, Alfred 5.8.1, Python 3.9.6 (Xcode's `/usr/bin/python3`) and Python 3.15 (Homebrew). The owner's machine specifics are in `docs/LOCAL.md`, which is not in the public repository.

## Rate sources (probed on 2026-11-13)

| Source | Result |
| --- | --- |
| open.er-api.com | 200 in 0.12 s; 166 currencies; updated daily |
| fawazahmed0 currency API (jsDelivr and Cloudflare Pages) | 200 in 0.05 s; 339 entries including crypto; daily |
| api.frankfurter.dev | 200; 29 ECB currencies |
| ECB daily XML | 200; 29 currencies |
| floatrates.com | 200, but 1.1 s |
| exchangerate.host | an HTML page now; key required |
| fixer.io (APILayer) | 401 without a key |
| coinpaprika.com tickers | 200 in 0.3 s; 2,000 coins in 1.7 MB |
| coingecko.com markets | 200; 250 coins per page |
| coinlore.net | 200; 100 coins per page |
| CryptoCompare, CoinMarketCap | key required |
| Coinbase, Binance, Kraken, OKX | connection refused from the test network |
| coincap.io | DNS failure |

The free currency sources agreed within 0.25% on 16 sampled currencies.

## Data provenance

- `data/regions.json`: every ISO region's currency, read from macOS's own locale data (`NSLocale`) on 2026-11-13.
- `data/crypto-symbols.json`: the 1,500 largest coins on coinpaprika.com on 2026-11-13, plus `SAT`. It only matters until the first price download.
- `flags/`, `icon.png` and the clock icon come from upstream 4.0.7. `lang/*.json` were converted from upstream's PHP language files, then corrected and extended.

## History

- 2026-11-13: Studied upstream 4.0.7 and its 30 open issues, probed rate sources, rebuilt the workflow in Python, wrote the 66 tests.
- 2026-11-15: Installed and checked in Alfred. Fuzzing found a crash on date formats that print nothing; fixed. Added `"` and `'` as inches and feet. The owner kept `time`. Added these docs and `tools/alfredctl.swift`. Set the VAT default to Indonesia's 11% and accepted `ppn` (5.0.1). Published to GitHub.
