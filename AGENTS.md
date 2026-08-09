# Weekly monitor procedure

Run a complete, evidence-based Poland/EU price check for the workstation in `monitor-config.json`.

1. Read `monitor-config.json`, the latest report in `reports/`, and all `data/observations.csv` rows before researching.
2. Search exact SKUs first. Use established Polish sellers, then established EU sellers that ship to Poland. Record the actual contracting seller, not a marketplace host.
3. For every observation capture date, category, exact product/SKU, seller/legal seller, country, gross price/currency, PLN conversion, VAT status, shipping, total delivered PLN, stock wording, warranty length/handler, RMA route/quality, direct URL, and evidence notes.
4. Append evidence-backed rows to `data/observations.csv`; never overwrite prior history. Unknown values remain `unknown`.
5. Reject incompatible near matches, especially: Enthoo Elite vs Enthoo Elite Server; `BK02` vs `BK03`; ATX 3.0 vs required PSU ATX 3.1; UDIMM vs ECC RDIMM; separately sourced RAM sticks vs matched 4-DIMM kit; oversized GPU substituted without dual-GPU analysis.
6. Calculate one-GPU and two-GPU totals only from purchase-compatible, currently available parts and delivered costs. If required parts are unavailable, label the total incomplete and show the known subtotal plus missing categories; never fabricate estimates.
7. Maintain first observed, previous, minimum, maximum, weekly change, total change, 30/90-day context when available, and detect fake discounts against this repository's own history.
8. Audit CPU/BIOS, memory QVL, case/motherboard/AIO/PSU/GPU dimensions, slot spacing/lane allocation, M.2 heatsinks, native 12V-2x6 leads, safe bend radius, EU mains requirements, fan groups, GPU support, and dual-GPU airflow before any BUY NOW recommendation.
9. Track a comparable full prebuilt with whole-system warranty. Require exact motherboard, RAM kit, GPU, PSU, cooling, storage, VAT, delivery, and cross-border collection/RMA details.
10. Write `reports/YYYY-MM-DD.md` in the requested report order: headline totals/deltas; detailed rows; BUY NOW / VERY GOOD PRICE / WATCH CLOSELY / WAIT; one- and two-GPU totals; prebuilt premium/savings; compatibility/warranty findings; evidence limitations and sources.
11. Validate JSON/CSV syntax and run `git diff --check`, then commit the completed weekly data/report changes to `main` with a concise conventional commit and push to `origin/main`. Never push a partial or failed report.
12. Send the user a concise Telegram summary with headline figures, alerts, missing/blocked parts, the report path, and the pushed commit identifier.

Architecture is locked. Never silently turn this into a conventional gaming PC or claim two GPUs automatically provide unified VRAM.
