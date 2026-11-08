"""One-time publication of manually reviewed November 8 public-source evidence.
No network, purchases, seller contacts or global-setting changes. Decimal only.
"""
import csv
import json
from datetime import date, timedelta
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAY = '2026-11-08'
q = lambda x: D(x).quantize(D('.01'), rounding=ROUND_HALF_UP)
fmt = lambda x: f'{q(x):,.2f}'
load = lambda path: json.loads(path.read_text(), parse_float=D)
manifest = load(ROOT/f'research/{DAY}-offers.json')
groups = {k:load(ROOT/f'research/{d}{s}-http.json') for k,d,s in [('p',DAY,''),('f',DAY,'-followup'),('s',DAY,'-specs'),('old','2026-11-01','')]}
fx_cap = groups['p'][49]
fx = json.loads(fx_cap['text'],parse_float=D)['rates'][0]
assert fx['effectiveDate']=='2026-11-06' and fx['mid']==D('4.3925')
rate = fx['mid']
offers = {}
for original in manifest['offers'] + manifest['references']:
    x = dict(original)
    group, index = x['capture'].split(':')
    cap = groups[group][int(index)]
    assert cap['retrieved_at'].startswith('2026-11-01' if group=='old' else DAY)
    x['url'] = cap['url']
    x['source_date'] = cap['retrieved_at'][:10]
    x['price'] = None if x['price']=='unknown' else D(x['price'])
    x['pln'] = None if x['price'] is None else q(x['price']*(rate if x['currency']=='EUR' else D(1)))
    if x['seller']=='Morele.net Sp. z o.o.':
        assert 'Sprzedaje i wysyła przedsiębiorca:\nMorele.net\n' in cap['text'], x['id']
    warranty = x.get('warranty','unknown')
    lines = cap.get('text','').splitlines()
    if warranty=='unknown' and 'Warunki gwarancji' in lines:
        window=lines[lines.index('Warunki gwarancji'):][:20]
        if 'Długość' in window and 'Typ gwarancji' in window:
            warranty=window[window.index('Długość')+1]+'; '+window[window.index('Typ gwarancji')+1]
    x['warranty']=warranty
    x.setdefault('vat','gross consumer VAT included')
    x.setdefault('shipping','unknown; selected Poland checkout not established')
    x.setdefault('rma','Poland seller route; exact collection/postage/service quality unknown' if x['country']=='Poland' else 'unknown; Poland cross-border collection/postage not verified')
    offers[x['id']]=x
unit={key:x['pln'] for key,x in offers.items()}
ram=q(offers['ramA']['price']/D('1.19')*D('1.23')*rate)
a_qty={'cpuA':1,'boardA':1,'ramA':1,'gpu':1,'coolA':1,'caseA':1,'psu':1,'ssd':2,'fan140':6,'fan120':6}
b_qty={'cpuB':1,'boardB':1,'ramB':1,'gpu':1,'coolB':1,'caseB':1,'fan140':8,'ssd':1,'ssdB2':1,'psu':1}
a_amounts={key:q((ram if key=='ramA' else unit[key])*n) for key,n in a_qty.items()}
b_amounts={key:q(unit[key]*n) for key,n in b_qty.items()}
a=sum(a_amounts.values()); b1=sum(b_amounts.values()); b2=b1-unit['psu']+unit['b2']; non=a-unit['gpu']
ap=sum(a_amounts[k] for k in ('cpuA','boardA','ramA','coolA','caseA'))
bp=sum(b_amounts[k] for k in ('cpuB','boardB','ramB','coolB','caseB'))
values={'A':a,'A_two':a+unit['gpu'],'C_non_gpu':non,'B1':b1,'B2':b2,'B1_two':b1+unit['gpu'],'platform_A_C':ap,'platform_B':bp,
        'platform_premium':ap-bp,'platform_premium_pct':(ap-bp)/bp*100,'A_over_B1':a-b1,'A_over_B1_pct':(a-b1)/b1*100,
        'A_over_B2':a-b2,'A_over_B2_pct':(a-b2)/b2*100,'cpu_alternative_premium':unit['cpuAlt']-unit['cpuB'],
        'cpu_alternative_premium_pct':(unit['cpuAlt']-unit['cpuB'])/unit['cpuB']*100,'cpuAlt_same_seller_weekly_change':unit['cpuAlt']-D('3951.74'),
        'cpuAlt_same_seller_weekly_pct':(unit['cpuAlt']-D('3951.74'))/D('3951.74')*100,
        'A_value_ram_scenario':a-ram+unit['ramValue'],'A_value_ram_difference':ram-unit['ramValue'],
        'A_fan120_group_reference':unit['fan120']*6,'C_nominal_GPU_heat_W':D(350)*2,'A2_reference_GPU_heat_W':D(575)*2,
        'AW420_stack_mm':D(27)+D(25),'AW420_nominal_margin_mm':D(65)-D(27)-D(25),'AW420_group_current_A':D('.36')*3}
previous=load(ROOT/'research/2026-11-01-calculations.json')
history={}
for track in ('A','B1','B2'):
    points=[dict(x) for x in previous['history'][track]['series']]
    points[-1]['originally_published']=True
    points.append({'date':DAY,'reference_pln':str(q(values[track])),'class':'incomplete heterogeneous product-only reference; PSU historical; never delivered','originally_published':False})
    vals=[D(x['reference_pln']) for x in points]
    windows={}
    for days in (30,90):
        start=date.fromisoformat(DAY)-timedelta(days=days)
        subset=[x for x in points if start<=date.fromisoformat(x['date'])<=date.fromisoformat(DAY)]
        amounts=[D(x['reference_pln']) for x in subset]
        windows[str(days)]={'start':str(start),'observations':len(subset),'first_available':subset[0]['date'],'minimum':str(min(amounts)),'maximum':str(max(amounts)),'change_from_first_available':str(q(vals[-1]-amounts[0]))}
    history[track]={'series':points,'first':str(vals[0]),'previous':str(vals[-2]),'current':str(vals[-1]),'minimum':str(min(vals)),'maximum':str(max(vals)),
                    'weekly_change':str(q(vals[-1]-vals[-2])),'weekly_pct':str(q((vals[-1]-vals[-2])/vals[-2]*100)),
                    'total_change':str(q(vals[-1]-vals[0])),'total_pct':str(q((vals[-1]-vals[0])/vals[0]*100)),'windows':windows,
                    'delivered_qualified_history':'undefined: no complete qualified delivered basket'}
history['C']={'first_observed':'2026-08-23','first_unqualified_reference':'56282.19','previous_current_qualified_total':None,'current_qualified_total':None,'fit_validated_total':None,
              'minimum_qualified_total':None,'maximum_qualified_total':None,'weekly_qualified_change':None,'total_qualified_change':None,
              'previous_non_gpu_reference':previous['results_pln']['C_non_gpu'],'current_non_gpu_reference':str(q(non)),
              'same_water_listing_reference_ask':'13050.00','weekly_reference_ask_change':'0.00','current_pair_ask':'unknown; sold/ended notice conflicts with surviving page',
              '30_day':'No qualifying current or fit-validated pair; Oct18/25 and Nov1 water sticker 13050; availability wording corrected, not a new verified stock loss.',
              '90_day':'Starts Aug23 air pair 7400 then stale; later water bundle is different cooling/condition, never same-offer inflation; no delivered extrema.'}
ledger={'date':DAY,'baseline_commit':manifest['baseline_commit'],'fx':{'eur_pln':str(rate),'effective':'2026-11-06','url':fx_cap['url']},
        'A_quantities':a_qty,'B1_quantities':b_qty,'A_amounts_pln':{k:str(v) for k,v in a_amounts.items()},'B1_amounts_pln':{k:str(v) for k,v in b_amounts.items()},
        'results_pln':{k:str(q(v)) for k,v in values.items()},'RAM_A_german_gross_pln':str(unit['ramA']),'RAM_A_polish_vat_illustration':str(ram),
        'delivered_totals':'unknown','C_current':'incomplete','C_fit_validated':'incomplete','C_savings_A1_A2':'undefined; no qualifying installed matching pair',
        'status':'incomplete product-only references, not purchasing recommendations','history':history,'current_observation_count':len(manifest['offers'])}
L=lambda label,url:f'[{label}]({url})'
price=lambda key,amount=None:L(fmt(unit[key] if amount is None else amount)+' PLN',offers[key]['url'])
R=f'../research/{DAY}-calculations.json'
warning={'ramA':'**No exact stock**; PL-VAT illustration only.','psu':'**2026-11-01 historical Morele-direct reference, not current offer.**','fan120':'**Only two selectable; six-fan group incomplete.**'}
report=f'''# Poland/EU workstation monitor — {DAY}

## Headline and RAM anomaly state

THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.

**WAIT A / WAIT C / WAIT B1 / WAIT B2.** Exact TRX50 AI TOP and ProArt 5090 are visibly **Morele-direct** again. Primary 9950X3D also returned to Morele direct; released 9950X3D2 fell to a repository exact-SKU asking-price low. Factory 4×32 ECC RDIMM remains unqualified/unavailable, B 2×64 RAM rose, and A/C six-fan availability is short. PRIME's Morele main offer is now Madman Gaming, so its last direct price is explicitly historical.

All complete delivered totals **unknown/incomplete**. Product-only, incomplete mixed-evidence references: **A {fmt(a)}; B1 {fmt(b1)}; B2 {fmt(b2)} PLN**. Track C current and fit-validated matching-pair installed totals **incomplete/incomplete**; no stale bundle is added. All tracks stay **128GB**. EUR/PLN **{rate}**, [NBP](https://api.nbp.pl/api/exchangerates/rates/a/eur/2026-11-06/?format=json) effective November 6. Germany-to-Poland RAM VAT adjustment is an illustration, not checkout.

## Table A — complete locked Threadripper / 128GB / one RTX 5090

| Exact component | Qty | Product-only PLN reference | Seller, stock and evidence |
|---|---:|---:|---|
'''
for key,n in a_qty.items():
    x=offers[key]
    report+=f"| {x['product']} `{x['sku']}` | {n} | {price(key,a_amounts[key])} | {x['seller']}; {x['stock']}. {warning.get(key,'')} {x['notes']} |\n"
report+=f'''
**A 128GB one-5090 reference {fmt(a)} PLN; theoretical two-5090 {fmt(a+unit['gpu'])} PLN.** Neither is delivered-qualified or thermally/quantity validated. A/C non-GPU reference **{fmt(non)} PLN**; PSU is historical and six 120mm fans are not available as a full group at the cited offer. No architecture change.

## Table C — complete inherited Threadripper / 128GB / dual used RTX 3090

| Exact component | Qty | Product-only reference | Condition, warranty, geometry and qualification |
|---|---:|---|---|
'''
for key,n in a_qty.items():
    if key=='gpu':continue
    x=offers[key]
    report+=f"| {x['product']} `{x['sku']}` | {n} | {price(key,a_amounts[key])} | Exact A non-GPU part inherited. {x['stock']}. {warning.get(key,'')} |\n"
report+=f'''| Two matching used/refurbished RTX 3090 24GB | 2 | **Current qualified price unknown** | No two cards with simultaneously verified seller, exact model/SKU/revision/cooler geometry/power connectors, ownership, serials, condition, warranty and sustained tests. |
| Prior Zotac Trinity OC Bykski bundle | 2 claimed | {price('pairOld')} **stale/conflicted asking reference, excluded** | Sold/ended notice despite surviving buy panel; same notice already in November 1 capture. Private identity unknown, no serial-linked tests or complete GPU loop. |
| Additional Łódź two-card listing | 2 claimed | {price('pairNew')} **stale/conflicted reference, excluded** | Exact model/SKU/revision/geometry unknown; sold/ended notice, private identity unknown. Not a confirmed matching pair. |
| EVGA XC3 `24G-P5-3975-KR`, Gigabyte Turbo `GV-N3090TURBO-24GD`, ASUS Turbo `TURBO-RTX3090-24G` | 2 optional target | No exact qualifying pair | Slim/blower geometry options only; thickness is not a purchase preference or completion gate. |
| Optional RTX 3090 NVLink bridge | optional | **Excluded from base total** | Generation, card connector position, exact selected motherboard slot spacing, delivered price and workload benefit unresolved. |

**C 128GB current matching-pair installed total: incomplete. Best fit-validated matching-pair installed total: incomplete.** Savings versus A's one-5090 and theoretical two-5090 references **undefined** until a real matching pair plus necessary cooling, power and delivery are priced. No current sticker total is constructed from stale listings or unrelated singles. The nominal **48GB is aggregate physical VRAM across two separate 24GB devices**, not unified memory.

## Table B — complete AM5 / 9950X3D / factory 128GB 2×64 UDIMM

| Exact component | Qty | Product-only PLN reference | Seller, stock and qualification |
|---|---:|---:|---|
'''
for key,n in b_qty.items():
    x=offers[key]
    report+=f"| {x['product']} `{x['sku']}` | {n} | {price(key,b_amounts[key])} | {x['seller']}; {x['stock']}. {warning.get(key,'')} {('B1 only: dual-GPU-power-ready, NOT stock-HAVN chassis-ready.' if key=='psu' else x['notes'])} |\n"
report+=f'''| B2 only: Seasonic VERTEX GX-1200 ATX 3.0 `4711173877721` | 1 | {price('b2')} | Morele direct; one-GPU-only alternative to B1, never additive. Exact monitored ATX 3.0 box/native GPU cable revision remains unverified for recommendation. |

**B1 {fmt(b1)} PLN; B2 {fmt(b2)} PLN**, incomplete product-only references. B1 theoretical two-5090 **{fmt(b1+unit['gpu'])} PLN**, excludes unpriced VGPU removal/conversion hardware and validated dual-card airflow; B2 is one-GPU-only. Released **9950X3D2 Dual Edition `100-100001978WOF` {price('cpuAlt')}** is **{fmt(values['cpu_alternative_premium'])} PLN / {fmt(values['cpu_alternative_premium_pct'])}%** above the primary CPU, same current Morele seller, before unknown freight. Week-on-week same-seller change **{fmt(values['cpuAlt_same_seller_weekly_change'])} PLN / {fmt(values['cpuAlt_same_seller_weekly_pct'])}%**. Cache-sensitive CPU workloads can benefit; no fitting GPU-bound local-AI benchmark justifies automatic substitution. Requires BIOS F8 or newer; latest stable preferred.

## Compact comparison — A, C and B

| Metric | Track A | Track C | Track B |
|---|---|---|---|
| CPU / motherboard | 9960X / TRX50 AI TOP | Exact A | 9950X3D / X870E AORUS MASTER X3D ICE |
| RAM | 128GB factory 4×32 ECC RDIMM | Exact A | 128GB factory 2×64 UDIMM, exact-board QVL pending |
| Case / cooler | Enthoo Elite Server BK02 / AW420 | Exact A | White HAVN HS 420 VGPU / white non-ARGB PANORAMA 360 |
| Case fans, AIO additional | 6×140 + 6×120 | Exact A; 120mm group incomplete | 8×140 |
| Storage | 2×9100 PRO 4TB | Exact A | 9100 PRO 4TB + 990 PRO 4TB |
| PSU | PRIME PX-2200 ATX 3.1 | Exact A | B1 PRIME 2200; B2 VERTEX 1200 ATX 3.0 reference |
| GPU / aggregate physical VRAM | 1×5090 32GB; theoretical 2×5090 64GB separate devices | 2×3090, 48GB across separate 24GB devices | 1×5090 32GB; theoretical B1 pair 64GB separate devices |
| Current delivered total | Unknown; {fmt(a)} incomplete reference | Current / fit-validated incomplete | Unknown; B1 {fmt(b1)} / B2 {fmt(b2)} incomplete references |
| Two-GPU caveat | Slot gap/airflow/cables/reserved cards unvalidated | Matching pair, condition, thermals and exact slot fit unvalidated | CPU-fed PCIe 5.0 **x8/x8, not x16/x16**; stock VGPU not two-GPU-ready; flat bottom bracket absent |

## Platform-only costs, 128GB totals and Threadripper premium

CPU + motherboard + RAM + cooler + case only, **excluding GPU/storage/PSU/fans**: **A=C {fmt(ap)} PLN; B {fmt(bp)} PLN**. Platform premium **{fmt(ap-bp)} PLN / {fmt(values['platform_premium_pct'])}%**. Complete-reference A premium over B1 **{fmt(a-b1)} PLN / {fmt(values['A_over_B1_pct'])}%**; over B2 **{fmt(a-b2)} PLN / {fmt(values['A_over_B2_pct'])}%**. These are incomplete-reference premiums, not delivered checkout differences.

**Weekly decision classification: above 15,000 PLN requires strong justification for Threadripper; WAIT.** The unavailable extreme 128GB RDIMM reference, not a 256GB upgrade, dominates the platform difference. B RAM is also inflated. Hypothetical unavailable Kingston {price('ramValue')} would reduce A's illustration to **{fmt(values['A_value_ram_scenario'])} PLN**, a **{fmt(values['A_value_ram_difference'])} PLN** reduction, but no substitution is made. Locked totals: A128 {fmt(a)} / theoretical {fmt(a+unit['gpu'])}; C128 current/fit incomplete; B128 B1/B2 {fmt(b1)} / {fmt(b2)}. Full delivered A/B/C totals unknown.

## Architecture advantages and compromises

- **Threadripper A/C advantages:** more PCIe connectivity, superior multi-GPU platform, ECC RDIMM, quad-channel memory, higher memory capacity and stronger long-term expansion. Compromises: higher platform price/power, expensive/unavailable matched RDIMM and larger chassis.
- **AM5 advantages:** lower platform price/power, better gaming-focused CPU, cheaper motherboard/RAM/case, a white showcase design and substantial 128GB capacity.
- **AM5 compromises:** dual-channel memory, 128GB preferred configuration, x8/x8 electrical dual GPU, fewer PCIe lanes, chipset/USB4 M.2 sharing, weaker 256GB+ expansion, and selected HAVN VGPU chassis not two-GPU-ready in stock layout.
- **Track C advantages:** Threadripper PCIe/expansion platform, potential lower acquisition cost, 48GB aggregate physical VRAM, and one application-distributed model or two independent 24GB workloads.
- **Track C compromises:** used-card condition and warranty risk, separate VRAM devices, multi-GPU software/communication overhead, approximately 700W GPU heat, older Ampere Tensor/RT/media features, and incomplete fit-validated matching-pair evidence.
- **Capacity versus latency versus throughput:** 1×5090 gives one 32GB device and simpler execution. 2×3090 gives two 24GB devices, nominal {fmt(values['C_nominal_GPU_heat_W'])}W GPU heat; theoretical 2×5090 gives two 32GB devices, roughly {fmt(values['A2_reference_GPU_heat_W'])}W at the 575W/card reference, not measured ProArt consumption. Larger distributed capacity requires runtime model/tensor/pipeline/layer splitting; independent jobs may improve throughput without improving one-request latency. Neither VRAM nor bandwidth is transparently combined. NVLink is optional transport, not memory pooling.

## Independent price history and fake-discount checks

Dates ascending, PLN. This is **not a delivered-qualified price series**: references mix dates, availability, FX, sellers and sometimes historical inputs. August Senetic gross and delivered fields are unreliable as corrected below. Missing runs are missing observations. October 18/25 were unpublished local drafts recovered in the November 1 publication, not successful earlier pushes.

| Track | First reference | Previous Nov 1 | Current reference | Min / max reference | Weekly change | First-to-current change |
|---|---:|---:|---:|---|---|---|
'''
for track in ('A','B1','B2'):
    h=history[track]
    report+=f"| {track} | {fmt(h['first'])} Aug 9 | {fmt(h['previous'])} | {fmt(h['current'])} | {fmt(h['minimum'])} / {fmt(h['maximum'])} | {fmt(h['weekly_change'])} / {fmt(h['weekly_pct'])}% | {fmt(h['total_change'])} / {fmt(h['total_pct'])}% |\n"
report+='| C | 56,282.19 Aug 23 unqualified air-pair reference | Qualified installed total absent | Current / fit incomplete | Qualified min/max undefined | Qualified change undefined | Qualified total change undefined |\n\n'
for track in ('A','B1','B2'):
    report+=f'- **{track} 30/90-day context:** '
    parts=[]
    for days,w in history[track]['windows'].items():
        parts.append(f"{days} days from {w['start']}: {w['observations']} dated references; first available {w['first_available']}; min/max {fmt(w['minimum'])}/{fmt(w['maximum'])}; change from first available {fmt(w['change_from_first_available'])} PLN")
    report+='; '.join(parts)+'. Delivered-qualified extrema/deltas undefined.\n'
report+='- **C independently:** '+history['C']['30_day']+' '+history['C']['90_day']+' Same water-page retained sticker is unchanged, but is not a verified current pair asking price. The ended-notice correction is not proof of newly lost stock.\n\n'
report+=(ROOT/f'research/{DAY}-findings.md').read_text()
report+='\n## Current warranty, seller and delivery ledger\n\n| Exact offer | Advertised warranty / handler | RMA and delivery |\n|---|---|---|\n'
for key in ('cpuA','boardA','ramA','gpu','coolA','caseA','psu','ssd','fan140','fan120','cpuB','boardB','ramB','coolB','caseB','b2','ssdB2','cpuAlt','pairOld','prebuilt'):
    x=offers[key]
    report+=f"| {L(x['product'],x['url'])} | {x['seller']}; {x['warranty']} | {x['rma']}; {x['shipping']}; delivered **unknown**. Source date {x['source_date']}. |\n"
report+=f'\n## Publication validation\n\n[Seller/offer ledger](../research/{DAY}-offers.json), [Decimal/history ledger](../research/{DAY}-calculations.json), [primary captures](../research/{DAY}-http.json), [follow-up](../research/{DAY}-followup-http.json), [specification attempts](../research/{DAY}-specs-http.json), [discovery log](../research/{DAY}-search-log.json), [validation](../research/{DAY}-validation.json). Publication requires the dated validator, parser tests, JSON/CSV/arithmetic/link checks and `git diff --check`. Remote retrieval failures remain recorded, never asserted healthy or interpreted as stock absence.\n'

report_path=ROOT/f'reports/{DAY}.md'
ledger_path=ROOT/f'research/{DAY}-calculations.json'
assert not report_path.exists() and not ledger_path.exists(), 'One-time publisher refuses overwrite'
csv_path=ROOT/'data/observations.csv'
assert not any(r.get('observed_at')==DAY for r in csv.DictReader(csv_path.open()))
readme_path=ROOT/'README.md'
old=readme_path.read_text()
archive=old[old.index('## November 1 current evidence matrix'):].replace('## November 1 current evidence matrix — exact 128GB targets','## November 1 archived evidence matrix — NOT CURRENT',1)
archive=archive.replace('## Separate Mac Studio current comparison — not A/B/C','## Separate Mac Studio November 1 archived comparison — NOT CURRENT',1)
readme=f'''# Three-track RTX 5090 / dual RTX 3090 workstation price monitor

Weekly Poland/EU monitoring through Black Friday 2026. A/C remain Threadripper; B remains AM5. All locked current capacities **128GB**.

Latest: **[{DAY} report](reports/{DAY}.md)**; [Decimal/history](research/{DAY}-calculations.json), [seller ledger](research/{DAY}-offers.json), [capture evidence](research/{DAY}-http.json).

**THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY. All tracks WAIT.** Complete delivered totals unknown. A **[{fmt(a)} PLN incomplete reference](reports/{DAY}.md)**; C **[current/fit-validated incomplete](reports/{DAY}.md)**; B1 **[{fmt(b1)} PLN incomplete reference](reports/{DAY}.md)**; B2 **[{fmt(b2)} PLN incomplete reference](reports/{DAY}.md)**. TRX50 AI TOP / ProArt / primary CPU are Morele direct again; PRIME main offer is third-party; factory RDIMM and A/C six-fan group still block completion.

## November 8 current evidence matrix — exact 128GB tracks

All amounts are product-only references, never selected delivered costs. Each component price links to its direct product page; totals link to the dated report. C inherits every A non-GPU row. B1/B2 are distinct PSU cases, never additive.

| Component | Track A / C non-GPU | Track B |
|---|---|---|
'''
for label,ak,bk in [('CPU','cpuA','cpuB'),('Motherboard','boardA','boardB'),('Factory 128GB RAM','ramA','ramB'),('Cooler','coolA','coolB'),('Case','caseA','caseB')]:
    av=price(ak,ram if ak=='ramA' else None)
    if ak=='ramA':av+=' **No exact stock**; PL-VAT illustration; exact factory 4×32 RDIMM'
    if ak=='caseA':av+=' French gross conversion; Poland checkout unknown'
    bv=price(bk)+('; exact-board QVL pending' if bk=='ramB' else '')
    readme+=f'| {label} | {av} | {bv} |\n'
readme+=f'''| GPU | A {price('gpu')} Morele direct; C **no qualifying current pair** ([exact used targets](reports/{DAY}.md#table-c--complete-inherited-threadripper--128gb--dual-used-rtx-3090)) | {price('gpu')} same ProArt |
| PSU | {price('psu')} **November 1 historical direct reference**, current Morele seller unqualified | B1 {price('psu')} same historical PRIME; B2 {price('b2')} VERTEX ATX 3.0 reference, native lead pending |
| Storage | {price('ssd',unit['ssd']*2)} two 9100 PRO | {price('ssd')} 9100 + {price('ssdB2')} 990 PRO |
| Fans | {price('fan140',unit['fan140']*6)} six 140 + {price('fan120',unit['fan120']*6)} six 120 reference; **only two 120 selectable** | {price('fan140',unit['fan140']*8)} eight 140 |
| Platform CPU+board+RAM+cooler+case | [{fmt(ap)} PLN incomplete](reports/{DAY}.md) A=C | [{fmt(bp)} PLN incomplete](reports/{DAY}.md) |
| Current complete delivered total | A [unknown; {fmt(a)} PLN reference](reports/{DAY}.md); C [current/fit incomplete](reports/{DAY}.md) | B1 [unknown; {fmt(b1)} PLN reference](reports/{DAY}.md); B2 [unknown; {fmt(b2)} PLN reference](reports/{DAY}.md) |
| Theoretical two 5090 | [{fmt(a+unit['gpu'])} PLN unvalidated](reports/{DAY}.md) | B1 [{fmt(b1+unit['gpu'])} PLN unvalidated](reports/{DAY}.md); stock VGPU not ready; B2 one GPU only |
| Distinct CPU alternative | Not installed; architectures locked | 9950X3D2 {price('cpuAlt')}, [{fmt(values['cpu_alternative_premium'])} PLN / {fmt(values['cpu_alternative_premium_pct'])}% premium](reports/{DAY}.md), no automatic substitution |

C 48GB is aggregate physical VRAM across separate devices, not unified. B CPU-fed pair is **x8/x8**, not x16/x16; stock VGPU is one-card oriented and lacks the flat standard bottom bracket. C prior water bundle has a sold/ended notice already present November 1: **availability wording corrected**, not a newly verified stock loss. No stale pair is included in totals.

## Separate Mac Studio current comparison — outside A/B/C

No 86GB option: **96GB probable intended RAM capacity, pending confirmation**. Exact M5 Ultra 30CPU/64GPU/96GB/1TB and 36CPU/80GPU/256GB/1TB Apple standard and Poland Education configured totals remain **unknown**. [iSpot exact 36/80/256GB/1TB 54,499.00 PLN](https://ispot.pl/apple-mac-studio-36-rdzeniowy-procesor-apple-m5-ultra-gpu-80-rdzeni-ram-256gb-dysk-1-tb) is unchanged, **2–8 weeks / on order**, not immediate stock. Education eligibility for this buyer unknown; unified RAM is not CUDA VRAM. [Current separate comparison](reports/{DAY}.md#separate-mac-studio-comparison).

'''
# All construction and source gates complete before append-only publication writes.
ledger_path.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
report_path.write_text(report)
with csv_path.open('a',newline='') as out:
    writer=csv.writer(out,lineterminator='\n')
    for item in manifest['offers']:
        x=offers[item['id']]
        writer.writerow([DAY,'Track '+x['track']+' '+x['category'],x['product'],x['sku'],x['seller'],x['country'],
                         'unknown' if x['price'] is None else str(q(x['price'])),x['currency'],'unknown' if x['pln'] is None else str(x['pln']),
                         x['vat'],x['shipping'],'unknown',x['stock'],x['warranty'],x['rma'],x['url'],x['notes']+' Capture '+x['capture']+'; product-only, not delivered.'])
readme_path.write_text(readme+archive)
print(json.dumps({'appended_rows':len(manifest['offers']),'results':{k:str(q(v)) for k,v in values.items()},'report':str(report_path)},indent=2))
