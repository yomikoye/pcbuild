"""Publish the inspected 2026-11-01 snapshot; never authorizes a purchase.

One-time append-only publisher. Source offers contain manual visible-seller/VAT decisions.
Uses Decimal, checks source identities, preserves pre-existing observations and archived matrices.
"""
import csv
import json
import re
from datetime import date, timedelta
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAY = '2026-11-01'
q = lambda n: D(n).quantize(D('.01'), rounding=ROUND_HALF_UP)
fmt = lambda n: f'{q(n):,.2f}'
raw = json.loads((ROOT/f'research/{DAY}-offers.json').read_text())
groups = {k: json.loads((ROOT/f'research/{DAY}{suffix}-http.json').read_text(), parse_float=D)
          for k, suffix in [('p',''),('f','-followup'),('s','-specs')]}
fx_item = groups['p'][48]
fx = json.loads(fx_item['text'], parse_float=D)['rates'][0]
assert fx['effectiveDate']=='2026-10-30'
rate = D(str(fx['mid']))
assert rate == D('4.3955')
offers = {}
for source in raw['offers']:
    x = dict(source)
    group, index = x['capture'].split(':')
    capture = groups[group][int(index)]
    assert capture['retrieved_at'].startswith(DAY)
    x['url'] = capture['url']
    x['http'] = capture.get('http', '')
    x['price'] = None if x['price']=='unknown' else D(x['price'])
    # The expired NL advertisement deliberately retains a dated asking-price reference, not live stock.
    if x['price'] is not None:
        assert x['http'].startswith('200 ') or x['id']=='pairNL', x['id']
    identity = capture.get('text','') + json.dumps(capture.get('products',[]), default=str)
    if x['id']=='gpu':
        assert '4711636502351' in identity and '90YV0P00-M0NA00' in identity
    elif x['id'] not in ('pairNL','pairC','gpuKR'):
        assert x['sku'] in identity or x['product'] in identity, x['id']
    if x['seller']=='Morele.net Sp. z o.o.':
        assert 'Sprzedaje i wysyła przedsiębiorca:\nMorele.net\n' in capture['text'], x['id']
    warranty = x.get('warranty','unknown')
    lines = capture.get('text','').splitlines()
    if warranty=='unknown' and 'Warunki gwarancji' in lines:
        w = lines[lines.index('Warunki gwarancji'):][:20]
        if 'Długość' in w and 'Typ gwarancji' in w:
            warranty = w[w.index('Długość')+1]+'; '+w[w.index('Typ gwarancji')+1]+'; current visible term'
    x['warranty'] = warranty
    x['vat'] = x.get('vat', 'gross consumer VAT included')
    x['shipping'] = x.get('shipping','unknown; selected checkout not established')
    x['delivered'] = 'unknown'
    x['rma'] = x.get('rma', 'Poland seller location; RMA route/quality and collection unknown' if x['country']=='Poland' else 'unknown')
    x['pln'] = None if x['price'] is None else q(x['price']*(rate if x['currency']=='EUR' else D(1)))
    offers[x['id']] = x

unit = {k: x['pln'] for k,x in offers.items()}
ram = q(offers['ramA']['price']/D('1.19')*D('1.23')*rate)
a_qty = {'cpuA':1,'boardA':1,'ramA':1,'gpu':1,'coolA':1,'caseA':1,'psu':1,'ssdA':2,'fan140':6,'fan120':6}
b_qty = {'cpuB':1,'boardB':1,'ramB':1,'gpu':1,'coolB':1,'caseB':1,'fan140':8,'ssdB':1,'ssdB2':1,'psu':1}
a_amounts = {k:q((ram if k=='ramA' else unit[k])*n) for k,n in a_qty.items()}
b_amounts = {k:q(unit[k]*n) for k,n in b_qty.items()}
a = sum(a_amounts.values()); non = a-unit['gpu']; b1 = sum(b_amounts.values()); b2=b1-unit['psu']+unit['b2']
ap = sum(a_amounts[k] for k in ('cpuA','boardA','ramA','coolA','caseA'))
bp = sum(b_amounts[k] for k in ('cpuB','boardB','ramB','coolB','caseB'))
values = {'A':a,'A_two':a+unit['gpu'],'C_non_gpu':non,'C_unqualified_stickers_no_loop':non+unit['pairC'],
          'B1':b1,'B2':b2,'B1_two':b1+unit['gpu'],'platform_A_C':ap,'platform_B':bp,
          'platform_premium':ap-bp,'platform_premium_pct':(ap-bp)/bp*100,
          'A_over_B1':a-b1,'A_over_B1_pct':(a-b1)/b1*100,'A_over_B2':a-b2,'A_over_B2_pct':(a-b2)/b2*100,
          'cpu_alternative_premium':unit['cpuAlt']-unit['cpuB'],
          'cpu_alternative_premium_pct':(unit['cpuAlt']-unit['cpuB'])/unit['cpuB']*100,
          'marketplace_gpu_surcharge':unit['gpuMarket']-unit['gpu'],
          'marketplace_gpu_surcharge_pct':(unit['gpuMarket']-unit['gpu'])/unit['gpu']*100,
          'C_unqualified_gpu_sticker_difference_A1':unit['gpu']-unit['pairC'],
          'C_unqualified_gpu_sticker_difference_A2':unit['gpu']*2-unit['pairC'],
          'A_value_ram_scenario':a-ram+unit['ramValue'],'A_value_ram_potential_difference':ram-unit['ramValue'],
          'AW420_stack_mm':D(27)+D(25),'AW420_stack_nominal_margin_mm':D(65)-D(27)-D(25),
          'AW420_three_fan_current_A':D('.36')*3,
          'gpu_heat_C_nominal_W':D(350)*2,'gpu_heat_A2_reference_W':D(575)*2}
# Historical reference figures are explicitly heterogeneous, never qualified delivered totals.
historical = {
 'A':[('2026-08-09','70348.67'),('2026-08-16','70545.48'),('2026-08-23','69881.19'),('2026-08-30','70312.19'),('2026-09-20','80026.53'),('2026-09-27','83611.84'),('2026-10-04','83834.04'),('2026-10-11','87907.57'),('2026-10-18','88358.50'),('2026-10-25','88705.37')],
 'B1':[('2026-08-09','47196.41'),('2026-08-16','48340.64'),('2026-08-23','48002.29'),('2026-08-30','48316.17'),('2026-09-20','56621.60'),('2026-09-27','58846.81'),('2026-10-04','60359.79'),('2026-10-11','63612.08'),('2026-10-18','65749.01'),('2026-10-25','65957.39')],
 'B2':[('2026-08-09','46025.26'),('2026-08-16','47184.06'),('2026-08-23','46855.99'),('2026-08-30','47100.84'),('2026-09-20','55119.32'),('2026-09-27','57539.14'),('2026-10-04','58829.43'),('2026-10-11','62383.41'),('2026-10-18','64303.96'),('2026-10-25','64512.34')]
}
history = {}
for track, series in historical.items():
    for when, amount in series:
        assert fmt(D(amount)) in (ROOT/f'reports/{when}.md').read_text(), (track,when,amount)
    points=[{'date':when,'reference_pln':amount,'class':'historical heterogeneous incomplete reference',
             'originally_published':when not in ('2026-10-18','2026-10-25')} for when,amount in series]
    points.append({'date':DAY,'reference_pln':str(q(values[track])),'class':'conditional reference; unavailable RAM/board or unapproved seller; not delivered','originally_published':False})
    ds=[D(p['reference_pln']) for p in points]
    today=date.fromisoformat(DAY)
    windows={}
    for days in (30,90):
        start=today-timedelta(days=days)
        subset=[p for p in points if start<=date.fromisoformat(p['date'])<=today]
        vals=[D(p['reference_pln']) for p in subset]
        windows[str(days)]={'start':str(start),'observations':len(subset),'first_available':subset[0]['date'],
                           'minimum_reference_pln':str(min(vals)),'maximum_reference_pln':str(max(vals)),
                           'change_from_first_available_pln':str(q(ds[-1]-vals[0]))}
    history[track]={'series':points,'first':series[0][1],'previous':series[-1][1],
                    'minimum_reference':str(min(ds)),'maximum_reference':str(max(ds)),
                    'weekly_reference_change':str(q(ds[-1]-ds[-2])),
                    'weekly_reference_pct':str(q((ds[-1]-ds[-2])/ds[-2]*100)),
                    'first_to_current_reference_change':str(q(ds[-1]-ds[0])),
                    'first_to_current_reference_pct':str(q((ds[-1]-ds[0])/ds[0]*100)),
                    'qualified_delivered_min_max_and_changes':'undefined; no complete qualified delivered basket',
                    'windows':windows}
history['C']={'first_date':'2026-08-23','first_unqualified_reference':'56282.19',
 'previous_qualified_total':None,'current_qualified_total':None,'fit_validated_total':None,
 'qualified_minimum':None,'qualified_maximum':None,'weekly_qualified_change':None,'total_qualified_change':None,
 'previous_unqualified_hardware_no_loop':'67809.53','current_unqualified_hardware_no_loop':str(q(non+unit['pairC'])),
 'same_listing_asking_series':[{'date':d,'pln':p} for d,p in [('2026-09-27','13150.00'),('2026-10-18','13050.00'),('2026-10-25','13050.00'),(DAY,'13050.00')]],
 'weekly_same_listing_ask_change':'0.00','first_same_listing_ask_change':'-100.00',
 '30_day':'same water-block listing 13050 in Oct 18/25 and Nov 1; Oct 4/11 not independently live-priced; no qualifying pair',
 '90_day':'Aug 23 air-pair lead 7400 stale; water bundle is different condition/cooling, not a market price rise; all complete qualified totals missing'}
ledger = {'date':DAY,'baseline_commit':raw['baseline_commit'],'fx':{'eur_pln':str(rate),'effective':'2026-10-30','url':fx_item['url']},
 'status':'conditional, product-only references; every delivered A/B/C total unknown',
 'A_quantities':a_qty,'B1_quantities':b_qty,'A_amounts_pln':{k:str(v) for k,v in a_amounts.items()},
 'B1_amounts_pln':{k:str(v) for k,v in b_amounts.items()},'B2_psu_amount_pln':str(unit['b2']),
 'ram_A_german_gross_pln':str(unit['ramA']),'ram_A_illustrative_polish_vat_pln':str(ram),
 'results_pln':{k:str(q(v)) for k,v in values.items()},'C_current':'incomplete','C_fit_validated':'incomplete',
 'C_qualified_savings_A1_A2':'undefined','delivered_totals':'unknown','history':history,'observation_count':len(offers)}

L = lambda label,url:f'[{label}]({url})'
price = lambda k,amount=None:L(fmt(unit[k] if amount is None else amount)+' PLN',offers[k]['url'])
report_path=ROOT/f'reports/{DAY}.md'
ledger_path=ROOT/f'research/{DAY}-calculations.json'
assert not report_path.exists() and not ledger_path.exists(), 'One-time publisher refuses overwrite'
rows=[]
for x in offers.values():
    rows.append([DAY,'Track '+x['track']+' '+x['category'],x['product'],x['sku'],x['seller'],x['country'],
                 str(q(x['price'])) if x['price'] is not None else 'unknown',x['currency'],
                 str(x['pln']) if x['pln'] is not None else 'unknown',x['vat'],x['shipping'],'unknown',
                 x['stock'],x['warranty'],x['rma'],x['url'],x['notes']+' Capture '+x['capture']+'; product-only; selected delivered cost unknown.'])
csv_path=ROOT/'data/observations.csv'
assert not any(r[0]==DAY for r in csv.reader(csv_path.open(newline='')))

heading = f'''# Poland/EU workstation monitor — {DAY}

## Headline and RAM anomaly state

**THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.** **WAIT A / WAIT C / WAIT B1 / WAIT B2.** TRX50 AI TOP is again **OutOfStock**; G5/T5 factory 4×32GB RDIMM remains unavailable. The white HAVN VGPU has returned to visible **Morele-direct** stock, but the manufacturer explicitly excludes the flat standard bottom fan bracket; hardware needed for a horizontal-layout conversion remains unvalidated. ProArt has a new {price('gpu')} PrimePC direct lead, not yet an approved established-seller recommendation; the old KR page remains generic.

Current complete delivered totals: **unknown/incomplete for all tracks**. Conditional product-only references, not purchasable baskets: **A {fmt(a)}; B1 {fmt(b1)}; B2 {fmt(b2)} PLN**. C current/fit-validated pair **incomplete/incomplete**. All capacities remain **128GB**. EUR/PLN **{rate}**, NBP effective 2026-10-30. German-to-Polish RAM VAT conversion is an illustration, never checkout. [Raw primary evidence](../research/{DAY}-http.json), [follow-up](../research/{DAY}-followup-http.json), [specifications](../research/{DAY}-specs-http.json), [reviewed seller ledger](../research/{DAY}-offers.json), [Decimal/history ledger](../research/{DAY}-calculations.json).

## Table A — complete locked Threadripper / 128GB / one RTX 5090

| Exact component | Qty | Product-only PLN reference | Seller / stock / qualification |
|---|---:|---:|---|
'''
for k,n in a_qty.items():
    x=offers[k]
    warning=' **No exact stock; illustrative Polish 23% VAT, not checkout.**' if k=='ramA' else (' **No exact stock; catalogue reference.**' if k=='boardA' else (' **Conditional seller lead, not approved purchase.**' if k=='gpu' else ''))
    heading += f"| {x['product']} `{x['sku']}` | {n} | {price(k,a_amounts[k])} | {x['seller']}; {x['stock']}.{warning} {x['notes']} |\n"
heading += f'''
**A one 5090 {L(fmt(a)+' PLN incomplete reference','../research/'+DAY+'-calculations.json')}; theoretical two 5090 {fmt(a+unit['gpu'])} PLN, not quantity/fit-validated.** A/C non-GPU reference **{fmt(non)} PLN**. Senetic's exact two-drive quantity is priced rather than doubling Morele's last single SSD. The second 5090 is arithmetic only despite a three-item seller stock label.

## Table C — complete Track A platform plus two matching used RTX 3090

| Exact component/state | Qty | Product-only reference | Pair, warranty and geometry evidence |
|---|---:|---|---|
| Every A non-GPU row above: 9960X, TRX50 AI TOP, factory 4×32 ECC RDIMM, AW420, BK02 Server, PX-2200, two 9100 PRO, 6×140+6×120 | A quantities | {L(fmt(non)+' PLN incomplete non-GPU reference','../research/'+DAY+'-calculations.json')} | Full A architecture inherited without AM5 substitution; no purchasable RDIMM/board demonstrated. |
| Two advertised Zotac Trinity OC `ZT-A30900J-10P` with Bykski blocks | 2 claimed | {price('pairC')} | Private seller name unknown; live buy panel, not a verified matching pair. Individual revision/SKU, serial/ownership/invoice, warranty/returns, mining/liquid/repair/pad history, core/hotspot/memory-junction temperatures, VRAM and 30-minute CUDA tests unknown. Unfilled code/test/original-cooler placeholders. Mandatory GPU loop absent/unpriced. |
| Fusion PCs/Siedo Gigabyte Vision OC multiunit lead | quantity unverified | {price('pairNL')} per-card **expired reference**, not a pair | HTTP 410 / VERLOPEN; gaming-only seven-day warranty explicitly excludes AI/mining. Reject, independent of thickness. No Poland delivery/test proof. |
| [EVGA XC3 24G-P5-3975-KR](https://www.newegg.com/evga-xc3-24g-p5-3975-kr-geforce-rtx-3090-24gb-graphics-card-triple-fans/p/N82E16814487524), [Gigabyte Turbo GV-N3090TURBO-24GD](https://www.gigabyte.com/Graphics-Card/GV-N3090TURBO-24GD), ASUS Turbo TURBO-RTX3090-24G | 2 target | No exact qualifying pair | Slim and blower geometry options only, **not requirements**. Thick matching open-air cards remain eligible with measured electrical-slot spacing, meaningful intake gap and sustained cooling evidence. |
| [RTX 3090 NVLink bridge reference](https://www.ceneo.pl/91191409) | optional | **Excluded from base total** | Exact generation, slot spacing, connector placement, delivered price and application benefit unresolved. |

**C 128GB current matching-pair installed total: incomplete. Best fit-validated matching-pair installed total: incomplete.** The sum **{fmt(non+unit['pairC'])} PLN** is only unqualified hardware sticker arithmetic, excludes compulsory custom GPU loop/insured delivery/tests, and is **not a complete C total**. Qualified installed savings versus A one/two 5090 are **undefined**. Unqualified GPU-only sticker differences **{fmt(unit['gpu']-unit['pairC'])} / {fmt(unit['gpu']*2-unit['pairC'])} PLN** are not installed savings. Never combine unrelated singles or multiply an expired offer into a pair.

## Table B — complete AM5 / 9950X3D / factory 2×64GB, separate B1/B2

| Exact component | Qty | Product-only PLN reference | Seller / stock / qualification |
|---|---:|---:|---|
'''
for k,n in b_qty.items():
    x=offers[k]
    note = 'B1 only: dual-GPU-power-ready, NOT stock-HAVN chassis-ready.' if k=='psu' else x['notes']
    heading += f"| {x['product']} `{x['sku']}` | {n} | {price(k,b_amounts[k])} | {x['seller']}; {x['stock']}. {note} |\n"
heading += f"| B2 only: VERTEX GX-1200 `VERTEX-GX-1200 ATX 3.0 PCIe 5.0` | 1 | {price('b2')} | Morele direct; ATX 3.0 exact EAN 4711173877721. One GPU only; native lead revision unverified. Never add to B1. |\n"
heading += f'''
**B1 {fmt(b1)} PLN; B2 {fmt(b2)} PLN**, conditional incomplete product-only references. B1 theoretical two ProArts **{fmt(b1+unit['gpu'])} PLN**, excludes unpriced chassis conversion/bracket and thermal validation. B2 is one-GPU-only. Released **9950X3D2 `100-100001978WOF` {price('cpuAlt')}** has a current gross-price premium of **{fmt(values['cpu_alternative_premium'])} PLN / {fmt(values['cpu_alternative_premium_pct'])}%** versus Senetic's primary CPU. Sellers differ; shipping-adjusted premium unknown. Cache-sensitive CPU jobs may benefit; no workload evidence justifies the premium for GPU-bound local AI. Never auto-substitute; BIOS F8+ (latest stable preferred).

## Compact comparison — A, C and B

| Metric | Track A | Track C | Track B |
|---|---|---|---|
| CPU / board | 9960X / TRX50 AI TOP | same exact A | 9950X3D / X870E AORUS MASTER X3D ICE |
| RAM | 128GB factory 4×32 ECC RDIMM | same exact A | 128GB factory 2×64 UDIMM; QVL unresolved |
| Case / cooler | Enthoo Elite **Server BK02** / AW420 | same exact A | white HAVN HS 420 **VGPU** / white non-ARGB PANORAMA 360 |
| Case fans (AIO fans additional) | 6×140 + 6×120 | same exact A | 8×140 |
| Storage | 2×9100 PRO 4TB | same exact A | 9100 PRO 4TB + 990 PRO 4TB |
| PSU | PRIME PX-2200 ATX 3.1 | same exact A | B1 PRIME 2200; B2 VERTEX 1200 ATX 3.0 reference |
| GPU / aggregate physical VRAM | 1×5090: 32GB; theoretical 2: 64GB across devices | 2×used 3090: **48GB across two separate 24GB devices** | 1×5090: 32GB; theoretical B1 2: 64GB across devices |
| Current delivered total | **incomplete**, {fmt(a)} reference | **incomplete current / fit-validated pair** | **incomplete**, B1 {fmt(b1)} / B2 {fmt(b2)} reference |
| Two-GPU caveat | second card, actual slot gap, airflow and cables unvalidated | matching cards/condition, cooling loop or safe air intake unvalidated | CPU-fed PCIe 5.0 **x8/x8, not x16/x16**; remove VGPU assembly; flat bottom bracket not included; two horizontal ProArts not airflow-safe default |

## Platform-only costs, 128GB totals and Threadripper premium

CPU + motherboard + RAM + cooler + case only (**exclude GPU, storage, PSU and fans**): **A=C {fmt(ap)} PLN**, **B {fmt(bp)} PLN**. A/C platform premium **{fmt(ap-bp)} PLN / {fmt(values['platform_premium_pct'])}%**. Complete-reference premium A over B1 **{fmt(a-b1)} PLN / {fmt(values['A_over_B1_pct'])}%**; over B2 **{fmt(a-b2)} PLN / {fmt(values['A_over_B2_pct'])}%**. These are conditional references, not delivered market premiums.

**Decision classification: above 15,000 PLN requires strong Threadripper justification; WAIT.** Unavailable RDIMM dominates A/C, not a 256GB upgrade. B RAM is also inflated. The unavailable {price('ramValue')} Kingston factory 4×32 kit would reduce A's illustration to **{fmt(values['A_value_ram_scenario'])} PLN**, a **{fmt(values['A_value_ram_potential_difference'])} PLN** difference, but it is only an unavailable/unvalidated value scenario, **never the official current total**. A 128GB one/two-5090 references {fmt(a)} / {fmt(a+unit['gpu'])}; C current/fit total incomplete/incomplete; B128 B1/B2 {fmt(b1)} / {fmt(b2)}.

## Architecture advantages and compromises

- **Threadripper A/C:** more PCIe connectivity, superior multi-GPU platform, ECC RDIMM, quad-channel memory, higher memory capacity and stronger long-term expansion. Higher platform price/power and poor matched-RDIMM availability are the compromise.
- **AM5 B:** lower platform price/power, better gaming-focused CPU, cheaper motherboard/RAM/case, white showcase design and substantial 128GB capacity. Compromises: dual-channel memory, 128GB preferred configuration, x8/x8 electrical dual GPU, fewer PCIe lanes, chipset/USB4 M.2 sharing, weaker 256GB+ expansion, and the selected HAVN VGPU chassis is not two-GPU-ready in stock layout.
- **Track C:** Threadripper PCIe/expansion platform, potential lower acquisition cost, 48GB aggregate physical VRAM, one application-distributed model or two independent 24GB workloads. Compromises: used-card condition/warranty risk, separate VRAM devices, multi-GPU software/communication overhead, approximately 700W GPU heat, older Ampere Tensor/RT/media features, and incomplete fit-validated matching-pair evidence.
- **Capacity ≠ latency ≠ throughput:** 1×5090 offers 32GB on one device and simpler execution; 2×3090 offers two 24GB devices (48GB aggregate), nominal {fmt(values['gpu_heat_C_nominal_W'])}W heat. Theoretical 2×5090 offers 64GB aggregate and roughly {fmt(values['gpu_heat_A2_reference_W'])}W GPU board-power reference using 575W/card, not a measured ProArt setup. Neither pair transparently unifies VRAM or adds per-device bandwidth into one memory system. Distributed-model capacity requires model/tensor/pipeline/layer splitting supported by the actual runtime; otherwise run independent jobs. NVLink may speed peer transport, not create a transparent 48GB device. No universal speed ranking without same-model/context/quantisation benchmarks.

## Independent price history and fake-discount checks

Dates ascending; PLN. Every number below is a **heterogeneous historical product-only illustration**, not a delivered-qualified price series. Original August Senetic gross/delivered claims remain unreliable and explicitly excluded from true landed-price history. October 18/25 were pre-existing **unpublished local drafts** at preflight (remote main ended October 11); they are retained as collected evidence, not prior successful publications. Missing September runs are missing observations, not unchanged weeks.

| Track | First reference/date | Previous collected Oct 25 | Current reference | Min / max reference | 7-day reference change | First-to-current reference change |
|---|---|---:|---:|---|---|---|
'''
for track,h in history.items():
    if track=='C':continue
    heading += f"| {track} | {fmt(D(h['first']))} / Aug 9 | {fmt(D(h['previous']))} | {fmt(values[track])} | {fmt(D(h['minimum_reference']))} / {fmt(D(h['maximum_reference']))} | {fmt(D(h['weekly_reference_change']))} / {fmt(D(h['weekly_reference_pct']))}% | {fmt(D(h['first_to_current_reference_change']))} / {fmt(D(h['first_to_current_reference_pct']))}% |\n"
heading += '| C | 56,282.19 / Aug 23 **unqualified air-pair illustration** | installed incomplete | installed / fit incomplete | qualified min/max undefined | qualified change undefined; same water listing ask unchanged | qualified total change undefined; cannot compare expired air pair with water blocks |\n\n'
for track in ('A','B1','B2'):
    h=history[track]
    heading += f"- **{track} 30/90-day context:** "
    parts=[]
    for days in ('30','90'):
        w=h['windows'][days]
        parts.append(f"{days} days from {w['start']}: {w['observations']} dated references, first available {w['first_available']}, reference min/max {fmt(D(w['minimum_reference_pln']))}/{fmt(D(w['maximum_reference_pln']))}, change from first available {fmt(D(w['change_from_first_available_pln']))} PLN")
    heading += '; '.join(parts)+'. Qualified delivered extrema/change remain undefined.\n'
heading += '\n- **C independently:** 30-day current water listing stayed 13,050 on Oct 18/25 and Nov 1; Oct 4/11 live-price evidence missing. Ninety-day history starts Aug 23, not August 3: 7,400 air-pair lead became stale; later water-block bundle is different condition/cooling and not evidence of market-wide price inflation. No current matched, fit-validated pair or qualified installed savings. The water listing fell 100 PLN from Sep 27 then stayed unchanged; never a qualified bargain.\n\n'
heading += (ROOT/f'research/{DAY}-findings.md').read_text()
# Concrete source-derived warranty/RMA ledger closes the report.
heading += '\n## Current warranty and delivery ledger\n\n| Exact offer | Warranty/handler | RMA and selected delivery |\n|---|---|---|\n'
for k in ('cpuA','boardA','ramA','gpu','coolA','caseA','psu','ssdA','fan140','fan120','cpuB','boardB','ramB','coolB','caseB','b2','ssdB','ssdB2','pairC'):
    x=offers[k]
    heading+=f"| {L(x['product'],x['url'])} | {x['warranty']} | {x['rma']}; shipping: {x['shipping']}; delivered PLN **unknown** |\n"
heading += '\nNo unsupported warranty/service-quality rating is inferred from the marketplace host, schema seller or price. Evidence establishes advertised terms, not measured service quality.\n'

# Persist only after every source/arithmetic/report construction above succeeded.
ledger_path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n')
with csv_path.open('a',newline='') as stream:
    csv.writer(stream, lineterminator='\n').writerows(rows)
report_path.write_text(heading)
readme_path=ROOT/'README.md'
old=readme_path.read_text()
archive=old[old.index('## October 25 current evidence matrix'):]
archive=archive.replace('## October 25 current evidence matrix — exact 128GB targets','## October 25 archived evidence matrix — NOT CURRENT (unpublished draft recovered November 1)',1)
archive=archive.replace('## October 18 current evidence matrix — 128GB exact locked targets (ARCHIVED, NOT CURRENT)','## October 18 archived evidence matrix — NOT CURRENT (unpublished draft recovered November 1)',1)
readme=f'''# Three-track RTX 5090 / dual RTX 3090 workstation price monitor

Weekly Poland/EU monitoring through Black Friday 2026. Locked **128GB** builds remain separate: A Threadripper/RTX 5090; C complete A non-GPU platform plus two matching used 3090; B AM5/5090 with separate B1/B2 PSUs.

Latest: **[{DAY} report](reports/{DAY}.md)**; [Decimal/history ledger](research/{DAY}-calculations.json), [seller ledger](research/{DAY}-offers.json), [primary](research/{DAY}-http.json), [follow-up](research/{DAY}-followup-http.json), [specifications](research/{DAY}-specs-http.json).

**THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.** All tracks **WAIT**. Current delivered totals **unknown/incomplete**; reference-only A **[{fmt(a)} PLN](reports/{DAY}.md)**, B1 **[{fmt(b1)} PLN](reports/{DAY}.md)**, B2 **[{fmt(b2)} PLN](reports/{DAY}.md)**. C installed/current and fit-validated matching-pair totals **[incomplete](reports/{DAY}.md)**. Board stock lost again; factory 4×32 RDIMM unavailable; white HAVN now Morele direct. New ProArt PrimePC lead is conditional, not an approved purchase. HAVN VGPU omits the standard flat bottom bracket; horizontal-conversion hardware and airflow remain **unvalidated**.

## November 1 current evidence matrix — exact 128GB targets

All component amounts link directly to the corresponding seller product page. **Product-only references**, never delivered; no exact stock means no complete purchasable basket. C inherits every A non-GPU row. B1/B2 are alternatives, not additive.

| Component | A / C non-GPU | B |
|---|---|---|
'''
for label,ak,bk in [('CPU','cpuA','cpuB'),('Motherboard','boardA','boardB'),('Factory 128GB RAM','ramA','ramB'),('Cooler','coolA','coolB'),('Case','caseA','caseB')]:
    av=price(ak,ram if ak=='ramA' else None); bv=price(bk)
    if ak in ('boardA','ramA'):av += ' **No exact stock**; '+('illustrative PL VAT' if ak=='ramA' else 'catalogue only')
    if bk=='ramB':bv+='; exact-board QVL pending'
    if ak=='caseA':av+='; French-VAT EUR reference converted to PLN; Poland checkout unknown'
    readme += f'| {label} | {av} | {bv} |\n'
readme+=f'''| GPU | A {price('gpu')} conditional PrimePC lead; C {price('pairC')} private water-block ask **not a qualified pair** | {price('gpu')} conditional lead, same exact ProArt |
| PSU | {price('psu')} PRIME PX-2200 ATX 3.1 | B1 {price('psu')}; B2 {price('b2')} VERTEX GX-1200 **ATX 3.0**, native lead pending |
| Storage | {price('ssdA',a_amounts['ssdA'])} two 9100 PRO / Senetic visible quantity | {price('ssdB')} one 9100 + {price('ssdB2')} one 990 PRO |
| Case fans | {price('fan140',a_amounts['fan140'])} six 140 + {price('fan120',a_amounts['fan120'])} six 120 | {price('fan140',b_amounts['fan140'])} eight 140 |
| Platform CPU+board+RAM+cooler+case | [{fmt(ap)} PLN incomplete](reports/{DAY}.md) A=C | [{fmt(bp)} PLN incomplete](reports/{DAY}.md) |
| Current delivered total | A [unknown; {fmt(a)} PLN reference](reports/{DAY}.md); C [current/fit incomplete](reports/{DAY}.md) | B1 [unknown; {fmt(b1)} PLN reference](reports/{DAY}.md); B2 [unknown; {fmt(b2)} PLN reference](reports/{DAY}.md) |
| Theoretical two 5090 | [{fmt(a+unit['gpu'])} PLN unvalidated](reports/{DAY}.md); C optional NVLink excluded | B1 [{fmt(b1+unit['gpu'])} PLN unvalidated](reports/{DAY}.md); stock VGPU not ready; B2 one GPU |

C 48GB is aggregate physical VRAM across separate devices, never unified. B CPU-fed pair is **x8/x8**, never x16/x16. All warranty, seller, exact-fit, M.2 and 30/90-day independent history gates are in the [report](reports/{DAY}.md). October 18/25 below were unpublished local drafts at this run's preflight, not previously pushed reports.

## Separate Mac Studio current comparison — not A/B/C

No 86GB RAM option; **96GB probable intended capacity, pending confirmation**. Exact M5 Ultra 30CPU/64GPU/96GB/1TB and 36CPU/80GPU/256GB/1TB Apple standard/Poland Education configured prices remain **unknown**, not derived from starting prices. A separately sourced [iSpot exact 36/80/256GB/1TB **54,499.00 PLN** retail quote](https://ispot.pl/apple-mac-studio-36-rdzeniowy-procesor-apple-m5-ultra-gpu-80-rdzeni-ram-256gb-dysk-1-tb) shows **2–8 weeks** dispatch, not immediate stock despite schema. Education price unknown, buyer eligibility unknown; [Apple eligibility policy](https://www.apple.com/legal/sales-support/sales-policies/education_pl.html) retrieved. Unified Mac RAM is not CUDA VRAM. See [current Mac evidence](reports/{DAY}.md#separate-mac-studio-comparison).

'''
readme_path.write_text(readme+archive)
print(json.dumps({'date':DAY,'appended_rows':len(rows),'results':{k:fmt(v) for k,v in values.items()},'report':str(report_path)},indent=2))
