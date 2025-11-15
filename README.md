# Repro Instructions Midterm-exam IDG3000

## Prerequisites
- macOS
- Node.js >= 18 (`node -v`)
- Chrome installed

## Install
```bash
cd /Users/hannasamborska/Documents/GitHub/idg3000-midterm-exam-hannasamborska/Midterm-exam/scripts/node
npm install
```

## Run full audit
```bash
node audit.js
node host-check.mjs
```

## Outputs
- evidence/lighthouse/*.json
- evidence/hosting/*_greencheck.json (+ carbon.txt files if any)
- evidence/summary.csv
- evidence/charts/*.png

## Regenerate
Delete evidence folder or run `npm run clean` (if added) then rerun commands above.

## Notes
- Fylke audited: Akershus (21 municipalities). No carbon.txt found (0/21).
- CO₂ models: OneByte & SWD via @tgwf/co2.
