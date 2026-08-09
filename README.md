# Threadripper RTX 5090 workstation price monitor

Weekly Poland/EU price, availability, warranty, RMA, and compatibility monitoring for a reliability-first Threadripper 9960X AI/gaming workstation through Black Friday 2026.

## Weekly component price matrix

Prices are gross PLN prices for the best verified qualifying offer on each observation date. `—` means no exact, purchase-compatible offer was verified. Foreign-currency listings use the cited NBP rate and exclude delivery until a Polish checkout total is available.

| Component | Qty | 2026-08-09 |
|---|---:|---:|
| Threadripper 9960X | 1 | 6,573.07 |
| Gigabyte TRX50 AI TOP | 1 | 4,579.00 |
| 256GB matched ECC RDIMM | 1 kit | No reputable PL/EU stock; target `F5-6400R3644E64GQ4-T5N` |
| 128GB matched ECC RDIMM fallback | 1 kit | No reputable PL/EU stock; current target `F5-6400R3239F32GQ4-T5N` |
| Four identical 64GB ECC RDIMMs | 4 | 28,253.88 `[RAM]` |
| RTX 5090 FE / ASUS ProArt | 1 | 20,999.00 |
| Thermaltake AW420 | 1 | 1,434.40 |
| Phanteks Enthoo Elite Server | 1 | 1,719.97 `[case]` |
| Seasonic PRIME PX-2200 ATX 3.1 | 1 | 2,173.14 `[PSU]` |
| Samsung 9100 PRO 4TB | 2 | 6,379.34 |
| Noctua NF-A14x25 G2 chromax | 6 | 1,013.82 |
| Noctua NF-A12x25 G2 chromax | 6 | 941.82 |
| **Provisional one-GPU total** |  | **74,067.44 `[total]`** |

Sources for 2026-08-09: Amazon.pl direct for the CPU; x-kom for the motherboard; NET-S for individual Micron RDIMMs; RTV Euro AGD via Ceneo evidence for the ProArt GPU; Morele direct for the PSU, AIO and fans; Senetic for SSDs; Caseking for the case. `[RAM]` assumes four NET-S modules at 7,063.47 PLN each, but four-unit inventory and identical revision/rank/batch must be confirmed. `[case]` is €399.90 converted at NBP EUR/PLN 4.301; the case is on pre-order and final Polish VAT/shipping is unresolved. `[PSU]` uses the directly purchasable Morele price; CAPS lists the same exact PSU at €468.72 / 2,015.96 PLN before final Polish VAT/shipping checkout verification. `[total]` uses the NET-S RAM configuration, RTV Euro AGD GPU, Morele PSU and Caseking displayed case price; it is not a buy-now total until RAM quantity identity, GPU checkout stock, case delivery, and final shipping/VAT are confirmed.

## Locked architecture

- CPU: AMD Ryzen Threadripper 9960X; track 9970X only when the premium becomes unusually compelling.
- Motherboard: Gigabyte TRX50 AI TOP; compare ASUS Pro WS TRX50-SAGE WiFi, but never substitute silently.
- RAM: 256GB remains the final target. Prefer a factory-matched 4x64GB ECC DDR5 RDIMM kit validated for TRX50. Also track matched 128GB 4x32GB kits as a temporary lower-cost starting point, plus four individually packaged 64GB RDIMMs when all four have the exact same manufacturer SKU/revision/rank/speed/timings/voltage and are bought together from one reputable seller, ideally from one batch. Never mix brands, SKUs, revisions, capacities, or memory types. The G.Skill Zeta R5 Neo 128GB reference `F5-6400R3239G32GQ4-ZR5NK` is marked EOL by G.Skill, so remaining reputable stock and current alternatives must be compared.
- GPU #1: RTX 5090 32GB, preferably NVIDIA Founders Edition or ASUS ProArt `PROART-RTX5090-O32G`; compact dual-GPU suitability matters.
- GPU #2: future matching RTX 5090. It is for supported multi-GPU AI/compute workloads, not unified VRAM or ordinary gaming.
- Cooler: Thermaltake AW420 TR5/SP6 `CL-W445-PL14BL-A`, top-mounted exhaust. No custom loop.
- Case: Phanteks Enthoo Elite Server `PH-ES916E_BK02`; fallback Enthoo Pro 2 Server V2 `PH-ES620PC_BK03`.
- PSU: Seasonic PRIME PX-2200 ATX 3.1. Seasonic officially confirms the 2200W ATX 3.1 / PCIe 5.1 model with two native 12V-2x6 cables. Retailer SKU `PRIME-PX-2200-ATX30`, EAN `4711173878414`, is the compatible product despite the legacy-looking `ATX30` suffix and inconsistent retailer title shorthand. Do not reject it based on the suffix alone.
- Storage: 2x Samsung 9100 PRO 4TB bare drives `MZ-VAP4T0BW` (one initially acceptable if pricing is poor).
- Fans: 6x Noctua NF-A14x25 G2 PWM chromax.black (4 front intake, 2 rear exhaust) and 6x Noctua NF-A12x25 G2 PWM chromax.black (side GPU intake). AW420's 3x140mm fans are top exhaust. Aim for slight positive pressure.
- Hubs/support: use included Phanteks hardware first; add Noctua NA-FH1 or extra GPU supports only if proven necessary.
- OS role: Windows 11 Pro desktop/gaming plus Linux AI, CUDA, Docker, LXC, VM, homelab, and development workloads.

## Buying priorities

1. Reliability
2. Warranty/RMA quality
3. Compatibility
4. AI performance
5. Expandability
6. Dual-GPU capability
7. RAM capacity
8. Cooling
9. Gaming performance
10. Price/value

Established Polish retailers are preferred. Established EU sellers are acceptable when delivered cost, warranty, and RMA remain competitive. Marketplace, grey-market, used, refurbished, and unknown sellers are excluded from primary recommendations.

## Repository layout

- `monitor-config.json`: machine-readable locked targets and rules
- `data/observations.csv`: append-only seller observations
- `reports/YYYY-MM-DD.md`: weekly reports
- `AGENTS.md`: autonomous weekly-run procedure

Reports preserve unavailable fields as `unknown`; they do not invent prices or silently substitute incompatible revisions.

## Monitoring cadence

- Weekly from 9 August through 8 November 2026.
- Daily from 13 November 2026, exactly two weeks before Black Friday, through 26 November 2026.
- Final Black Friday buying report on 27 November 2026.
- Successful monitoring runs commit and push their validated report/data changes to `origin/main`.
