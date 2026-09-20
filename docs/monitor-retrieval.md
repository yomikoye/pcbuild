# Monitor retrieval, evidence and recovery

## Read-only collection preflight

Read AGENTS.md, monitor-config.json, all observations and latest report before research. Work from the repository root explicitly; do not assume a previous terminal call changed the next call's working directory.

The configured native search backend supports discovery but not `web_extract`. Do not repeatedly invoke unsupported extraction, change global backends, alter approval/security settings or install browser dependencies as part of this project.

Tested on 2026-09-20:

1. Use an explicit, reviewable JSON array of public HTTPS source URLs under `research/YYYY-MM-DD-urls.json` (write_file). No credentials, authenticated pages or private endpoints.
2. Run `python3 -m unittest discover -s tests -v`.
3. Run `python3 scripts/collect_evidence.py research/YYYY-MM-DD-urls.json research/YYYY-MM-DD-http.json` through the normal terminal tool. This calls ordinary curl GET with finite time/size limits and parses product JSON-LD plus visible HTML text using the already-installed BeautifulSoup package. Output must not exist: choose a distinct suffix for a second batch. The script does not choose offers, mutate CSV, touch git, contact sellers or buy anything.
4. Inspect HTTP status, final URL, errors, product identity, visible text and JSON-LD. HTTP 200 alone is not extraction success: a CAPTCHA, category redirect, login or empty product list is not a product offer. Per-URL failures are retained and do not imply stock absence.
5. Search exact SKU, manufacturer/QVL, direct retail and comparison/specialist paths. Blocked requests remain unknown; research alternative public sources without circumventing access controls. A unavailable browser environment is an evidence limitation, not permission to fix global npm/cache ownership.

## Approval boundaries

This workflow is not an approval allowlist. The ordinary terminal policy remains in force. If any command is flagged, leave it unexecuted and request the specific approval. Do not rewrite, split, encode, move into a script, delegate or route a blocked operation through another tool to evade the decision. In an unattended run, persist an honest blocker and stop the blocked operation; do not disable approvals. Preflight of today's interactive session does not prove unattended approval.

The failed September run's inline Python invocation required approval; a separate plain curl request succeeded. A recovery follow-up command was flagged because its URL-matching regular expression was interpreted as an invalid hostname; that command was left unexecuted when approval was not received. Prefer explicit URL manifests for reviewability, not as a workaround for a pending denial. No global/security changes are required or authorized.

## Mandatory interpretation gates

- Morele JSON-LD can name `Morele.net Sp. z o.o.` while the visible **Sprzedaje i wysyła przedsiębiorca** field identifies another merchant. Record the visible contracting seller. Exclude unknown marketplace businesses from A/B primary totals; record them only as unqualified leads. Do not inherit Morele direct shipping/return terms for those merchants.
- Senetic JSON-LD can contain the **net** price. Read the visible `netto`/`brutto` labels; totals use gross. Preserve source amounts and record an explicit correction rather than applying net as VAT-inclusive. Do not retrospectively invent the gross price on old dates without old page evidence.
- Price-valid-until and InStock metadata are evidence, not a reservation. Compare visible purchase/availability controls. For marketplaces, verify exact seller, exact card pair/quantity and condition; never multiply a single-card offer into a qualifying pair.
- An unfinished two-card listing with a placeholder about differing card codes does not prove a matching pair. Its advertised bundle price may be recorded, but current and fit-validated Track C totals remain incomplete; exclude an unpriced mandatory custom loop and NVLink from any claim of a complete installed cost.
- Unknown shipping means `delivered_pln=unknown`, not product price. A shipping range starting at zero is not confirmed free delivery. Preserve old rows; explain historical fields that used product-only amounts under delivered_pln.
- Date every retained reference. Failed/missing weekly runs are missing observations, not unchanged prices. Calculate change since the previous observation separately from unavailable seven-day change. Never carry a stale pair into a current total.

## Publication and verification

Keep raw collection and search evidence plus bounded research notes under research/. Do not include credentials, cookies or entire private session transcripts. Compute amounts with Decimal and retain a machine-readable dated calculation ledger. Cross-check source amounts, quantities, tax assumptions and input dates before using totals.

Before publishing: validate all JSON, fixed-width CSV rows, append-only historical prefix, calculation ledger, all report sections, README clickable prices and local links; classify remote links as fetched, blocked, indexed or historical rather than asserting all are healthy. Run parser tests and `git diff --check`; inspect the full changed-path list. No BUY NOW without the compatibility/seller gates in AGENTS.md. Commit/push main only after the completed research/report passes validation. Verify `git ls-remote origin refs/heads/main` equals local HEAD; distinguish command success from remote verification. A failed Git attempt is not a successful publication.

For the September 20 recovery, `python3 scripts/validate_monitor.py ea60a1402d27dde57c116df27dfc441e2a0b7c75` revalidates the dated snapshot against its pre-recovery commit. The validator and `publish_2026_09_20.py` contain date-specific expectations; they are not a generic future-run generator. The one-time publisher refuses to replace its existing report or append duplicate dated rows. Future runs must create their own dated calculation/report artifacts and adapt validation to their actual baseline. When saving validator stdout into a JSON ledger, parse that output separately with `python3 -m json.tool`; the validator excludes its own potentially open output file from the input scan.

Cron changes use supported cron tools/CLI only. Change only the monitor prompt if necessary, preserving existing schedule, repeat counters, enable/paused state, delivery, workdir and skills. Do not create jobs or recursively schedule work. Scheduler last_status=ok indicates the agent returned, not that the market report was completed and pushed.
