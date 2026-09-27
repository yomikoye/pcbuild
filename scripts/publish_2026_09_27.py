"""One-time evidence-checked weekly snapshot. Refuses to overwrite report or duplicate observations."""
import csv
import json
import re
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

root=Path(__file__).resolve().parents[1]
date='2026-09-27'
report=root/f'reports/{date}.md'
ledger=root/f'research/{date}-calculations.json'
if report.exists() or ledger.exists(): raise FileExistsError('dated publication already exists')
obs=root/'data/observations.csv'
old=obs.read_text()
if any(row.startswith(date+',') for row in old.splitlines()):raise ValueError('observations already appended')
http=[]
for suffix in ('http','followup-http','fallback-http'):
    http.extend(json.loads((root/f'research/{date}-{suffix}.json').read_text()))
byurl={r['url']:r for r in http}
U={
'cpuA':'https://www.morele.net/procesor-amd-ryzen-threadripper-9960x-4-2-ghz-128-mb-box-100-100001595wof-15415332/',
'boardA':'https://www.morele.net/plyta-glowna-gigabyte-trx50-ai-top-13812451/',
'ramA':'https://www.alternate.de/G-Skill/RIMM-128-GB-DDR5-6000-4x-32-GB-Quad-Kit-ECC-Arbeitsspeicher/html/product/100130582',
'ramAlt':'https://www.morele.net/pamiec-kingston-fury-renegade-pro-ddr5-128-gb-6000mhz-cl32-kf560r32rbek4-128-13263643/',
'gpu':'https://www.komputronik.pl/product/1013522/asus-geforce-rtx-5090-proart-oc-32gb-dlss-4.html',
'coolA':'https://www.morele.net/chlodzenie-wodne-thermaltake-aio-aw420-cl-w445-pl14bl-a-15342140/',
'caseA':'https://www.caseking.de/en/phanteks-enthoo-elite-server-pc-case-big-tower-ssi-eeb-and-multi-gpu-black/GEPH-222.html',
'psu':'https://www.morele.net/zasilacz-seasonic-prime-px-atx-3-2200w-prime-px-2200-atx30-14499536/',
'ssd':'https://www.senetic.pl/product/MZ-VAP4T0BW',
'fan140':'https://www.morele.net/wentylator-noctua-nf-a14x25-g2-pwm-chromax-black-15645657/',
'fan120':'https://www.morele.net/wentylator-noctua-nf-a12x25-g2-pwm-chromax-black-600144884/',
'cpuB':'https://www.morele.net/procesor-amd-ryzen-9-9950x3d-4-3-ghz-128-mb-box-100-100000719wof-14743984/',
'cpuB2':'https://www.morele.net/procesor-amd-ryzen-9-9950x3d2-4-3-ghz-192-mb-box-100-100001978wof-15920184/',
'boardB':'https://www.morele.net/plyta-glowna-gigabyte-x870e-aorus-master-x3d-ice-15566741/',
'ramB':'https://www.morele.net/pamiec-kingston-fury-beast-ddr5-128gb-5600mt-s-cl40-czarny-kf556c40bbk2-128-15245805/',
'coolB':'https://www.morele.net/chlodzenie-wodne-jetworld-tryx-panorama-360-aio-l-p360n-ds3m-g1w-14962229/',
'caseB':'https://www.morele.net/obudowa-havn-hs-420-vgpu-biala-hvn-ca-hs420-07-14454524/',
'psuB2':'https://www.morele.net/zasilacz-seasonic-vertex-gx-1200w-vertex-gx-1200-13040437/',
'ssdB':'https://www.krsystem.pl/samsung_dysk_ssd_990pro_gen4.0x4_nvme_4tb_mzv9p4t0bw-item-73006.html',
'pair':'https://allegrolokalnie.pl/oferta/zestaw-2x-rtx-3090-zotac-trinity-24gb-nvlink-wodne',
'prebuilt':'https://www.x-kom.pl/p/1533478-desktop-nyxum-workstation-r9-9950x3d-128gb-4tb-rtx-5090-fe-w11px.html',
'slim1':'https://www.newegg.com/evga-xc3-24g-p5-3975-kr-geforce-rtx-3090-24gb-graphics-card-triple-fans/p/N82E16814487524',
'slim2':'https://www.gigabyte.com/Graphics-Card/GV-N3090TURBO-24GD',
'slim3':'https://allegro.pl/produkt/karta-graficzna-asus-turbo-rtx3090-24g-24-gb-979a4b37-0fd9-492f-a849-ab0deb545370',
'bridge':'https://www.ceneo.pl/91191409',
}
fmt=lambda x:f'{x:,.2f}'
fx=D('4.3750') # NBP 187/A/NBP/2026, effective 2026-09-25
q=lambda n:n.quantize(D('.01'),rounding=ROUND_HALF_UP)
raw={}
def product(k,amount,availability=None):
    r=byurl[U[k]]; assert r['http'].startswith('200 '),(k,r['http'])
    p=r['products'][0]; o=p['offers'];o=o[0] if isinstance(o,list) else o
    assert q(D(str(o['price'])))==D(str(amount)),(k,o.get('price'),amount)
    if availability:assert availability in o['availability'],(k,o['availability'])
    raw[k]=q(D(str(amount)))
for k,p,s in [('boardA','4168.10','OutOfStock'),('ramA','5816','OutOfStock'),('ramAlt','3535.98','OutOfStock'),('gpu','30390','InStock'),('coolA','1501.99','InStock'),('psu','2407.67','InStock'),('fan140','167.53','InStock'),('fan120','194.36','InStock'),('cpuB','2669','InStock'),('cpuB2','3918.72','InStock'),('boardB','2233.16','InStock'),('ramB','9836.81','InStock'),('coolB','1499.19','InStock'),('caseB','1139','InStock'),('psuB2','1100','InStock'),('ssdB','3066.05','InStock')]:product(k,p,s)
# Morele JSON-LD's contracting seller is overridden by the visible field. Do not use these two price teasers.
for key,merchant in [('cpuA','kubartech')]:
    text=byurl[U[key]]['text'];assert re.search(r'Sprzedaje i wysyła przedsiębiorca:.{0,120}'+merchant,text,re.S),key
morele_ssd=byurl['https://www.morele.net/dysk-ssd-samsung-9100-pro-4tb-m-2-2280-pci-e-x4-gen5-nvme-mz-vap4t0bw-14740719/']['text']
assert re.search(r'Sprzedaje i wysyła przedsiębiorca:.{0,120}COMPUTERIO',morele_ssd,re.S)
assert '4 265,69\nzł\nbrutto' in byurl[U['ssd']]['text']
raw['ssd']=D('4265.69') # SENETIC visible GROSS, JSON-LD is NET
raw['cpuA']=D('6421.10') # 2026-08-30 historical, no current qualifying direct seller
raw['caseA']=D('1719.97') # 2026-08-09 historical; 403
raw['ramA_pl']=q(raw['ramA']/D('1.19')*D('1.23')*fx) # illustrative, not Polish delivered quote
A={'cpuA':1,'boardA':1,'ramA_pl':1,'gpu':1,'coolA':1,'caseA':1,'psu':1,'ssd':2,'fan140':6,'fan120':6}
B={'cpuB':1,'boardB':1,'ramB':1,'gpu':1,'coolB':1,'caseB':1,'psu':1,'ssd':1,'ssdB':1,'fan140':8}
def total(items):return q(sum((raw[k]*n for k,n in items.items()),D('0')))
At=total(A);A2=At+raw['gpu'];Ap=total({k:1 for k in ('cpuA','boardA','ramA_pl','coolA','caseA')});An=At-raw['gpu']
B1=total(B);B2=B1-raw['psu']+raw['psuB2'];Btwo=B1+raw['gpu'];Bp=total({k:1 for k in ('cpuB','boardB','ramB','coolB','caseB')})
# An offer for a water-block pair does not produce an installed machine without a separately priced loop.
C={'current':None,'fit_validated':None,'inherited_non_gpu_reference':An}
Deltas={'A_from_Sep20':At-D('80026.53'),'B1_from_Sep20':B1-D('56621.60'),'B2_from_Sep20':B2-D('55119.32'),'platform':Ap-Bp,'premiumB1':At-B1,'premiumB2':At-B2,'cpuB2':raw['cpuB2']-raw['cpuB']}
ledger_data={'date':date,'fx':{'EUR_PLN':'4.3750','source':'https://api.nbp.pl/api/exchangerates/rates/a/eur/2026-09-25/?format=json','effective':'2026-09-25'},'unit_inputs':{k:str(v) for k,v in raw.items()},'quantities':{'A':A,'B1':B},'totals_product_only':{'A':str(At),'A_two_theoretical':str(A2),'A_non_gpu_reference':str(An),'C_current':None,'C_fit_validated':None,'B1':str(B1),'B2':str(B2),'B1_two_theoretical':str(Btwo),'A_C_platform_only':str(Ap),'B_platform_only':str(Bp)},'deltas':{k:str(v) for k,v in Deltas.items()},'limitations':['RAM A illustrative Polish VAT, no checkout or stock','CPU A 2026-08-30 historical','case A 2026-08-09 historical','all shipping unknown except GPU displayed free; sums not delivered','A board OutOfStock; RAM OutOfStock','C no qualifying pair; advertised water loop absent','SSD uses Senetic visible gross, not JSON-LD net']}
def link(k,amount=None,label=None):return f'[{label or (fmt(amount)+" PLN")}]({U[k]})'
def row(label,qty,k,price,note):return f'| {label} | {qty} | {link(k,price)} | {note} |'
# Append evidence-backed records. Shared A non-GPU rows are explicitly referenced by C rather than duplicated.
fields=next(csv.reader([old.splitlines()[0]]));rows=[]
def add(track,cat,sku,k,price,seller,country='Poland',currency='PLN',vat='gross VAT included',stock='unknown',warranty='unknown',rma='unknown',notes='',shipping='unknown',product_name=None):
    amount='unknown' if price is None else str(price)
    d={v:'unknown' for v in fields}
    d.update(observed_at=date,category=f'Track {track} {cat}',product=product_name or cat,sku=sku,seller=seller,country=country,price=amount,currency=currency,pln_price=('unknown' if price is None else str(q(D(str(price))* (fx if currency=='EUR' else D(1))))),vat_status=vat,shipping_to_poland=shipping,delivered_pln='unknown',stock=stock,warranty=warranty,rma_quality=rma,source_url=U[k],notes=notes)
    rows.append(d)
common='Direct product HTML/visible merchant checked against JSON-LD where available; gross retail product price; shipping/checkout not fixed. '
for k,cat,sku,track in [('boardA','Motherboard','TRX50 AI TOP','A'),('ramA','RAM matched 128GB reference','F5-6000R3036G32GQ4-G5N','A'),('ramAlt','RAM value 128GB alternative','KF560R32RBEK4-128','A'),('gpu','GPU','PROART-RTX5090-O32G','A'),('coolA','CPU cooler','CL-W445-PL14BL-A','A'),('psu','PSU','PRIME-PX-2200-ATX30','A'),('ssd','SSD gross VAT','MZ-VAP4T0BW','A'),('fan140','Fan 140mm','NF-A14x25 G2 PWM CH.BK','A'),('fan120','Fan 120mm','NF-A12x25 G2 PWM chromax.black','A'),('cpuB','CPU','100-100000719WOF','B'),('cpuB2','CPU alternative','100-100001978WOF','B'),('boardB','Motherboard','X870E AORUS MASTER X3D ICE','B'),('ramB','RAM 128GB','KF556C40BBK2-128','B'),('coolB','CPU cooler','L-P360N-DS3M-G1W','B'),('caseB','Case','HVN-CA-HS420-07','B'),('psuB2','PSU B2 one-GPU-only','VERTEX-GX-1200 ATX 3.0','B'),('ssdB','SSD secondary','MZ-V9P4T0BW','B')]:
    p=byurl[U[k]].get('products',[{}])[0];o=p.get('offers',{});o=o[0] if isinstance(o,list) else o
    currency='EUR' if k=='ramA' else 'PLN'
    seller={'ramA':'ALTERNATE GmbH','gpu':'Komputronik S.A.','ssd':'Senetic S.A.','ssdB':'KR System'}.get(k,'Morele.net Sp. z o.o.')
    vat='German gross incl 19% VAT; Polish 23% reference '+str(raw['ramA_pl'])+' PLN, checkout unknown' if k=='ramA' else 'gross VAT included; Senetic JSON-LD NET excluded' if k=='ssd' else 'gross VAT included'
    stock='OutOfStock' if k in ('boardA','ramA','ramAlt') else 'InStock'
    notes=common+('Senetic visible gross 4265.69 PLN / net 3468.04 PLN; 11-20 units; JSON-LD net ignored. ' if k=='ssd' else '')+('ALTERNATE DE delivery 7.99 EUR is NOT Polish checkout. ' if k=='ramA' else '')+('Visible Morele direct, no marketplace attribution. ' if seller.startswith('Morele') else '')+('shared with Track C non-GPU' if track=='A' and k!='gpu' else 'shared with Track A and B' if k=='gpu' else '')
    if k=='boardA':notes+=' Current board unavailable; not a purchasable bundle.'
    if k=='ramAlt':notes+=' Exact board QVL row not reproduced; value lead not used in total.'
    if k=='psu':notes+=' EAN 4711173878414; ATX 3.1 verified historically against Seasonic; native cables need package audit; shared C and B1.'
    if k=='psuB2':notes+=' Exact offer ATX 3.0, EAN 4711173877721; no 3.1 inference.'
    add(track,cat,sku,k,raw[k],seller,country='Germany' if k=='ramA' else 'Poland',currency=currency,vat=vat,stock=stock,warranty=('3 years seller service' if k=='gpu' else 'unknown; see product page / historical terms'),rma='Poland seller route; actual handling unmeasured' if currency=='PLN' else 'DE return policy; Poland return cost unknown',notes=notes,shipping='free displayed; checkout not submitted' if k=='gpu' else 'unknown; DE 7.99 EUR is not Poland' if k=='ramA' else 'unknown; Morele 0-25.99 PLN range is not selected' if seller.startswith('Morele') else 'unknown',product_name=p.get('name',cat))
add('A','CPU unqualified marketplace lead','100-100001595WOF','cpuA',D('6624.85'),'kubartech; legal identity unverified',country='unknown',stock='last units visible; unqualified',vat='gross PL listing; visible seller differs from JSON-LD',notes='Direct product; visible contracting merchant kubartech, not Morele. Historical 2026-08-30 6421.10 PLN used as A/C reference, not current direct offer.')
add('A','Case exact target no stock','PH-ES916E_BK02','caseA',None,'Caseking GmbH; access blocked',country='Germany',currency='EUR',stock='unknown; HTTP 403',vat='unknown',notes='Historical 2026-08-09 1719.97 PLN used only as reference; do not confuse standard Enthoo Elite/BK03. Current PL delivery/stock unknown.')
# Separate teaser URL not in selected inputs: explicit evidence row.
r=byurl['https://www.morele.net/dysk-ssd-samsung-9100-pro-4tb-m-2-2280-pci-e-x4-gen5-nvme-mz-vap4t0bw-14740719/'];p=r['products'][0]
d={v:'unknown' for v in fields};d.update(observed_at=date,category='Track A SSD unqualified marketplace lead',product=p['name'],sku='MZ-VAP4T0BW',seller='COMPUTERIO; legal identity/terms unverified',country='unknown',price='3899.00',currency='PLN',pln_price='3899.00',vat_status='gross PL listing; visible seller differs from JSON-LD',shipping_to_poland='unknown',delivered_pln='unknown',stock='InStock metadata; third-party terms unverified',warranty='unknown',rma_quality='unknown',source_url=r['url'],notes='Shared B/C teaser excluded from selected totals; JSON-LD falsely names Morele as contracting seller.');rows.append(d)
add('B','PSU B1 shared A','PRIME-PX-2200-ATX30','psu',raw['psu'],'Morele.net Sp. z o.o.',stock='InStock',notes='Same exact direct Track A PSU; ATX 3.1 EAN 4711173878414; B1 power-ready not HAVN chassis-ready.')
add('B','GPU shared A','PROART-RTX5090-O32G','gpu',raw['gpu'],'Komputronik S.A.',stock='InStock',shipping='free displayed; checkout not submitted',notes='Same direct Track A offer; one GPU installed; two-unit stock unverified.')
add('B','SSD primary shared A gross','MZ-VAP4T0BW','ssd',raw['ssd'],'Senetic S.A.',stock='11-20 shown',notes='Shared A/C Senetic visible gross, not net JSON-LD; M2A_CPU.')
add('B','Fan 140mm shared A','NF-A14x25 G2 PWM CH.BK','fan140',raw['fan140'],'Morele.net Sp. z o.o.',stock='InStock',notes='Unit price x8, no quantity reservation.')
# C keeps independent pair evidence and references every A non-GPU row.
add('C','GPU advertised matching pair','ZT-A30900J-10P advertised; individual revisions unverified','pair',D('13150.00'),'private seller; identity unknown',vat='private sale; VAT invoice unknown',stock='Kup teraz visible; qualification fails',warranty='none shown; no private withdrawal right',rma='private seller; local in-person testing required',shipping='10.49 PLN parcel locker / 17 PLN courier advertised; insured shipping unknown',notes='Two Bykski water-block Zotac cards advertised but exact serial/revision match, original coolers, mining/liquid/repair/pad history, temperatures, VRAM and CUDA tests unknown; GPU custom loop unpriced and NVLink absent; no qualified current/fit total. Marketplace host is not seller.')
for cat,sku,k in [('GPU slim geometry target EVGA','24G-P5-3975-KR','slim1'),('GPU blower geometry target Gigabyte','GV-N3090TURBO-24GD','slim2'),('GPU blower geometry target ASUS','TURBO-RTX3090-24G','slim3'),('optional NVLink bridge','RTX 3090 generation/spacing unverified','bridge')]:
    add('C',cat,sku,k,None,'no qualifying pair seller verified',country='unknown',vat='unknown',stock='exact matching quantity two unverified',notes='Discovery/identity reference only; no pair price; thick matching air-cooled cards remain eligible if lanes, spacing, intake and sustained temperatures validate. NVLink excluded.' if k=='bridge' else 'Geometry option only; no current two-unit matching seller/condition/warranty tests confirmed.')
add('B','comparable prebuilt historical recheck','NYXUM NW1','prebuilt',None,'x-kom sp. z o.o.',vat='unknown',stock='HTTP 403; no present offer verified',notes='46,000 PLN and 36-month door-to-door from 2026-08-30 only; motherboard, RAM/PSU/SSD/cooler models undisclosed; current VAT/delivery and whole-system RMA unverified.')
# Normalize C private pair: advertised price is a listing, never a qualifying installed total.
for d in rows:
    if d['category']=='Track C GPU advertised matching pair':d['delivered_pln']='unknown'
assert all(set(d)==set(fields) for d in rows)
# Produce the report from the verified unit inputs.
A_labels=[('Threadripper 9960X 100-100001595WOF','cpuA',1,'2026-08-30 historical; current Morele visible seller kubartech unqualified'),('Gigabyte TRX50 AI TOP','boardA',1,'OutOfStock; listed price not purchasable'),('G.Skill G5 Neo 4x32 ECC RDIMM F5-6000R3036G32GQ4-G5N','ramA',1,'EUR 5,816 OutOfStock; illustrative PL VAT, NOT checkout'),('ASUS ProArt RTX 5090 PROART-RTX5090-O32G','gpu',1,'Komputronik direct InStock; free delivery displayed'),('Thermaltake AW420 CL-W445-PL14BL-A','coolA',1,'Morele direct InStock'),('Phanteks Enthoo Elite Server PH-ES916E_BK02','caseA',1,'2026-08-09 HISTORICAL reference; Caseking 403'),('Seasonic PRIME PX-2200 ATX 3.1 / EAN 4711173878414','psu',1,'Morele direct InStock; ATX30 is not an ATX-3.0 inference'),('Samsung 9100 PRO 4TB MZ-VAP4T0BW','ssd',2,'Senetic visible gross unit x2; shipping unknown'),('Noctua NF-A14x25 G2 chromax 140mm','fan140',6,'Morele direct unit x6'),('Noctua NF-A12x25 G2 chromax 120mm','fan120',6,'Morele direct unit x6')]
def Arows(gpu=True):
    return '\n'.join(row(label,n,k,raw['ramA_pl'] if k=='ramA' else raw[k]*n,note) for label,k,n,note in A_labels if gpu or k!='gpu')
B_labels=[('Ryzen 9 9950X3D 100-100000719WOF','cpuB',1),('X870E AORUS MASTER X3D ICE','boardB',1),('Kingston Beast 2x64GB KF556C40BBK2-128 UDIMM','ramB',1),('ASUS ProArt RTX 5090 PROART-RTX5090-O32G','gpu',1),('TRYX PANORAMA white non-ARGB L-P360N-DS3M-G1W','coolB',1),('HAVN HS 420 VGPU white HVN-CA-HS420-07','caseB',1),('Noctua NF-A14x25 G2 140mm','fan140',8),('Samsung 9100 PRO 4TB MZ-VAP4T0BW','ssd',1),('Samsung 990 PRO 4TB MZ-V9P4T0BW','ssdB',1),('B1 Seasonic PRIME PX-2200 ATX 3.1','psu',1)]
Btable='\n'.join(row(label,n,k,raw[k]*n,'Direct gross; delivery unknown' if k not in ('ssd','gpu') else 'Senetic visible GROSS (JSON-LD NET); delivery unknown' if k=='ssd' else 'Komputronik direct; free delivery displayed') for label,k,n in B_labels)
# Percentages are Decimal-based; no mental arithmetic or unverified delivered cost.
pct=lambda d,b:fmt(q(d/b*100))
hist={'A':[D(v) for v in ('70348.67','70545.48','69881.19','70312.19','80026.53')], 'B1':[D(v) for v in ('47196.41','48340.64','48002.29','48316.17','56621.60')], 'B2':[D(v) for v in ('46025.26','47184.06','46855.99','47100.84','55119.32')]}
current={'A':At,'B1':B1,'B2':B2}
history='| Track | First Aug 9 | Previous Sep 20 | Current Sep 27 | Min / max published | Weekly change from Sep 20 | Total change from first |\n|---|---:|---:|---:|---:|---:|---:|\n'
for k in ('A','B1','B2'):
    series=hist[k]+[current[k]];delta=current[k]-hist[k][-1]
    history+=f'| {k} | {fmt(series[0])} | {fmt(series[-2])} | {fmt(series[-1])} | {fmt(min(series))} / {fmt(max(series))} | {fmt(delta)} ({pct(delta,series[-2])}%) | {fmt(series[-1]-series[0])} ({pct(series[-1]-series[0],series[0])}%) |\n'
history+='| C | 56,282.19 Aug 23 air-pair lead, not verified present | Incomplete Sep 20 | **Incomplete** | historical reference min 56,282.19 / max 62,463.19 (different unqualified pairs) | Not comparable | Not comparable |'
R=f'''# Poland/EU three-track workstation monitor — {date}

## Headline and RAM anomaly state

**THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.** A **{fmt(At)} PLN** product-only mixed-date/incomplete reference; C **incomplete** (no qualifying matching pair or GPU loop); B1 **{fmt(B1)} PLN** and B2 **{fmt(B2)} PLN** product-only provisional. All three: **WAIT**, not BUY NOW. None is a verified delivered, fully buyable workstation. Biggest new alert: exact TRX50 AI TOP is now OutOfStock at Morele; Komputronik GPU rose from 28,490 to 30,390 PLN; Morele SSD/CPU JSON-LD conceal third-party merchants. See [dated HTTP source captures](../research/{date}-http.json), [follow-up](../research/{date}-followup-http.json) and [fallback](../research/{date}-fallback-http.json).

## Table A — Threadripper 9960X / 128GB / one RTX 5090

| Component / exact identity | Qty | Product/reference PLN | Evidence state |
|---|---:|---:|---|
{Arows()}

**A one-GPU {fmt(At)} PLN**; theoretical two matching ProArts **{fmt(A2)} PLN** (same unit multiplied, quantity two/fit unverified); A non-GPU subtotal **{fmt(An)} PLN**. FE offer not verified. The RAM input is not a stocked PL-delivered offer: ALTERNATE EUR 5,816 gross at German VAT, NBP 4.3750 on Sep 25, illustrative Polish 23% VAT **{fmt(raw['ramA_pl'])} PLN**. CPU uses Aug 30 {fmt(raw['cpuA'])} PLN reference, case Aug 9 {fmt(raw['caseA'])} PLN reference; board explicitly OutOfStock. All delivery costs are unknown except GPU's displayed free service; A total is neither current purchasable nor landed.

## Table C — same complete Threadripper platform, dual used RTX 3090

| Inherited non-GPU component | Qty | Product/reference PLN | Evidence state |
|---|---:|---:|---|
{Arows(False)}

| GPU / condition / warranty / geometry | Evidence and amount | Status |
|---|---|---|
| Advertised Zotac Trinity OC pair, ZT-A30900J-10P *advertised* with Bykski water blocks | {link('pair',D('13150'))}; private seller identity/serials/revisions not verified; no written warranty or private-sale withdrawal; 2x 8-pin stated, water-loop hardware absent | **Unqualified advertised bundle**; not an installed cost |
| Matching air-cooled pair currently buyable | No simultaneous exact SKU/revision, condition, seller and test evidence | **Incomplete** |
| Best fit-validated matching pair | Slot spacing, intake gap, PSU leads and sustained thermals not verified for any simultaneous pair | **Incomplete** |
| EVGA XC3 Ultra 24G-P5-3975-KR / Gigabyte Turbo GV-N3090TURBO-24GD / ASUS Turbo TURBO-RTX3090-24G | [EVGA exact SKU]({U['slim1']}), [Gigabyte exact SKU]({U['slim2']}), [ASUS single catalogue]({U['slim3']}); 2.2-slot EVGA ~285.37mm, dual-slot Gigabyte ~295mm; ASUS dimensions need authoritative confirmation | No exact qualifying pair, geometry options only; thick pairs are eligible after fit validation |
| RTX 3090 NVLink bridge | [Exact-generation bridge catalogue]({U['bridge']}); slot spacing, connector position, price, application benefit unknown | **Excluded**, not free or automatic pooling |

**C inherited non-GPU reference {fmt(An)} PLN; current installed matching-pair total incomplete; fit-validated total incomplete.** No defensible complete-system saving vs A's {fmt(At)} / theoretical {fmt(A2)} PLN. The unqualified water bundle would be {fmt(raw['gpu']-D('13150'))} / {fmt(raw['gpu']*2-D('13150'))} PLN less in advertised *GPU acquisition* than one/two ProArts, **not** like-for-like savings: custom GPU loop, shipping, tests and matched identity unpriced. The August OLX 7,400 PLN air pair is stale/unreachable today and must not be carried forward. 48GB is aggregate physical VRAM **across separate 24GB devices**, never one transparent unified 48GB allocation; model distribution requires explicit multi-GPU runtime support.

## Table B — AM5 9950X3D / 128GB / one RTX 5090

| Component / exact identity | Qty | Product/reference PLN | Evidence state |
|---|---:|---:|---|
{Btable}
| B2 substitute PSU ONLY: VERTEX GX-1200 ATX 3.0, EAN 4711173877721 | 1 | {link('psuB2',raw['psuB2'])} | Separate one-GPU-only option; cable revision unverified |

**B1 PRIME PX-2200: {fmt(B1)} PLN** (one GPU installed, dual-GPU *power*-ready, stock HAVN not two-GPU chassis-ready). **B2 VERTEX GX-1200: {fmt(B2)} PLN** (one GPU only). B1 theoretical two-ProArt arithmetic **{fmt(Btwo)} PLN** is not a complete/fit-safe offer. All are product-price sums, **not** delivered totals; do not mix B1 and B2. Distinct released [9950X3D2 100-100001978WOF]({U['cpuB2']}) **{fmt(raw['cpuB2'])} PLN**, premium **{fmt(Deltas['cpuB2'])} PLN / {pct(Deltas['cpuB2'],raw['cpuB'])}%**: potentially cache-sensitive CPU workloads, not automatic value for GPU-bound jobs; BIOS F8 or newer, preferably latest stable; excluded from B totals.

## Compact equal-128GB comparison

| Metric | A | C | B |
|---|---|---|---|
| CPU / board | 9960X / TRX50 AI TOP (board OutOfStock) | Same A platform | 9950X3D / X870E AORUS MASTER X3D ICE |
| RAM | 4x32 ECC RDIMM quad-channel; G5 unavailable | Identical A 128GB kit | 2x64 Kingston UDIMM dual-channel, board QVL pending |
| Case / cooler | Enthoo Elite Server BK02 historical / AW420 | Identical A parts; GPU loop not included | HAVN HS 420 VGPU white / TRYX PANORAMA white 360 |
| Fans | 6x140 + 6x120 + AIO | Same A | 8x140 + AIO |
| Storage | 2x9100 PRO 4TB | Same A | 9100 PRO + 990 PRO 4TB |
| PSU | PRIME PX-2200 ATX 3.1 | Same; independent PCIe leads per socket | B1 PRIME; B2 VERTEX GX-1200 ATX 3.0 |
| GPU / aggregate physical VRAM | 1x5090, 32GB | 2x used 3090, 48GB separate | 1x5090, 32GB |
| Current total PLN | {fmt(At)} incomplete reference | Incomplete | {fmt(B1)} B1 / {fmt(B2)} B2 provisional |
| Two-GPU caveat | {fmt(A2)} theoretical; two-card geometry/stock unproved | No matching tested pair; ~700W GPUs; loop missing for current lead | x8/x8; VGPU removal/two horizontal cards; two ProArts not safe default |

## Platform-only costs and required totals

CPU + motherboard + RAM + cooler + case, **excluding GPU/storage/PSU/fans**: A=C **{fmt(Ap)} PLN** reference (non-stock RAM/board, dated CPU/case); B **{fmt(Bp)} PLN** product-only. Platform-only Threadripper premium **{fmt(Deltas['platform'])} PLN / {pct(Deltas['platform'],Bp)}%**. A 128GB one GPU **{fmt(At)}**, C 128GB current **incomplete** and fit-validated **incomplete**, B1 **{fmt(B1)}**, B2 **{fmt(B2)} PLN**. Kingston 4x32 kit [{fmt(raw['ramAlt'])} PLN]({U['ramAlt']}) is OutOfStock and exact-board kit QVL not reproduced; potential arithmetic difference **{fmt(raw['ramA_pl']-raw['ramAlt'])} PLN** is NOT a purchasing saving. 256GB only future A expansion / non-default B experiment.

## Threadripper premium and weekly classification

A above B1 **{fmt(Deltas['premiumB1'])} PLN / {pct(Deltas['premiumB1'],B1)}%**; above B2 **{fmt(Deltas['premiumB2'])} PLN / {pct(Deltas['premiumB2'],B2)}%**. **Above-15,000 PLN: require strong justification for Threadripper**; distorted by the non-stock matched RDIMM and dated case/CPU, not a pure GPU value delta. Both one-GPU choices breach the 50,000 PLN reassessment threshold. **WAIT A/B/C** pending stock, delivered VAT/shipping, exact QVL and fit/warranty gates. No fake discount: do not call a third-party seller's lower teaser a Morele direct reduction, a DE VAT calculation a Polish checkout, or the stale Aug pair a current saving.

## Architecture advantages and compromises

Threadripper: more PCIe connectivity, superior multi-GPU platform, ECC RDIMM, quad-channel memory, higher memory capacity and stronger long-term expansion. AM5: lower platform price/power, better gaming-focused CPU, cheaper motherboard/RAM/case, white showcase design and substantial 128GB capacity. AM5 compromises: dual-channel, 128GB preferred, PCIe 5.0 x8/x8 electrical dual GPU (NOT x16/x16), fewer lanes, chipset/USB4 M.2 sharing, weaker 256GB+ expansion, and stock HAVN VGPU not two-GPU-ready. C offers TRX50 expansion, 48GB aggregate physical VRAM, potentially lower GPU acquisition cost, and one distributed model or two independent 24GB jobs. C compromises: used-card condition/warranty risk, separate VRAM devices, software/communication overhead, ~700W GPU heat nominal (AIB limits may differ), older Ampere Tensor/RT/media features and incomplete fit-validated pair evidence. NVLink may accelerate peer traffic but never produces one transparent 48GB device.

## Detailed observations, seller attribution and recommendation gates

- **Stock and seller:** Morele's [TRX50 AI TOP]({U['boardA']}) now shows OutOfStock at 4,168.10 PLN, down 200.90 from Sep 20's 4,369 in-stock; a lower unavailable price is **not** a buyable discount. Komputronik's exact ProArt is 30,390 PLN, InStock/add-to-cart, 3-year seller service, free shipping displayed; **+1,900 PLN at the same seller** vs Sep 20, two-card quantity unproven. Morele's 9960X page JSON-LD says Morele but visible seller is **kubartech**, 6,624.85 PLN; Morele's 9100 PRO JSON-LD 3,899 PLN names Morele but visible merchant is **COMPUTERIO**. Both unqualified for direct-retailer totals. Komputronik CPU 6,790 PLN SoldOut and board 4,149 PLN Discontinued; x-kom direct pages 403. Historical A CPU 6,421.10 PLN is not current. No silently substituted ordinary Enthoo Elite or BK03: exact Server Caseking page 403; Aug 9 reference only.
- **VAT/storage:** [Senetic exact 9100 PRO]({U['ssd']}) has 11–20 pieces visibly, **3,468.04 PLN net / 4,265.69 PLN gross**; JSON-LD carries net. A/C use two gross, B one. Sep 20 Morele-direct 3,946.06 gross was a *different seller*, not proof of a same-offer Senetic price rise. Sep 20 Senetic gross 4,038.20 vs now 4,265.69 is a genuine **+227.49 PLN/unit**. Proline 3,999 PLN SoldOut despite search index's stale 1,765 PLN teaser. [KR System 990 PRO]({U['ssdB']}) 3,066.05 gross / 2,492.72 net, dispatch 48h, final shipping unknown. Historical Aug Senetic rows erroneously marked JSON-LD net as VAT-included remain untouched; not retrospectively recalculated without dated gross pages.
- **RAM searches:** exact G.Skill G5 [QVL](https://www.gskill.com/qvl/400/446/1747204820/F5-6000R3036G32GQ4-G5N-QVL) search-index lists TRX50 AI TOP (direct manufacturer 403). G5 ALTERNATE 5,816 EUR OutOfStock, up 328 EUR vs Sep 20; G.Skill T5 `F5-6400R3239F32GQ4-T5N` [ALTERNATE](https://www.alternate.de/G-Skill/RIMM-128-GB-DDR5-6400-4x-32-GB-Quad-Kit-ECC-Arbeitsspeicher/html/product/100142743) 6,671 EUR InStock, even less rational, Poland checkout unproved. Kingston `KF560R32RBEK4-128` Morele 3,535.98 OutOfStock; Kingston exact-board configurator was 403 and indexed results did not establish exact kit row. Net-S exact SKU connection failed, Ceneo challenge; Micron/Samsung individual RDIMMs and PHS board-compatible [32GB module](https://www.phs-memory.com/computer-memory-32gb-ddr5-gigabyte-trx50-ai-top-ram-rdimm-sp598864.html) (1,677.90 EUR each) are NOT factory-matched four-module kits and require one-seller identical manufacturer part/revision/rank/speed/timings/voltage/batch, QVL/vendor proof and four-channel stability. Do not substitute irrationally priced modules. B's exact 2x64 UDIMM 9,836.81 PLN InStock; selected GIGABYTE QVL/vendor row still unknown, validate DDR5-5600 before overclocking. No RDIMM on AM5.
- **Track C seller and condition:** [private water-block listing]({U['pair']}) shows 13,150 PLN, 10.49 parcel-locker or 17 courier as offered (insured delivery/fee unknown); visible excerpt states two cards and ZT-A30900J-10P but **does not establish both physical revision/serials**. Original coolers, invoice/ownership, mining/liquid history, prior repairs/pads, fans/connectors, core/hotspot/memory-junction temps, VRAM tests, sustained >=30min CUDA, written returns/warranty and full custom GPU loop remain unknown. No private withdrawal right; platform dispute mechanism is not hardware warranty. Prefer business invoice/test report and >=12 months; private requires local in-person testing. Previous water-bundle unfilled placeholder text was observed Sep 20 and must not be taken as current positive testing. Exact EVGA XC3, Gigabyte Turbo, ASUS Turbo and any thick matching air pair searched via marketplace/exact SKU/refurbisher; Pixel2Point single refurbished Zotac 1,089.99 EUR SoldOut (12-month German defect liability historically) cannot be doubled. Indexed 27,600 PLN mining-rig pair now redirects to search and has no verified inventory; OLX 403. No pair fulfills gates. Optional bridge lacks generation/slot spacing/card connector alignment/delivered price/benefit. Two two-socket 3090 cards need four independent 8-pin leads, three-socket models six; no daisy chains. PRIME 2200W is nominally sufficient for two ~350W cards; verify exact limits, electrical slots, physical gap, direct intake, side fans, anti-sag, EU mains and sustained undervolted thermals.
- **Compatibility:** A/C selected CPU support/BIOS and exact TRX50 slot positions/electrical lane allocation, case-to-board size, AW420 TR5 coverage and top radiator-plus-fans thickness, two-card width/intake, PSU mounting/cable chamber, 12V-2x6 bend, fan-header current/groups and EU mains still need a manual/dry-fit audit. GIGABYTE board marketing's multiple x16 slots alone does not prove this two-card thermal installation. B Ryzen 9000 CPU-fed GPU pair x8/x8; M.2 does NOT reduce it: 9100 PRO in `M2A_CPU`, 990 PRO in `M2C_SB`; `M2B_CPU` shares ASMedia USB4, `M2D_SB` disables chipset `PCIEX4`, `M2E_SB` PCIe 4.0 x2. PANORAMA top-exhaust 55mm stack below HAVN 65mm nominal no-RAM-overlap limit, pump/display dry-fit. Stock VGPU is for one vertical GPU: remove assembly and use two horizontal cards only after spacing/airflow validation; two ProArts are not safe by default. B1 PRIME EAN 4711173878414 is ATX **3.1** based on historical Seasonic model-page validation (manufacturer 403 today); check native 12V-2x6 packaging and PSU-to-GPU clearance. B2 exact GX-1200 EAN 4711173877721 is **ATX 3.0**, 10-year manufacturer term visible, native lead/revision not proven; one GPU only. Seller 14-day mail return metadata where present is not a measured RMA quality or whole-system warranty.
- **Prebuilt:** [NYXUM NW1]({U['prebuilt']}) x-kom current 403; 46,000 PLN, 9950X3D/128GB/5090 FE/4TB, 36-month door-to-door were **Aug 30 history**, not current offer. Exact board/RAM/GPU-submodel PSU ATX revision/cables, cooler/SSD/case, VAT, delivery and cross-border collection/RMA are unverified; not a comparable full BOM. Optional AMD R9700/W7900 are not CUDA-substitutes; no new verified launch/stock claim.
- **Limits:** direct capture 200 is not reservation; 403, 000, search-index, sold-out and catalogue pages are not absence proof. No authenticated carts, sellers contacted, GPU tests or complete manual-based installation audit. All selected shipping unknown (GPU free shown subject to checkout); delivered_pln remains `unknown` in new observation rows. Historic rows with product-only amounts wrongly placed in delivered_pln remain unchanged and labelled. No BUY NOW.

## Independent price history and 30/90-day context

{history}

30-day window Aug 30–Sep 27 has Aug 30, Sep 20, Sep 27; Sep 6/13 missing, not flat prices. 90-day available sample starts Aug 9 (C Aug 23), shorter than a complete 90 days. C first published Aug 23 56,282.19 and previous Aug 30 62,463.19 were DIFFERENT provisional listings; present no pair, weekly/total deltas undefined, not a 3090 market-wide rise. A/B deltas are product-reference movements and cannot be equated to delivered cost changes. Same-seller ProArt rises; AW420 drops {fmt(D('1990.76')-raw['coolA'])} PLN while 120mm fan rises {fmt(raw['fan120']-D('158.53'))} PLN. Board 4,168.10 is below earlier 4,369 but out of stock and above Aug 30 3,915.39 low; no fake 'historic low'. RAM is extreme; no low alert based on unqualified seller, stale index or Polish-VAT projection. See [calculation ledger](../research/{date}-calculations.json) and [retrieval/approval boundaries](../docs/monitor-retrieval.md).
'''
# README: preserve old history, add a new linked column to every price matrix.
readme=root/'README.md';prior=readme.read_text()
prior=prior.replace('Latest report: **[2026-09-20 recovery](reports/2026-09-20.md)**',f'Latest report: **[{date}](reports/{date}.md)**')
prior=prior.replace('All tracks: WAIT. Current sums are product-only, not delivered purchase quotations. A includes explicitly dated CPU/case references and non-stock RAM. C has no qualifying or fit-validated matching pair. September 6/13 are missing observations, not unchanged prices. Historical columns below are preserved, including the now-disclosed Senetic VAT and delivered-field limitations.',f'All tracks: WAIT. A **[{fmt(At)} PLN incomplete](reports/{date}.md)**, B1 **[{fmt(B1)} PLN provisional](reports/{date}.md)**, B2 **[{fmt(B2)} PLN provisional](reports/{date}.md)**, C **[incomplete](reports/{date}.md)**. Sums are product-only, not delivered. A board and RAM unavailable; CPU/case references dated; C has no qualified pair. September 6/13 missing, not unchanged. Older historical Senetic net/delivered-field weaknesses remain disclosed in the report.')
sections=prior.split('\n## ')
assert len(sections)>=7
A_cells=[('cpuA',raw['cpuA'],'Aug 30 historical; no current direct seller'),('boardA',raw['boardA'],'No exact stock; listed only'),('ramA',raw['ramA_pl'],'No exact stock; PL-VAT reference'),('ramAlt',raw['ramAlt'],'No exact stock; QVL pending'),('gpu',raw['gpu'],'Komputronik direct'),('coolA',raw['coolA'],None),('caseA',raw['caseA'],'No exact stock; Aug 9 reference'),('psu',raw['psu'],None),('ssd',raw['ssd']*2,'gross x2'),('fan140',raw['fan140']*6,'x6'),('fan120',raw['fan120']*6,'x6')]
B_cells=[('cpuB',raw['cpuB'],None),('cpuB2',raw['cpuB2'],'alternative; not installed'),('boardB',raw['boardB'],None),('ramB',raw['ramB'],'QVL pending'),('gpu',raw['gpu'],None),('coolB',raw['coolB'],None),('caseB',raw['caseB'],None),('psu',raw['psu'],'B1'),('psuB2',raw['psuB2'],'B2 ATX 3.0'),('ssd',raw['ssd'],'gross'),('ssdB',raw['ssdB'],None),('fan140',raw['fan140']*8,'x8')]
def append_matrix(section,cells,totals):
    lines=section.splitlines();i=next(i for i,l in enumerate(lines) if l.startswith('| Component | Qty |') or l.startswith('| Component / state | Qty |'))
    lines[i]+=' | 2026-09-27 |';lines[i+1]+='---:|'
    data=iter(cells)
    for j in range(i+2,len(lines)):
        if not lines[j].startswith('|'):break
        if lines[j].startswith('| **') and any(name in lines[j] for name in totals):
            key=next(name for name in totals if name in lines[j])
            value=totals.get(key)
            if value is None: cell=f'[Incomplete; no qualifying pair](reports/{date}.md)'
            else:cell=f'**[{fmt(value)} PLN; incomplete/provisional](reports/{date}.md)**'
        else:
            k,amount,note=next(data)
            cell=link(k,amount,(fmt(amount)+' PLN'+('; '+note if note else '')))
        lines[j]+=' '+cell+' |'
    remainder=list(data)
    assert not remainder,(section.splitlines()[0],remainder,lines[i:i+18])
    return '\n'.join(lines)
# sections indexing: 0 intro, 1 A, 2 C, 3 B, 4 comparison.
sections[1]=append_matrix(sections[1],A_cells,{'one-GPU total':At,'theoretical two-GPU total':A2})
# C keeps inherited total and five options, plus two total rows.
clines=sections[2].splitlines();ci=next(i for i,l in enumerate(clines) if l.startswith('| Component / state |'))
clines[ci]+=' | 2026-09-27 |';clines[ci+1]+='---:|'
Ccells=[f'**[{fmt(An)} PLN; inherited reference](reports/{date}.md)**',link('pair',D('13150'),'13,150 PLN private water-block pair; incomplete loop'),link('slim1',label='No exact matching pair; EVGA XC3 target'),link('slim2',label='No exact matching pair; Gigabyte Turbo target'),link('slim3',label='No exact matching pair; ASUS Turbo target'),link('bridge',label='Excluded; RTX 3090 bridge spacing unverified'),f'**[Incomplete; no qualifying pair](reports/{date}.md)**',f'**[Incomplete; no fit-validated pair](reports/{date}.md)**']
for j,cell in enumerate(Ccells,ci+2):assert clines[j].startswith('|');clines[j]+=' '+cell+' |'
sections[2]='\n'.join(clines)
sections[3]=append_matrix(sections[3],B_cells,{'one GPU, 2200W PSU':B1,'one-GPU-only':B2,'theoretical two-GPU hardware':Btwo})
# Replace current comparison matrix only; historical columns above remain intact.
comp=sections[4];prefix=comp.split('\n## Comparable prebuilt')[0]
comparison=f'''Current **2026-09-27** direct-linked component matrix; A/C reference prices explicitly labelled:

| Metric | Track A | Track C (inherits A) | Track B |
|---|---|---|---|
| CPU | {link('cpuA',raw['cpuA'],'6,421.10 PLN; Aug 30 historical')} | same A historical CPU | {link('cpuB',raw['cpuB'])} |
| Motherboard | {link('boardA',raw['boardA'],'4,168.10 PLN; No exact stock')} | same A unavailable board | {link('boardB',raw['boardB'])} |
| RAM | {link('ramA',raw['ramA_pl'],fmt(raw['ramA_pl'])+' PLN; No exact stock; illustrative PL VAT')} | same A 4x32 ECC RDIMM | {link('ramB',raw['ramB'])} |
| Case | {link('caseA',raw['caseA'],'1,719.97 PLN; No exact stock; Aug 9 historical')} | same A case | {link('caseB',raw['caseB'])} |
| Cooler | {link('coolA',raw['coolA'])} | same A | {link('coolB',raw['coolB'])} |
| Fans | {link('fan140',raw['fan140']*6,'140mm x6: '+fmt(raw['fan140']*6)+' PLN')} + {link('fan120',raw['fan120']*6,'120mm x6: '+fmt(raw['fan120']*6)+' PLN')} | same A | {link('fan140',raw['fan140']*8,'140mm x8: '+fmt(raw['fan140']*8)+' PLN')} |
| Storage | {link('ssd',raw['ssd']*2,'9100 PRO x2 '+fmt(raw['ssd']*2)+' PLN gross')} | same A | {link('ssd',raw['ssd'],'9100 PRO '+fmt(raw['ssd'])+' PLN gross')} + {link('ssdB',raw['ssdB'],'990 PRO '+fmt(raw['ssdB'])+' PLN')} |
| PSU | {link('psu',raw['psu'])} | same A | B1 {link('psu',raw['psu'])}; B2 {link('psuB2',raw['psuB2'])} |
| GPU | {link('gpu',raw['gpu'])} | {link('pair',D('13150'),'13,150 PLN private water pair; unqualified/loop missing')} | {link('gpu',raw['gpu'])} |
| Physical VRAM | 32GB | 48GB aggregate separate devices | 32GB |
| Platform only | **[{fmt(Ap)} PLN incomplete](reports/{date}.md)** | **[{fmt(Ap)} PLN incomplete](reports/{date}.md)** | **[{fmt(Bp)} PLN provisional](reports/{date}.md)** |
| Current total | **[{fmt(At)} PLN incomplete](reports/{date}.md)** | **[Incomplete; no qualified pair](reports/{date}.md)** | B1 **[{fmt(B1)} PLN](reports/{date}.md)**; B2 **[{fmt(B2)} PLN](reports/{date}.md)** |
| Two GPU | **[{fmt(A2)} PLN theoretical](reports/{date}.md)**; fit/stock unverified | pair, cooling/condition incomplete; no pooled VRAM | **[{fmt(Btwo)} PLN B1 theoretical](reports/{date}.md)**; x8/x8; stock VGPU unsuitable |
'''
sections[4]=sections[4][:0]+comparison.strip()+'\n'
# Preserve remaining headings; sections[5] is comparable prebuilt, etc.
updated='\n## '.join(sections)
updated=updated.replace('## Comparable prebuilt\n\n[x-kom NYXUM NW1: 9950X3D / 128GB / RTX 5090 FE / 4TB / Windows 11 Pro — 46,000 PLN, historical August 30 reference only]',f'## Comparable prebuilt\n\n[x-kom NYXUM NW1: 9950X3D / 128GB / RTX 5090 FE / 4TB / Windows 11 Pro — 46,000 PLN, HISTORICAL August 30 reference only]')
updated=updated.replace('September 20 recheck blocked: current stock/price unknown.','September 27 recheck blocked: current stock/price unknown.')
updated=updated.replace('The live water-block listing contains unfilled condition/test placeholders, excludes NVLink and all loop hardware, and offers no private-sale withdrawal right or written warranty.', 'The current excerpt does not provide serial-linked tests, excludes a priced full GPU loop and has no private-sale withdrawal right or written warranty; September 20 placeholder text was not revalidated.')
updated=updated.replace('Current non-GPU subtotal is a mixed-date reference',f'Current non-GPU subtotal **[{fmt(An)} PLN](reports/{date}.md)** is a mixed-date reference')
# update old stand-alone warning and notes without falsely claiming the historical comparison is current.
updated=updated.replace('The Kingston value kit remains out of stock and pending exact-board validation;', 'The Kingston value kit remains out of stock and pending exact-board validation; the selected TRX50 AI TOP is also out of stock;')
updated=updated.replace('36-month door-to-door claim and incomplete BOM are historical;', '36-month door-to-door claim and incomplete BOM are historical;')
with obs.open('a',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writerows(rows)
ledger.write_text(json.dumps(ledger_data,ensure_ascii=False,indent=2)+'\n')
report.write_text(R)
readme.write_text(updated)
print('published',len(rows),'rows; totals',ledger_data['totals_product_only'])
