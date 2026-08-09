# Dual-track workstation monitor procedure

Run a complete, evidence-based Poland/EU price check for both locked workstation tracks in `monitor-config.json`. Never merge the tracks or silently substitute one architecture for the other.

1. Read `monitor-config.json`, the latest report in `reports/`, and all `data/observations.csv` rows before researching.
2. Research Track A Threadripper and Track B AM5 independently. Preserve separate price histories, totals, availability findings and recommendation classes.
3. Search exact SKUs first. Use established Polish sellers, then established EU sellers that ship to Poland. Record the actual contracting seller, not a marketplace host. A zero-result native search is not completion: also search manufacturer configurators/QVLs, retailer site search, comparison sites, EAN/MPN variants, structured product data, reputable workstation-memory specialists, and direct-page/Jina extraction. Try at least three independent discovery paths before concluding that no qualifying offer exists.
4. For every observation capture track, date, category, exact product/SKU, seller/legal seller, country, gross price/currency, PLN conversion, VAT status, shipping, total delivered PLN, stock wording, warranty length/handler, RMA route/quality, direct URL and evidence notes. Prefix categories with `Track A` or `Track B`; shared exact GPU/PSU prices may be referenced by both totals.
5. Append evidence-backed rows to `data/observations.csv`; never overwrite historical observations. Correct demonstrably false baseline data explicitly and explain the correction. Unknown values remain `unknown`.
6. Reject incompatible near matches, especially: Enthoo Elite vs Enthoo Elite Server; `BK02` vs `BK03`; UDIMM vs RDIMM; incorrectly matched RAM; or oversized GPUs without physical analysis. For the Seasonic PSU, `PRIME-PX-2200-ATX30` / EAN `4711173878414` is the required ATX 3.1 product; verify against Seasonic and exact EAN rather than inferring from the suffix.
7. Track A RAM procedure:
   - The locked current capacity is 128GB. Aggressively search factory-matched 4x32GB ECC RDIMM kits from G.Skill T5/G5 Neo, Kingston workstation families, Micron, Samsung and reputable EU workstation-memory suppliers.
   - Do not include 256GB RAM in the current Track A total. Track 256GB only as a future upgrade reference.
   - Do not recommend irrationally priced individual modules merely because they are listed.
   - Separate modules are eligible only when bought together from one reputable seller with identical manufacturer SKU, revision, rank, speed, timings, voltage and preferably batch, plus QVL/vendor validation and full stability testing.
   - If extreme RAM pricing dominates the result, print exactly: `THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.`
8. Track B CPU procedure: 9950X3D remains primary. Monitor the distinct released 9950X3D2 Dual Edition `100-100001978WOF`; report its exact premium and workload value but never substitute it automatically.
9. Track B RAM procedure: use a factory-matched 128GB 2x64GB DDR5 UDIMM kit as primary. Prefer exact GIGABYTE X870E AORUS MASTER X3D ICE QVL or memory-vendor validation at DDR5-5600 or stable DDR5-6000 EXPO. Stability outranks memory overclocking. Track 256GB only as a non-default experiment.
10. Track B lane procedure: with Ryzen 9000, the two CPU-fed GPU slots on X870E AORUS MASTER X3D ICE operate PCIe 5.0 x8/x8, not x16/x16. M.2 does not reduce that GPU pair. Put the 9100 PRO in `M2A_CPU` and the 990 PRO in `M2C_SB`; `M2B_CPU` shares bandwidth with ASMedia USB4, `M2D_SB` disables chipset `PCIEX4`, and `M2E_SB` is PCIe 4.0 x2.
11. Track B case/cooling procedure: monitor exact white HAVN HS 420 VGPU `HVN-CA-HS420-07` and white non-ARGB TRYX PANORAMA 360 `L-P360N-DS3M-G1W`. Mount the 55mm AIO stack at the top as exhaust. Treat the stock VGPU layout as one-GPU-oriented: a second GPU requires removal of the VGPU assembly and two horizontal cards; two ProArt cards are not an airflow-safe default.
12. Track B PSU procedure: calculate B1 with PRIME PX-2200 as dual-GPU-power-ready but explicitly not chassis-ready in the stock HAVN VGPU layout. Calculate B2 with a separate high-quality one-GPU-only 1200W–1600W PSU. Never mix B1 and B2. Verify exact ATX revision and native GPU cable before recommendation.
13. Audit CPU/BIOS, exact memory QVL, case/motherboard/AIO/PSU/GPU dimensions, radiator-plus-fan thickness, slot spacing/lane allocation, M.2 placement, native 12V-2x6 leads, safe bend radius, EU mains requirements, fan groups, GPU support and dual-GPU airflow before any BUY NOW recommendation. The 9950X3D2 requires BIOS F8 or newer on the selected GIGABYTE board; prefer the latest stable BIOS.
14. Calculate only evidence-backed totals. If an exact required component is unavailable, mark the total provisional/incomplete and identify the reference price used; never hide a non-matching revision inside a compatible total.
15. Every weekly report must contain, in this order:
   - headline and RAM anomaly state;
   - Table A: complete Threadripper workstation prices;
   - Table B: complete AM5 value workstation prices, including B1 and B2 PSU totals;
   - a compact `Metric | Threadripper | AM5 | Difference` comparison covering CPU, motherboard, RAM, case, cooler, case fans, storage, PSU, RTX 5090, one-GPU total and theoretical two-GPU hardware total with the Track B chassis warning;
   - platform-only costs for CPU + motherboard + RAM + cooler + case, excluding GPU/storage/PSU;
   - Track A 128GB total and Track B 128GB B1/B2 totals;
   - Threadripper premium in PLN and percent, with the weekly decision classification and an explanation of what drives it;
   - architecture advantages/compromises;
   - detailed observations, recommendation classes, compatibility/warranty findings and evidence limitations.
16. The architecture comparison must always state:
   - Threadripper advantages: more PCIe connectivity, superior multi-GPU platform, ECC RDIMM, quad-channel memory, higher memory capacity and stronger long-term expansion.
   - AM5 advantages: lower platform price/power, better gaming-focused CPU, cheaper motherboard/RAM/case, a white showcase design, and substantial 128GB capacity.
   - AM5 compromises: dual-channel memory, 128GB preferred configuration, x8/x8 electrical dual GPU, fewer PCIe lanes, chipset/USB4 M.2 sharing, weaker 256GB+ expansion, and a selected HAVN VGPU chassis that is not two-GPU-ready in its stock layout.
17. Maintain first observed, previous, minimum, maximum, weekly change, total change and 30/90-day context independently for each track. Detect fake discounts against repository history.
18. Track a comparable full prebuilt with whole-system warranty. Require exact CPU, motherboard, RAM, GPU, PSU, cooling, storage, VAT, delivery and cross-border collection/RMA details.
19. Update both README price matrices. Every displayed component price must be a Markdown link directly to the retailer product page so the numeric price is clickable on GitHub. Link unavailable exact targets to manufacturer/configurator evidence and totals to the corresponding report. Do not leave a bare `—`; state `No exact stock` and the exact validated target or non-matching reference.
20. Validate JSON/CSV syntax and all arithmetic, run `git diff --check`, then commit completed report/data/README/config changes to `main` and push to `origin/main`. Never push a partial or failed report.
21. After a successful GitHub push, notify the originating Telegram thread only for a meaningful change: component price/delivered-cost change, historical low, stock change, new qualifying seller, warranty/RMA change, compatibility finding, relevant launch, prebuilt comparison change or recommendation-class change. Include headline figures, what changed, alerts, report path and commit. If nothing meaningful changed, begin the final response exactly `[SILENT]`.

Neither track may claim two GPUs automatically provide unified VRAM. Track B must never be presented as x16/x16 dual GPU, and Track A must never be silently reduced to a conventional gaming build.
