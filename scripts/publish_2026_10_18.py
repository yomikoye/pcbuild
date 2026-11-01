"""Dated, append-only 2026-10-18 observation and Decimal illustration builder.
Run once after reviewing both public-HTTPS captures. Not a generic quote selector.
"""
import csv
import json
from decimal import Decimal as D
from pathlib import Path

root = Path(__file__).resolve().parents[1]
raw = json.loads((root / 'research/2026-10-18-http.json').read_text())
raw += json.loads((root / 'research/2026-10-18-followup-http.json').read_text())
by_url = {x['url']: x for x in raw}
old = list(csv.reader((root / 'data/observations.csv').open(newline='')))
assert not any(r[0] == '2026-10-18' for r in old[1:]), 'Already published'
columns = old[0]
assert len(columns) == 17
rows = []
selected = {}

def add(track, cat, url, product, sku, seller, price=None, currency='PLN', stock='unknown', note='', warranty='unknown', rma='unknown', vat=None, pln=None, shipping='unknown', country='Poland', key=None):
    evidence = by_url[url]
    assert evidence['url'].startswith('https://')
    assert evidence.get('http', '').startswith('200 '), url
    offer = next((p.get('offers') for p in evidence.get('products', []) if isinstance(p.get('offers'), dict)), {})
    if price is not None and offer.get('price') is not None:
        assert D(str(offer['price'])) == D(str(price)), (url, offer.get('price'), price)
    if seller == 'Morele.net Sp. z o.o.' and stock != 'out of stock':
        assert 'Sprzedaje i wysyła przedsiębiorca:\nMorele.net' in evidence['text'], url
    if seller == 'ALTERNATE GmbH':
        assert offer['seller']['name'] == seller
    if seller == 'KR System':
        assert offer['seller']['name'] == seller
    v = 'gross consumer VAT included' if vat is None and currency == 'PLN' else (vat or 'unknown')
    amount = 'unknown' if price is None else str(D(str(price)).quantize(D('.01')))
    val = amount if pln is None and currency == 'PLN' else (str(pln) if pln is not None else 'unknown')
    rows.append(['2026-10-18', 'Track ' + track + ' ' + cat, product, sku, seller, country, amount, currency, val, v, shipping, 'unknown', stock, warranty, rma, url, note + ' Direct 2026-10-18 capture; selected freight/checkout not established; delivered PLN unknown.'])
    if key:
        selected[key] = D(val)

m = 'https://www.morele.net/'
a = 'https://www.alternate.de/G-Skill/'
add('A','CPU',m+'procesor-amd-ryzen-threadripper-9960x-4-2-ghz-128-mb-box-100-100001595wof-15415332/','Threadripper 9960X','100-100001595WOF','Morele.net Sp. z o.o.','6814.14','PLN','InStock; visible merchant','Shared C.',key='acpu')
add('A','Motherboard',m+'plyta-glowna-gigabyte-trx50-ai-top-13812451/','Gigabyte TRX50 AI TOP','TRX50 AI TOP','Morele.net named in metadata; visible merchant unavailable','4409.99','PLN','OutOfStock','Shared C; not purchasable.')
add('A','RAM matched 128GB reference',a+'RIMM-128-GB-DDR5-6000-4x-32-GB-Quad-Kit-ECC-Arbeitsspeicher/html/product/100130582','G.Skill G5 Neo 4x32GB ECC RDIMM','F5-6000R3036G32GQ4-G5N','ALTERNATE GmbH','5866','EUR','OutOfStock','Shared C; gross German 19% VAT; no PL checkout; DDR5-6000 quad kit.','unknown','DE returns 30 days by mail; PL RMA unknown','German 19% VAT; Poland adjustment illustrative','25611.54','DE-only 7.99 EUR; PL unknown','Germany')
add('A','RAM T5 matched alternative',a+'RIMM-128-GB-DDR5-6400-4x-32-GB-Quad-Kit-ECC-Arbeitsspeicher/html/product/100142743','G.Skill T5 Neo 4x32GB ECC RDIMM','F5-6400R3239F32GQ4-T5N','ALTERNATE GmbH','6729','EUR','OutOfStock','Not substituted; 256GB future-only.','unknown','DE returns 30 days; PL unknown','German 19% VAT; PL checkout unknown','29379.08','DE-only 7.99 EUR; PL unknown','Germany')
add('A','RAM Kingston value alternative',m+'pamiec-kingston-fury-renegade-pro-ddr5-128-gb-6000mhz-cl32-kf560r32rbek4-128-13263643/','Kingston Renegade Pro 4x32GB ECC RDIMM','KF560R32RBEK4-128','Morele.net metadata; visible merchant unavailable','3535.98','PLN','OutOfStock','Exact board QVL pending; not substituted.')
add('A','GPU shared B', 'https://www.krsystem.pl/karta_graficzna_asus_proart_geforce_rtx_5090_oc_32gb_gddr7_dls-item-80334.html','ASUS ProArt RTX 5090 OC 32GB','PROART-RTX5090-O32G','KR System','33945.84','PLN','InStock JSON-LD; quantity two unknown','New exact Polish seller; visible 33945.84 gross; ship and final stock unconfirmed.','unknown','PL seller RMA detail unknown',key='gpu')
add('A','GPU sold-out comparator','https://www.komputronik.pl/product/1013522/asus-geforce-rtx-5090-proart-oc-32gb-dlss-4.html','ASUS ProArt RTX 5090 OC 32GB','PROART-RTX5090-O32G','Komputronik S.A.','36390','PLN','SoldOut','Not an available 36390 offer; last week 32890 SoldOut.')
add('A','CPU cooler',m+'chlodzenie-wodne-thermaltake-aio-aw420-cl-w445-pl14bl-a-15342140/','Thermaltake AW420 TR5/SP6','CL-W445-PL14BL-A','Morele.net Sp. z o.o.','1884.29','PLN','InStock; visible merchant','Shared C.',key='acooler')
add('A','Case','https://www.ldlc.com/en/product/PB00756899.html','Phanteks Enthoo Elite Server','PH-ES916E_BK02','LDLC','499.95','EUR','InStock; Add to basket','Shared C; Polish shipping and checkout unknown; ordinary Enthoo Elite excluded.','unknown','France to PL collection/RMA unknown','French gross; PL checkout VAT unknown','2182.83','Poland unknown','France')
add('A','PSU',m+'zasilacz-seasonic-prime-px-atx-3-2200w-prime-px-2200-atx30-14499536/','Seasonic PRIME PX-2200 ATX 3.1','PRIME-PX-2200-ATX30','Morele.net Sp. z o.o.','2499','PLN','InStock; visible merchant','Shared C/B1; EAN 4711173878414; Seasonic official family URL 403 today; native leads pending.','12 years historically','PL mail route; handling unmeasured',key='psu')
add('A','SSD shared B',m+'dysk-ssd-samsung-9100-pro-4tb-m-2-2280-pci-e-x4-gen5-nvme-mz-vap4t0bw-14740719/','Samsung 9100 PRO 4TB','MZ-VAP4T0BW','Morele.net Sp. z o.o.','4026.61','PLN','InStock; visible merchant','Shared C x2 / B x1; quantity two not reserved; Senetic visible gross 4913.54, NOT JSON-LD net.','5 years/TBW historically','PL mail route; handling unmeasured',key='ssd')
add('A','SSD Senetic gross crosscheck','https://www.senetic.pl/product/MZ-VAP4T0BW','Samsung 9100 PRO 4TB','MZ-VAP4T0BW','Senetic S.A.','4913.54','PLN','21-30 displayed','Visible 3994.75 net / 4913.54 gross; 19.18 shipping displayed but quantity/checkout not fixed.','5 years/TBW historically','Senetic RMA route unknown',shipping='19.18 PLN displayed; checkout quantity unknown')
add('A','Fan 140mm',m+'wentylator-noctua-nf-a14x25-g2-pwm-chromax-black-15645657/','Noctua NF-A14x25 G2 PWM chromax.black','NF-A14x25 G2 PWM CH.BK','Morele.net Sp. z o.o.','169.86','PLN','InStock; visible merchant','Unit price; A/C six B eight; multiunit stock unknown.','6 years historically','PL mail route',key='fan140')
add('A','Fan 120mm',m+'wentylator-noctua-nf-a12x25-g2-pwm-chromax-black-600144884/','Noctua NF-A12x25 G2 PWM chromax.black','NF-A12x25 G2 PWM chromax.black','Morele.net Sp. z o.o.','179.60','PLN','InStock; visible merchant','Unit price; A/C six; multiunit stock unknown.','6 years historically','PL mail route',key='fan120')
add('B','CPU unqualified marketplace',m+'procesor-amd-ryzen-9-9950x3d-4-3-ghz-128-mb-box-100-100000719wof-14743984/','AMD Ryzen 9 9950X3D','100-100000719WOF','ITsun Sp.z o.o.; underlying merchant terms unqualified','2898','PLN','InStock metadata','Visible merchant ITsun not Morele direct; primary uses Sep 27 direct 2669 reference.')
add('B','CPU alternative',m+'procesor-amd-ryzen-9-9950x3d2-4-3-ghz-192-mb-box-100-100001978wof-15920184/','AMD Ryzen 9 9950X3D2 Dual Edition','100-100001978WOF','Morele.net Sp. z o.o.','4102.49','PLN','InStock; visible merchant','Released; F8+ BIOS; not substituted.',key='balt')
add('B','Motherboard',m+'plyta-glowna-gigabyte-x870e-aorus-master-x3d-ice-15566741/','GIGABYTE X870E AORUS MASTER X3D ICE','X870E AORUS MASTER X3D ICE','Morele.net Sp. z o.o.','2102.99','PLN','InStock; visible merchant','EAN 4719331876517; x8/x8 GPU pair; QVL pending.',key='bboard')
add('B','RAM 128GB',m+'pamiec-kingston-fury-beast-ddr5-128gb-5600mt-s-cl40-czarny-kf556c40bbk2-128-15245805/','Kingston Beast 2x64GB DDR5-5600 UDIMM','KF556C40BBK2-128','Morele.net Sp. z o.o.','13098.98','PLN','InStock; visible merchant','Factory kit; exact GIGABYTE board QVL still unverified; no RDIMM substitution.','limited lifetime historically','PL mail route',key='bram')
add('B','CPU cooler',m+'chlodzenie-wodne-jetworld-tryx-panorama-360-aio-l-p360n-ds3m-g1w-14962229/','TRYX PANORAMA 360 white non-ARGB','L-P360N-DS3M-G1W','Morele.net Sp. z o.o.','1670.16','PLN','InStock; visible merchant','55mm stack top exhaust; large pump dry-fit.','6 years cooler / 2 display historically','PL mail route',key='bcooler')
add('B','Case marketplace',m+'obudowa-havn-hs-420-vgpu-biala-hvn-ca-hs420-07-14454524/','HAVN HS 420 VGPU White','HVN-CA-HS420-07','SuperTech; actual marketplace merchant','1249.99','PLN','InStock metadata','Not Morele direct; B retains 1139 Sep 27 direct reference; stock VGPU one-GPU-first.')
add('B','PSU B2 one-GPU-only',m+'zasilacz-seasonic-vertex-gx-1200w-vertex-gx-1200-13040437/','Seasonic VERTEX GX-1200 ATX 3.0','VERTEX-GX-1200','Morele.net Sp. z o.o.','1053.95','PLN','InStock; visible merchant','EAN 4711173877721; NOT ATX 3.1; native GPU cable revision unverified.',key='b2psu')
add('B','SSD secondary','https://www.krsystem.pl/samsung_dysk_ssd_990pro_gen4.0x4_nvme_4tb_mzv9p4t0bw-item-73006.html','Samsung 990 PRO 4TB','MZ-V9P4T0BW','KR System','3238.55','PLN','InStock metadata','M2C_SB; shipping unknown.',key='bssd')
add('C','GPU advertised water-block pair','https://allegrolokalnie.pl/oferta/zestaw-2x-rtx-3090-zotac-trinity-24gb-nvlink-wodne','Two Zotac RTX 3090 Trinity OC 24GB with Bykski blocks','ZT-A30900J-10P claimed; revisions unknown','private individual identity unknown','13050','PLN','Kup teraz panel visible; pair unqualified','Price 13050 visible in text (no Product JSON-LD); private; placeholders for different codes and tests; original coolers, serials, ownership, mining/repairs/pads, temperature, VRAM/CUDA tests, warranty unknown; full custom loop unpriced; NVLink excluded.','none verified; private withdrawal unavailable','in-person test only; carrier coverage unknown','private sale; invoice/VAT unknown',shipping='10.49 locker / 10.95 InPost / 17 courier displayed; insured shipping unknown')
# Pixel2Point HTTP 404: stale single-card listing, not a qualifying current pair.
assert len(rows) == 23
rate = D('4.3661')
assert (D('5866')*rate).quantize(D('.01')) == D('25611.54')
# Use gross foreign-price conversion and distinct, hypothetical Polish VAT adjustment only.
ram_pl = (D('5866') / D('1.19') * D('1.23') * rate).quantize(D('.01'))
case_pl = (D('499.95') * rate).quantize(D('.01'))
assert case_pl == D('2182.83')
assert selected['gpu'] == D('33945.84')
platform_a = selected['acpu'] + D('4409.99') + ram_pl + selected['acooler'] + case_pl
platform_b = D('2669') + selected['bboard'] + selected['bram'] + selected['bcooler'] + D('1139')
non_gpu_a = platform_a + selected['psu'] + selected['ssd']*2 + selected['fan140']*6 + selected['fan120']*6
one_a = non_gpu_a + selected['gpu']
b1 = platform_b + selected['gpu'] + selected['psu'] + selected['ssd'] + selected['bssd'] + selected['fan140']*8
b2 = b1 - selected['psu'] + selected['b2psu']
calc = {k: str(v if k == 'eur_pln_nbp_oct16' else v.quantize(D('.01'))) for k,v in {
 'eur_pln_nbp_oct16': rate, 'g5_german_gross_eur': D('5866'), 'g5_converted_german_gross_pln': D('5866')*rate,
 'g5_illustrative_polish_23pct_pln': ram_pl, 'case_french_gross_pln':case_pl,
 'a_c_platform_only':platform_a,'b_platform_only':platform_b,'a_c_non_gpu':non_gpu_a,'a_one_5090':one_a,'a_theoretical_two_5090':one_a+selected['gpu'],
 'b1_one_5090':b1,'b2_one_5090':b2,'b1_theoretical_two_5090':b1+selected['gpu'],
 'platform_premium_pln':platform_a-platform_b,'platform_premium_percent':(platform_a-platform_b)/platform_b*100,
 'a_vs_b1_pln':one_a-b1,'a_vs_b1_percent':(one_a-b1)/b1*100,
 'a_vs_b2_pln':one_a-b2,'a_vs_b2_percent':(one_a-b2)/b2*100,
 'cpu_alternative_vs_direct_historical_pln':selected['balt']-D('2669'),
 'cpu_alternative_vs_direct_historical_percent':(selected['balt']-D('2669'))/D('2669')*100,
 'c_unqualified_pair_hardware_only':non_gpu_a+D('13050')
 }.items()}
calc.update({'date':'2026-10-18','status':'incomplete product-only illustrative baskets; no current delivered A/B/C total','c_current':'incomplete','c_fit_validated':'incomplete','source':'research/2026-10-18-http.json + followup; 2026-10-11.md historical B CPU/case direct references','rows_added':len(rows)})
ledger = root/'research/2026-10-18-calculations.json'
assert not ledger.exists()
ledger.write_text(json.dumps(calc, indent=2, ensure_ascii=False)+'\n')
with (root/'data/observations.csv').open('a', newline='') as out:
    csv.writer(out, lineterminator='\n').writerows(rows)
print(json.dumps(calc, indent=2))
