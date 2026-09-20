"""One-time recovery artifact builder from reviewed, persisted public evidence.
No network, scheduler or Git writes. Refuses repeat publication; preserves CSV prefix.
"""
import csv
import io
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-09-20'
D = Decimal

def money(x):
    return str(D(str(x)).quantize(D('.01'), rounding=ROUND_HALF_UP))

def fmt(x):
    return f'{D(str(x)):,.2f}'

def load(name):
    return json.loads((ROOT / 'research' / name).read_text())

raw = load(DATE+'-http.json')
verify = load(DATE+'-verification-http.json')
follow = load(DATE+'-followup-http.json')
old_bytes = (ROOT/'data/observations.csv').read_bytes()
old = list(csv.DictReader(io.StringIO(old_bytes.decode())))
assert not any(r['observed_at'] == DATE for r in old), 'Already appended'
assert not (ROOT/'reports'/f'{DATE}.md').exists(), 'Already published'
fields = list(old[0])
new = []

def observation(category, product, sku, seller, country, price, currency, pln, stock, url,
                notes, vat='included', shipping='unknown', warranty='unknown', rma='unknown', delivered='unknown'):
    row = dict(zip(fields, [DATE,category,product,sku,seller,country,str(price),currency,str(pln),vat,shipping,delivered,stock,warranty,rma,url,notes]))
    new.append(row)
    return row

def direct(i, category, warranty='unknown', extra=''):
    r=raw[i]; p=r['products'][0]; o=p['offers']; assert isinstance(o,dict)
    seller = 'Morele.net Sp. z o.o.'
    if i==2: seller='Madman Gaming Sp. z o.o.; reputation/terms unverified'
    if i==3: seller='kubartech; legal identity/reputation unverified'
    historical=next((h for h in reversed(old) if h['source_url']==r['url']),None)
    sku=p.get('mpn') or (historical['sku'] if historical else 'unknown')
    return observation(category,p['name'],sku,seller,'Poland' if i not in [2,3] else 'unknown',money(o['price']),'PLN',money(o['price']),o['availability'].split('/')[-1],r['url'],
        f'Direct HTML plus JSON-LD; visible contracting seller checked; research/{DATE}-http.json index {i}. '+extra,
        shipping='PL structured 0-25.99 PLN; selected cost unknown' if i not in [2,3] else 'unknown; host metadata not seller terms',
        warranty=warranty,rma='local seller mail route; 14-day consumer return metadata, customer-paid postage; service quality unmeasured' if i not in [2,3] else 'unknown')

entries={}
for key,i,cat,w,extra in [
 ('cpu_unqualified',3,'Track A CPU unqualified marketplace lead','unknown','Excluded from primary current prices; do not call Morele direct.'),
 ('boardA',5,'Track A Motherboard','unknown','Shared with C.'),
 ('coolA',6,'Track A CPU cooler','unknown','Last unit shown; shared with C.'),
 ('fan140',8,'Track A Fan 140mm','6 years manufacturer (historical; term not revalidated)','Unit price; six A/C or eight B; quantities not reserved.'),
 ('fan120',9,'Track A Fan 120mm','6 years manufacturer','Unit price; six A/C; quantity not reserved.'),
 ('psu',11,'Track A PSU','12 years manufacturer (historical; verify exact offer)','Last unit; EAN 4711173878414; shared C/B1. ATX30 suffix does not mean ATX 3.0.'),
 ('ram_value',1,'Track A RAM matched 128GB value alternative','lifetime manufacturer','Out of stock; exact-board kit row pending; not substituted.'),
 ('ramB',17,'Track B RAM 128GB','duration unknown; manufacturer handling via Morele','Exact-board QVL still pending.'),
 ('cpuB',18,'Track B CPU','unknown','Primary unchanged.'),
 ('boardB',19,'Track B Motherboard','unknown','Exact selected board; no architecture change.'),
 ('cpuB2',20,'Track B CPU alternative','unknown','Not substituted; BIOS F8 or newer required.'),
 ('coolB',21,'Track B CPU cooler','historical TRYX 6 years cooler/2 display; reconfirm','Exact white non-ARGB SKU; top exhaust.'),
 ('psuB2',26,'Track B PSU B2 one-GPU-only','unknown','Exact listing remains ATX 3.0 EAN 4711173877721; supplied native GPU cable must be verified.'),
 ('caseB',27,'Track B Case','unknown','Exact HVN-CA-HS420-07; stock VGPU is one-card-only.'),
 ('gpu_unqualified',2,'Track A GPU unqualified marketplace lead','unknown','Shared B lead; excluded from primary totals; not Morele direct.')]:
    entries[key]=direct(i,cat,w,extra)

fx=D(json.loads(verify[0]['text'])['rates'][0]['mid'])
for key,index,sku in [('ramA',4,'F5-6000R3036G32GQ4-G5N'),('ramT5',2,'F5-6400R3239F32GQ4-T5N')]:
    r=verify[index];p=r['products'][0];o=p['offers'];eur=D(o['price']);pln=money(eur*fx);plvat=money(eur/D('1.19')*D('1.23')*fx)
    entries[key]=observation('Track A RAM matched 128GB '+('reference' if key=='ramA' else 'alternative'),p['name'],sku,'ALTERNATE GmbH','Germany',money(eur),'EUR',pln,o['availability'],r['url'],
        f'Exact factory 4x32 ECC RDIMM; current direct retailer proof; illustrative PL 23% VAT amount {plvat} PLN; NBP 2026-09-18 EUR/PLN {fx}. Not destination checkout; no substitution. Board QVL historical, not freshly reproduced.',
        vat='German displayed VAT; PL adjustment illustrative',shipping='7.99 EUR applies DE only; PL unknown',warranty='unknown',rma='30-day mail return metadata DE only; PL route/cost unknown')

r=follow[3];p=r['products'][0]
entries['gpu']=observation('Track A GPU shared Track B',p['name'],'PROART-RTX5090-O32G','Komputronik S.A.','Poland','28490.00','PLN','28490.00','InStock; add to basket; dispatch usually 1 business day from store',r['url'],
    'Direct price/MPN/stock/free delivery/3-year seller service visible. New seller-specific baseline, not same-offer increase from old Euro lead; quantity two not verified.',shipping='free delivery shown; destination checkout not submitted',warranty='3 years seller service',rma='Polish seller service; collection/postage terms and service quality unknown',delivered='28490.00')
r=follow[10];p=r['products'][0]
entries['ssd']=observation('Track A SSD shared Track B',p['name'],'MZ-VAP4T0BW','Morele.net Sp. z o.o.','Poland','3946.06','PLN','3946.06','InStock; last units; selector shows up to three',r['url'],
    'Visible seller Morele authorized; unit gross price. A/C two, B one; no reservation. Cheaper alternative-seller teaser 3899 not accepted without identity.',shipping='PL structured 0-25.99 PLN; selected cost unknown',warranty='5 years/TBW manufacturer limit historical; offer term unverified',rma='local mail; 14-day consumer return metadata; customer-paid postage')
r=raw[7]
observation('Track A SSD VAT correction shared Track B','Samsung 9100 PRO 4TB','MZ-VAP4T0BW','Senetic S.A.','Poland','4038.20','PLN','4038.20','3 units visible',r['url'],
    'Visible 3283.09 PLN NET and 4038.20 PLN GROSS. JSON-LD is net: do not label VAT-included. Old 2026-08 rows claiming included VAT from JSON-LD are not reliable gross evidence; retained unchanged, not retroactively inflated without archived pages.',warranty='5 years/TBW historical; reconfirm',rma='local seller; terms/quality unverified')
r=raw[24]
entries['ssdB']=observation('Track B SSD secondary','Samsung 990 PRO 4TB','MZ-V9P4T0BW','KR System','Poland','3058.37','PLN','3058.37','InStock; dispatch 48h visible',r['url'],
    'Visible 3058.37 gross / 2486.48 net; M2C_SB. Shipping not revalidated; old from-10.99 reference is not current checkout.',warranty='60 months visible; TBW limit historical',rma='local seller route; service quality unknown')
for idx,cat,sku in [(8,'Track A Motherboard alternative','90MB1FZ0-M0EAY0')]:
    r=verify[idx];p=r['products'][0];o=p['offers']
    observation(cat,p['name'],sku,'Morele.net Sp. z o.o.','Poland',money(o['price']),'PLN',money(o['price']),'InStock; last units',r['url'],'No automatic substitution; exact CPU BIOS/slot topology and QVL would need audit.')
for idx,cat,sku in [(8,'Track B PSU alternative','VERTEX PX-1200 ATX 3.0 PCIe 5.0'),(9,'Track A optional AMD GPU','W7900 AI TOP 48G')]:
    r=follow[idx];p=r['products'][0];o=p['offers']
    observation(cat,p['name'],sku,'Morele.net Sp. z o.o. (catalogue)','Poland',money(o['price']),'PLN',money(o['price']),'OutOfStock',r['url'],'No substitution. PSU remains ATX 3.0, not searched 3.1. AMD GPU requires workload ecosystem review.' if idx==8 else 'Optional 48GB AMD card; not CUDA-compatible replacement; excluded from locked totals.')
for i,cat,product,sku in [(4,'Track A Case','Phanteks Enthoo Elite Server','PH-ES916E_BK02'),(22,'Track B comparable prebuilt','NYXUM Workstation 9950X3D 128GB RTX 5090 FE 4TB','NW1')]:
    r=raw[i]
    observation(cat,product,sku,'Caseking GmbH' if i==4 else 'x-kom sp. z o.o.','Germany' if i==4 else 'Poland','unknown','EUR' if i==4 else 'PLN','unknown','unknown; HTTP 403',r['url'],'No current stock or price inferred. Historical report reference explicitly dated in report.',vat='unknown')
observation('Track C GPU advertised bundle','Two Zotac RTX 3090 Trinity OC with Bykski blocks','ZT-A30900J-10P advertised; matching revision unverified','private seller; identity unknown','Poland','13150.00','PLN','13150.00','Kup teraz; advertised two-card bundle, not purchase-qualified',raw[16]['url'],
    'No matching-pair total: SKU-difference placeholder; serials/ownership/mining/repairs/thermal/VRAM/CUDA tests unknown. Original coolers unresolved. Full custom loop absent/unpriced; NVLink explicitly excluded. See dated Track C note.',vat='unknown; private sale',shipping='10.49 locker / 10.95 InPost / 17 courier shown; insured selected total unknown',warranty='unknown; no withdrawal right shown',rma='private sale; unknown; in-person test required')
observation('Track C GPU old air-pair recheck','Zotac RTX 3090 air pair','unknown','unknown','unknown','unknown','PLN','unknown','unknown; HTTP 403',raw[10]['url'],'7400 PLN and HTTP 410 belong to prior August evidence, not today. No live stock inferred.',vat='unknown')
r=verify[3]
observation('Track C GPU refurbisher single reference','Zotac RTX 3090 Trinity OC refurbished','unknown','Pixel2Point; proprietor Wolfgang Lentner','Germany','1089.99','EUR',money(D('1089.99')*fx),'Ausverkauft; sold out',r['url'],
    'One card only; never doubled into pair. Pads/paste/ultrasonic cleaning and multi-hour FurMark/3DMark are seller claims, not serial-specific CUDA/VRAM/temperature reports. Legal notice independently fetched.',vat='VAT exempt under German small-business rule section 19',shipping='DE free; other countries only if checkout offers; PL unknown',warranty='12 months Gewaehrleistung; not independently a commercial warranty',rma='German seller; PL return route/cost unknown')
observation('Track C optional NVLink','RTX 3090 NVLink bridge','unknown','unknown','unknown','unknown','PLN','unknown','unknown; Ceneo challenge',raw[14]['url'],'Excluded; generation/slot spacing/card connector alignment/current price/application benefit unknown; does not unify VRAM.',vat='unknown')
r=verify[1]
observation('Track A RAM specialist single lead','PHS 32GB DDR5-5600 ECC RDIMM 2Rx8 1.1V','SP598864','PHS-electronic GmbH','Germany','1677.90','EUR',money(D('1677.90')*fx),'immediately available; identical four unverified',r['url'],
    'Exact board compatibility promised only for this supplier part. Not factory matched; original OEM SKU/revision/batch/timings unknown. Four-unit arithmetic EUR 6711.60 is not qualifying kit; no substitution.',vat='German displayed VAT',warranty='5 years supplier',rma='Germany; compatibility/money-back claim; PL freight unknown')
r=follow[4]
observation('Track A GPU EU backorder shared B','ASUS ProArt RTX 5090 OC 32GB','PROART-RTX5090-O32G','LDLC; exact contracting entity to confirm','France','5899.95','EUR',money(D('5899.95')*fx),'BackOrder; 7 days / 22 Sep shown (inconsistent relative date)',r['url'],
    'Destination VAT/shipping/stock date not confirmed; no replacement of in-stock PL source.',vat='displayed consumer VAT; PL checkout unknown',warranty='2 years seller commercial warranty',rma='cross-border postage/collection unknown')

# Reviewed inputs: A historical CPU/case remain explicit; GPU now has a current direct seller.
inputs={}
def inp(key,name,amount,url,state,date=DATE,qtyA=0,qtyB=0):
    inputs[key]={'name':name,'unit_pln':money(amount),'source_url':url,'source_date':date,'state':state,'qtyA':qtyA,'qtyB':qtyB}
    return inputs[key]
def e(key,name,qa=0,qb=0,state='current direct offer; delivery/compatibility gates remain'):
    r=entries[key];return inp(key,name,r['pln_price'],r['source_url'],state,qtyA=qa,qtyB=qb)
hcpu=next(r for r in old if r['observed_at']=='2026-08-30' and r['category']=='Track A CPU')
hcase=next(r for r in old if r['observed_at']=='2026-08-09' and r['sku']=='PH-ES916E_BK02')
inp('cpuA','Threadripper 9960X 100-100001595WOF',hcpu['pln_price'],hcpu['source_url'],'HISTORICAL prior seller attribution not revalidated; current marketplace excluded','2026-08-30',1)
e('boardA','Gigabyte TRX50 AI TOP',1)
r=entries['ramA'];inp('ramA','G.Skill 128GB 4x32 F5-6000R3036G32GQ4-G5N',D(r['price'])/D('1.19')*D('1.23')*fx,r['source_url'],'current non-stock reference; illustrative PL VAT; shipping unknown',qtyA=1)
e('gpu','ASUS ProArt PROART-RTX5090-O32G 32GB',1,1,'current Komputronik direct offer; free delivery shown; qty two not verified')
e('coolA','Thermaltake AW420 CL-W445-PL14BL-A',1)
inp('caseA','Phanteks Enthoo Elite Server PH-ES916E_BK02',hcase['pln_price'],hcase['source_url'],'HISTORICAL displayed-VAT reference; current 403; destination VAT/shipping unknown','2026-08-09',1)
e('psu','Seasonic PRIME PX-2200 ATX 3.1 / PRIME-PX-2200-ATX30',1,1)
e('ssd','Samsung 9100 PRO 4TB MZ-VAP4T0BW',2,1)
e('fan140','Noctua NF-A14x25 G2 PWM chromax.black',6,8)
e('fan120','Noctua NF-A12x25 G2 PWM chromax.black',6)
e('cpuB','Ryzen 9 9950X3D 100-100000719WOF',0,1)
e('boardB','GIGABYTE X870E AORUS MASTER X3D ICE',0,1)
e('ramB','Kingston 128GB 2x64 KF556C40BBK2-128',0,1)
e('coolB','TRYX PANORAMA 360 White L-P360N-DS3M-G1W',0,1)
e('caseB','HAVN HS 420 VGPU White HVN-CA-HS420-07',0,1)
e('ssdB','Samsung 990 PRO 4TB MZ-V9P4T0BW',0,1)
e('psuB2','Seasonic VERTEX-GX-1200 ATX 3.0',0,0,'B2 replaces PRIME only; one GPU; exact cable verification pending')

v=lambda k:D(inputs[k]['unit_pln'])
A=sum(v(k)*x['qtyA'] for k,x in inputs.items())
B1=sum(v(k)*x['qtyB'] for k,x in inputs.items())
B2=B1-v('psu')+v('psuB2')
PA=sum(v(k) for k in ['cpuA','boardA','ramA','coolA','caseA'])
PB=sum(v(k) for k in ['cpuB','boardB','ramB','coolB','caseB'])
calc={'fx_eur_pln':str(fx),'fx_date':'2026-09-18','inputs':inputs,'totals':{k:money(x) for k,x in {
'A_reference':A,'A_theoretical_two_gpu':A+v('gpu'),'A_C_non_gpu_reference':A-v('gpu'),'B1':B1,'B2':B2,'B1_theoretical_two_gpu':B1+v('gpu'),'platform_A_C':PA,'platform_B':PB,'A_premium_B1':A-B1,'A_premium_B2':A-B2,'A_premium_B1_percent':(A/B1-1)*100,'A_premium_B2_percent':(A/B2-1)*100,'platform_premium':PA-PB,'platform_premium_percent':(PA/PB-1)*100,
'9950X3D2_premium':D(entries['cpuB2']['pln_price'])-v('cpuB'),'9950X3D2_premium_percent':(D(entries['cpuB2']['pln_price'])/v('cpuB')-1)*100,
'conditional_ram_saving':v('ramA')-D(entries['ram_value']['pln_price']),
'nonqualified_bundle_gpu_gap_one':v('gpu')-D('13150'),'nonqualified_bundle_gpu_gap_two':2*v('gpu')-D('13150')}.items()},
'C_current_qualifying_pair_total':None,'C_fit_validated_pair_total':None,'C_actual_savings':None,'totals_basis':'Product-only current/reference mixture, NOT delivered or purchase-qualified. C system not computed.'}

# Price history is exact source/product where possible, not a market-wide price index.
history=[]
for key,row in entries.items():
    past=[r for r in old if r['source_url']==row['source_url'] and r['currency']==row['currency'] and r['price']!='unknown']
    if not past: continue
    bydate={r['observed_at']:r for r in past};past=[bydate[k] for k in sorted(bydate)]
    curr=D(row['price']);vals=[D(r['price']) for r in past]+[curr];first=past[0];prev=past[-1]
    history.append({'key':key,'track':row['category'],'source_url':row['source_url'],'currency':row['currency'],'first_date':first['observed_at'],'first':first['price'],'previous_date':prev['observed_at'],'previous':prev['price'],'current':row['price'],'min':money(min(vals)),'max':money(max(vals)),'change_previous':money(curr-D(prev['price'])),'change_first':money(curr-D(first['price'])),'weekly_change':'unknown; no 2026-09-13 observation','note':'GPU/CPU marketplace seller changed; not like-for-like' if key.endswith('unqualified') else 'raw offer history; availability, seller and tax evidence must be considered'})
calc['component_history']=history
# Independent track histories from published report figures (not retroactively restated).
calc['track_history']={
 'A':{'2026-08-09':'70348.67','2026-08-16':'70545.48','2026-08-23':'69881.19','2026-08-30':'70312.19',DATE:money(A)},
 'B1':{'2026-08-09':'47196.41','2026-08-16':'48340.64','2026-08-23':'48002.29','2026-08-30':'48316.17',DATE:money(B1)},
 'B2':{'2026-08-09':'46025.26','2026-08-16':'47184.06','2026-08-23':'46855.99','2026-08-30':'47100.84',DATE:money(B2)},
 'C':{'2026-08-23':'56282.19','2026-08-30':'62463.19',DATE:None}}

def link(x,amount=None):
    return f'[{fmt(x["unit_pln"] if amount is None else amount)} PLN]({x["source_url"]})'

def table(keys,track):
    out=['| Component / exact identity | Qty | Product/reference PLN | Evidence date and state |','|---|---:|---:|---|']
    for k in keys:
        x=inputs[k];q=x['qtyA' if track in ['A','C'] else 'qtyB'];amount=v(k)*q
        out.append(f'| {x["name"]} | {q} | {link(x,amount)} | {x["source_date"]}: {x["state"]} |')
    return '\n'.join(out)
ka=[k for k,x in inputs.items() if x['qtyA']]
kb=[k for k,x in inputs.items() if x['qtyB']]
t=calc['totals']
report=f'''# Recovery workstation monitor report — {DATE}

## Headline and RAM anomaly state

**THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.**

- A, 128GB, one ProArt RTX 5090: **{fmt(A)} PLN reference-priced, incomplete**. CPU reference is dated August 30; case reference August 9; G5 kit is special-order, not stocked.
- C, same 128GB Threadripper platform: **current qualifying matching-pair total incomplete; fit-validated total incomplete**. No invented pair/system price or savings. The advertised water-block bundle is not purchase-qualified.
- B1, 128GB/one ProArt/PRIME PX-2200: **{fmt(B1)} PLN product-only provisional**.
- B2, same AM5 machine with VERTEX GX-1200: **{fmt(B2)} PLN product-only provisional, one-GPU-only**.
- Decisions: **WAIT for A, C and B**. No BUY NOW. Prices are not full delivered installation costs; unresolved QVL, cabling, physical and seller gates remain.
- Important changes: an exact ProArt is now directly offered by Komputronik, not just a stale Euro price; Morele marketplace seller attribution and Senetic net/gross traps were detected. Full details below. No observations for September 6/13 were manufactured; seven-day changes are unknown.

## Table A — complete locked Threadripper workstation prices

{table(ka,'A')}

A one-GPU reference sum **{fmt(A)} PLN**; theoretical two-ProArt arithmetic **{fmt(A+v('gpu'))} PLN** (not a two-card stock quote). Non-GPU reference subtotal **{fmt(A-v('gpu'))} PLN**. Delivery, destination case VAT and any required hubs/support extras remain unknown. Founders Edition current price/stock unknown; ProArt is the configured alternative, not an architecture change.

## Table C — complete locked Threadripper dual-used-RTX-3090 value workstation

{table([k for k in ka if k!='gpu'],'C')}

| GPU/condition/fit requirement | Current evidence | Price/state |
|---|---|---|
| Advertised two Zotac Trinity OC ZT-A30900J-10P, Bykski water blocks | Private Kraków seller identity/serials/revision match unverified; unfinished condition/test text; original coolers uncertain | [13,150.00 PLN advertised bundle]({raw[16]['url']}); not a qualifying pair |
| Complete GPU loop | Not included; block geometry, rear-memory cooling, pump/radiators/fittings/leak tests unresolved | Unpriced; CPU AW420 is not the GPU loop |
| Current qualifying matching-pair installed system | All A non-GPU parts retained; no gaming-platform substitution | **Incomplete** |
| Best fit-validated matching-pair installed system | None of sampled offers passes identity/condition/thermal/geometry gates | **Incomplete** |
| NVLink | Explicitly absent from bundle; generation/spacing/price/benefit unverified | Excluded, not assumed free |

48GB is aggregate physical VRAM across two 24GB devices, never one unified allocation. No current savings against A can be established. Merely comparing the unqualified advertised bundle with one/two current ProArt unit prices yields {fmt(t['nonqualified_bundle_gpu_gap_one'])}/{fmt(t['nonqualified_bundle_gpu_gap_two'])} PLN GPU acquisition gaps; these are **not system savings** and omit mandatory water-loop costs and all qualification risk. The old OLX air pair is HTTP 403 today, not verified current stock; August's price/status stays historical. [Full pair, refurbished-single, warranty and testing evidence](../research/{DATE}-track-c.md).

## Table B — complete locked AM5 value/showcase workstation prices

{table(kb,'B')}

| Alternative / total | Product/reference amount | Qualification |
|---|---:|---|
| B2 replaces B1 PSU with VERTEX GX-1200 | {link(inputs['psuB2'])} | ATX 3.0 exact listing; native cable check required; one GPU only |
| 9950X3D2 100-100001978WOF, optional CPU | [{fmt(entries['cpuB2']['pln_price'])} PLN]({entries['cpuB2']['source_url']}) | +{fmt(t['9950X3D2_premium'])} PLN / +{t['9950X3D2_premium_percent']}%; not substituted |
| B1 one GPU | **{fmt(B1)} PLN** | Product-only provisional; 2200W power-ready, not stock-layout chassis-ready |
| B2 one GPU | **{fmt(B2)} PLN** | Product-only provisional; lower-power PSU, no two-GPU claim |
| B1 theoretical two ProArts | **{fmt(B1+v('gpu'))} PLN** | Arithmetic only; quantity two unverified; HAVN conversion/airflow unpriced |

## Compact equal-128GB architecture comparison

| Metric | A | C | B |
|---|---|---|---|
| CPU / board | 9960X / TRX50 AI TOP | Same A platform | 9950X3D / X870E AORUS MASTER X3D ICE |
| RAM | 4x32 ECC RDIMM, quad-channel | Same A kit | 2x64 UDIMM, dual-channel |
| Case / cooler | Enthoo Elite Server BK02 / AW420 | Same; separate GPU loop absent for advertised bundle | White HS 420 VGPU / white non-ARGB PANORAMA 360 |
| Fans | 6x140 + 6x120, plus AIO fans | Same | 8x140, plus AIO fans |
| Storage | 2x9100 PRO 4TB | Same | 9100 PRO 4TB + 990 PRO 4TB |
| PSU | PRIME PX-2200 | Same; leads depend on exact card sockets | B1 PRIME PX-2200; B2 VERTEX GX-1200 |
| GPU / physical VRAM | 1x5090 / 32GB | 2x3090 / 48GB separate devices | 1x5090 / 32GB |
| Current total state | {fmt(A)} PLN mixed-date reference | Incomplete | {fmt(B1)} B1 / {fmt(B2)} B2 PLN product-only |
| Two-GPU caveat | Theoretical {fmt(A+v('gpu'))} PLN; fit and quantity two unverified | Pair/loop/thermal gates open | x8/x8; stock VGPU assembly must be removed; two ProArts not airflow-safe default |

## Platform-only costs

CPU + motherboard + RAM + cooler + case only; GPU/storage/PSU/fans excluded:

- A and C: **{fmt(PA)} PLN**, including dated CPU/case and special-order RAM references.
- B: **{fmt(PB)} PLN**, current product prices, delivery excluded.
- Platform premium: **{fmt(PA-PB)} PLN / {t['platform_premium_percent']}%**. The unavailable Kingston RDIMM value kit would reduce A's arithmetic by {fmt(t['conditional_ram_saving'])} PLN, but is not a purchasable/QVL-validated replacement and is excluded from official totals. 256GB remains future-only.

## Totals, Threadripper premium and weekly decision

A 128GB {fmt(A)} PLN; C current/fit-validated 128GB states both incomplete; B 128GB B1 {fmt(B1)} / B2 {fmt(B2)} PLN. All non-delivered and non-BUY-NOW as described above.

A premium over B1: **{fmt(A-B1)} PLN / {t['A_premium_B1_percent']}%**; over B2: **{fmt(A-B2)} PLN / {t['A_premium_B2_percent']}%**. Classification: **require strong justification for Threadripper** (above the configured 15,000 PLN premium threshold). Expensive RDIMM dominates, followed by platform/cooling differences; this is not simply a GPU-speed premium. All headline one-GPU figures exceed the 50,000 PLN reassessment threshold; no under-40,000 PLN purchase alert.

## Architecture advantages and compromises

Threadripper provides more PCIe connectivity, a superior multi-GPU platform, ECC RDIMM, quad-channel memory, higher capacity and stronger long-term expansion. AM5 has a lower-price/lower-power platform, a better gaming-focused CPU, cheaper motherboard/RAM/case, white showcase design and substantial 128GB capacity. Its compromises are dual-channel memory, 128GB preferred population, PCIe 5.0 x8/x8 dual GPU, fewer lanes, chipset/USB4 M.2 sharing, weaker 256GB+ expansion and a stock HAVN VGPU layout that is not two-GPU-ready.

Track C preserves Threadripper expansion and offers 48GB aggregate physical VRAM for supported distributed models or two independent 24GB jobs, with potentially lower acquisition cost. Compromises: used-card/warranty risk, separate devices, software/communication overhead, roughly 700W nominal GPU heat (exact AIB limits can differ), older Ampere Tensor/RT/media features and incomplete fit-validated evidence. Neither memory bandwidth nor VRAM is transparently pooled. NVLink is optional and application-dependent. The 9950X3D2 premium needs measured cache-sensitive workload benefit; it is not an automatic upgrade for GPU-dominated AI.

## Detailed observations and evidence limitations

### Current offers, seller identity and tax corrections

- **ProArt stock:** [Komputronik](https://www.komputronik.pl/product/1013522/asus-geforce-rtx-5090-proart-oc-32gb-dlss-4.html) directly shows exact `PROART-RTX5090-O32G`, 28,490 PLN gross, add-to-basket, store dispatch usually one business day, free delivery and three years in seller service. Final stock reservation and collection/return-postage terms are unverified. This supersedes the **20,999 PLN Euro reference observed August 9**, not a measured price rise at the same seller. Current Euro access is blocked. No verified standalone FE offer emerged from exact search and NVIDIA marketplace retrieval; this is not proof of market-wide absence.
- Morele's ProArt offer names **Madman Gaming Sp. z o.o.** visibly, despite JSON-LD naming Morele. Its 30,538 PLN is an unqualified third-party lead, excluded from totals. The 9960X page similarly identifies **kubartech**, at 6,635.33 PLN. Its legal identity, reputation and contract terms remain unverified; current CPU price in the primary basket is therefore unknown. A uses the **August 30 historical 6,421.10 PLN record**, explicitly not current stock or newly verified historical seller identity. Exact CPU/retailer searches, x-kom direct page and Ceneo comparison were attempted; the latter two were blocked/challenged. The 9970X x-kom recheck also returned 403; no invented current alternative premium.
- **SSD VAT:** Senetic visibly shows 3,283.09 PLN **net** and 4,038.20 PLN **gross**, with three units. Its JSON-LD contains the net amount. Prior observation rows that labelled structured prices as VAT-included are unreliable gross baselines; old amounts are not silently overwritten or inflated without dated page evidence. This run selects the exact no-heatsink 9100 PRO from **Morele direct at 3,946.06 PLN gross**, with last units and a quantity selector up to three (not a reservation). This is a source/tax correction, not a pure same-offer price increase. KR System's 990 PRO visibly confirms 3,058.37 gross / 2,486.48 net and 48-hour dispatch.
- **Shipping:** unknown means unknown, not free. Morele's structured 0–25.99 PLN range is not a selected delivery method. All new rows keep `delivered_pln=unknown` unless delivery is explicitly priced; Komputronik's shown free-delivery offer is still subject to destination confirmation. Historical rows sometimes used product-only prices as delivered totals; that inconsistency is preserved and disclosed, not repeated.
- Morele direct current prices: TRX50 AI TOP 4,369; AW420 1,990.76 (last unit); PRIME PX-2200 2,407.67 (last unit); 140mm fan 172.34 and 120mm fan 158.53 per unit. Fan group quantities are priced arithmetically, not reserved. B's selected board is 2,237.68, CPU 2,612.42, cooler 1,478.48, case 1,122.65 and B2 PSU 905.39 PLN. For these direct offers, PL return metadata says 14-day consumer mail returns with customer-paid postage; actual RMA service quality and any product-specific warranty duration not evidenced remain unknown. Marketing cashback is excluded.
- ASUS SAGE WiFi alternative is 3,453.29 PLN from Morele direct, but no substitution: BIOS, RAM validation, slot topology and mechanical implications need separate analysis. PRIME's exact EAN remains the locked ATX 3.1 identity even though the merchant code ends ATX30; official page was blocked in this run, so earlier manufacturer verification is historical. The additional VERTEX PX-1200 search result resolves to an **out-of-stock ATX 3.0** offer, not proof of an ATX 3.1 replacement.

### Memory and exact case follow-through

[Memory research](../research/2026-09-20-memory.md) covers manufacturer/QVL/configurator discovery, exact Polish/EU sellers and comparison/specialist paths, including Kingston, G.Skill, Micron and Samsung. Primary memory findings were independently re-fetched into `2026-09-20-verification-http.json`.

- G5 `F5-6000R3036G32GQ4-G5N`: ALTERNATE **EUR 5,488**, visible special-order 9–15 working days, OutOfStock. NBP 4.3633 effective September 18 gives 23,945.79 PLN at displayed German VAT, or **24,750.69 PLN illustrative Polish VAT** using EUR / 1.19 × 1.23 × FX. The latter is the reference input, not a delivered quote. Previous August 30 comparator EUR 5,483 / 24,555.29 PLN is historical; exchange rate and underlying price both changed. The direct retailer URL is a new source, so it has no same-URL historical-low claim.
- T5 `F5-6400R3239F32GQ4-T5N`: ALTERNATE metadata InStock at EUR 6,659; not all 128GB quad kits are unavailable. Poland delivery and exact-board proof remain unresolved, and its price is even less rational. No substitution. German shipping/30-day return terms are not automatically Polish terms.
- Kingston RDIMM `KF560R32RBEK4-128`: 3,535.98 PLN, unavailable. Exact TRX50 AI TOP configurator found but the actual kit row unextracted. The B UDIMM `KF556C40BBK2-128` is directly available at 9,889.55 PLN; its exact selected-board row also remains unverified. ASUS board validation does not validate GIGABYTE. Do not mix RDIMM/UDIMM or separate kits; conservative supported speeds and actual channel/ECC/memory stability tests are required.
- PHS `SP598864`: supplier guarantees its 32GB 2Rx8 DDR5-5600 ECC RDIMM for this board, five years, EUR 1,677.90 each. Four-module arithmetic is EUR 6,711.60, **not** a validated matching kit offer. OEM SKU/revision/batch and identical stock-four proof are absent. Its generic eight-slot/2TB text is not a CPU/population guarantee. Micron/Samsung exact part leads and CompuRAM remain validation/stock unknown, not cheap substitutions.
- Exact Enthoo Elite Server `PH-ES916E_BK02` remains unresolved: Caseking 403; exact-SKU/comparison searches found mainly non-EU and non-Server near matches; manufacturer-store indexed Server URL returned 404. Do not substitute normal Enthoo Elite or BK03. **1,719.97 PLN is solely the August 9 Caseking reference**, with destination VAT/shipping unresolved. The historical September 22 restock estimate is not newly confirmed.

### Compatibility and recommendation gates

All tracks remain **WAIT**, not merely because pricing is high. No hardware installation or stress test was performed. Before purchase, close CPU/BIOS support, exact QVL/population, cooler/socket coverage, board/case/GPU/PSU dimensions, radiator-plus-fan clearance, GPU support and cable bending, fan-header current/hub counts, native GPU leads, EU mains rating, sustained cooling and seller warranty gates.

A/C retain TRX50 AI TOP and the Server chassis: actual selected slot spacing and CPU-fed electrical widths must be audited against the exact CPU/manual and cards before asserting dual-card readiness. More expansion capability does not prove the proposed cards' fit. ProArt's 304 × 140 × 50 mm retailer specification is useful corroboration, not a completed mechanical audit. A/C fan plan remains four front 140 intake, two rear 140 exhaust, six side 120 GPU intake and AW420 top exhaust.

B's Ryzen 9000 GPU pair is PCIe 5.0 **x8/x8, not x16/x16**. M.2 does not reduce that pair under the locked board rules. Put 9100 PRO in `M2A_CPU`, 990 PRO in `M2C_SB`; `M2B_CPU` shares USB4, `M2D_SB` disables chipset `PCIEX4`, `M2E_SB` is PCIe 4.0 x2. These are retained project/manual findings, not a new full-board audit. 9950X3D2 needs F8 or newer, preferably latest stable. PANORAMA's 55mm stack is top exhaust, with display/RAM/shroud dry-fit required. Eight case fans: three bottom and three side intake, two rear exhaust. B1 is power-ready only: remove the HAVN vertical assembly for any horizontal two-card experiment and prove airflow; B2 remains one-GPU-only.

C: verify matching physical SKU/revision/serials and ownership, mining/liquid/repair history, fans/connectors/pads, at least 30 minutes sustained CUDA plus full VRAM tests and logged core/hotspot/memory-junction temperatures. Prefer business invoice, written tests and at least 12-month coverage; private sales require in-person testing. Exact card socket count controls independent PSU leads: four for two two-socket cards, six for two three-socket cards; no daisy chains. Cooling must address roughly 700W nominal heat, appropriate undervolting, mechanical support and an actual intake gap. Thick matching cards are eligible when geometry and sustained airflow validate; thin/blower targets remain optional, not a completion gate. No sampled pair passed these gates. The water-bundle placeholders prevent even exact matching identity from being asserted. Refurbisher single-card catalogues in the Track C note are sold out and were not doubled into fictional pairs.

### Comparable prebuilt and optional professional GPU watch

[x-kom NYXUM NW1](https://www.x-kom.pl/p/1533478-desktop-nyxum-workstation-r9-9950x3d-128gb-4tb-rtx-5090-fe-w11px.html) recheck is HTTP 403. **46,000 PLN / in-stock / 36-month door-to-door are August 30 historical claims only**, not today's offer. Even then motherboard, RAM SKU, SSD, PSU revision, cooler and case were undisclosed. Current VAT/delivery, whole-system collection/RMA terms and like-for-like total remain unknown. Independent exact search and a [PCForce 9960X/128GB/5090 prebuilt lead](https://pcforce.pl/stacja-robocza-exs-pro-ai-amd-ryzen-threadripper-9960x-rtx5090-128gb-2tb) were attempted; the latter's direct connection failed. No exact-comparable fully specified current prebuilt was verified in this sample.

Optional AMD watch does not change the NVIDIA-locked tracks. Morele lists exact Gigabyte W7900 AI TOP 48GB at **16,545.39 PLN OutOfStock**; R9700 exact retail recheck at x-kom is blocked. Official-domain discovery found an [AMD R9700S driver page](https://www.amd.com/es/support/downloads/drivers.html/graphics/radeon-ai-pro/radeon-ai-pro-r9000-series/amd-radeon-ai-pro-r9700s.html), an indexed identity lead only: no price, launch recommendation or installable substitute inferred. ROCm/CUDA software fit remains workload-dependent.

### Recovery diagnosis and collection limits

The failed `cron_83a18a73b082_20260920_130614` transcript confirms: `web_extract` rejected the search-only backend; an inline Python command required approval and was not executed; a later plain curl fetched the product page successfully and its JSON-LD was subsequently read. The agent then ended without collecting all tracks or writing report/CSV/README. **No commit or push was attempted; this was not a Git failure, and no actual timeout is evidenced in that cron transcript.** Successful HTTP recovery was not followed through to completed research. Scheduler `last_status=ok` meant the agent returned, not that publication succeeded.

This manual recovery used normal read-only curl GETs and an explicit URL-manifest collector; parser tests cover JSON-LD plus visible text and explicit parse failures. No approval bypass, global configuration/security change, seller contact, cart submission or extra job was used. Discovery results, direct product text/metadata and failed HTTP results are persisted alongside the calculation ledger. Unsupported extraction is no longer the prescribed path; [workflow guidance](../docs/monitor-retrieval.md) is linked from AGENTS.md and appended to existing weekly/daily/final prompts. Schedules, counters, paused state and delivery were verified unchanged; the activator was untouched. Interactive successful execution is not proof that every future unattended command will be approved: a future approval block must still be reported honestly.

Some pages returned 403/429, CAPTCHA, 404 or connection failure; these remain unknown, never market-wide absence. Browser initialization in bounded research failed on a local npm cache permission error; no global permission repair was attempted. Three-path memory/used-GPU research and the additional direct-seller/comparison follow-up were completed with these limits. Public storefront evidence is not physical stock reservation, a Poland checkout or hardware testing.

## Independent history, seven-day and 30/90-day context

Seven-day change is **unknown**: no September 13 report exists. Changes below are since August 30, not WoW. Historical totals were provisional and include VAT/seller weaknesses explained above; new source changes are not pure same-offer inflation. Old reports/rows are preserved.

| Track | First published | Previous Aug 30 | Current | Observed min / max | Change previous | Change first |
|---|---:|---:|---:|---:|---:|---:|
'''
for tr,h in calc['track_history'].items():
    vals=[D(x) for x in h.values() if x is not None];first=D(next(iter(h.values())));previous=D(h['2026-08-30']);cur=h[DATE]
    if cur is None:
        report+=f'| {tr} | {fmt(first)} historical lead | {fmt(previous)} historical cooling-incomplete | Incomplete | {fmt(min(vals))} / {fmt(max(vals))} historical only | Not comparable | Not comparable |\n'
    else:
        cur=D(cur);report+=f'| {tr} | {fmt(first)} | {fmt(previous)} | {fmt(cur)} | {fmt(min(vals))} / {fmt(max(vals))} | {fmt(cur-previous)} ({money((cur/previous-1)*100)}%) | {fmt(cur-first)} ({money((cur/first-1)*100)}%) |\n'
report+='''
30-day context contains only August 23, August 30 and today; 90-day context covers the available series starting August 9, not a complete 90-day market history. C began August 23. C's earlier air and water bundles are different listings, not evidence of a same-pair price rise. No fake-discount or market-wide scarcity claim is supported. Current same-source nominal lows include 9950X3D, PANORAMA, HAVN and VERTEX GX-1200; full-build BUY NOW remains blocked. All per-component first/previous/min/max and absolute changes are retained below and in the calculation ledger; stock and seller changes must be read alongside them.

| Component key / track | Currency | First (date) | Previous (date) | Current | Min / max | Change previous / first |
|---|---|---:|---:|---:|---:|---:|
'''
for h in history:
    report+=f'| {h["key"]} / {h["track"]} | {h["currency"]} | {h["first"]} ({h["first_date"]}) | {h["previous"]} ({h["previous_date"]}) | {h["current"]} | {h["min"]} / {h["max"]} | {h["change_previous"]} / {h["change_first"]} |\n'
report+=f'\n[Calculation ledger and source dates](../research/{DATE}-calculations.json). [Recovery workflow](../docs/monitor-retrieval.md).\n'
(ROOT/'reports'/f'{DATE}.md').write_text(report)
(ROOT/'research'/f'{DATE}-calculations.json').write_text(json.dumps(calc,indent=2,ensure_ascii=False)+'\n')
with (ROOT/'data/observations.csv').open('a',newline='') as f:
    csv.DictWriter(f,fieldnames=fields,lineterminator='\n').writerows(new)
assert (ROOT/'data/observations.csv').read_bytes().startswith(old_bytes)
print(json.dumps({'appended':len(new),'totals':t},indent=2))
