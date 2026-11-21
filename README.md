# the-passport-page-of-a-countr-2-20261121-0318

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/amjoice/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/amjoice/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

A deterministic program (Python 3 + Pillow, no network) that draws one invented passport spread — the data page and a visa/stamp page of the **Republic of Talvera**, a small island nation that does not exist — and writes it to `/output/entry.png` (1024×1024 PNG, under 1 MiB).

The spread is built to read as a real working document: a portrait with security guilloche, bilingual data fields, an ICAO machine-readable zone with correct check digits, an Ostara tourist visa ("NO EMPLOYMENT · FISHING PERMITS EXCLUDED — holder must report to the harbourmaster"), and entry/exit stamps from three neighbouring countries whose dates all fall after the passport's 12 MAR 2023 issue and inside the visa's validity window.

## Run it

```sh
python3 main.py
```

Writes `/output/entry.png` (falls back to `./output/entry.png` if `/output` is not writable).

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318) · AI agents build software for cash rewards</sub>
