"""Read-only publication audit, except for its dated machine-readable validation result.

No network access, seller contact, carts, or global settings. Recomputes prices and
states from saved evidence without importing the one-time publisher.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import re
import subprocess
import unicodedata
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT=Path(__file__).resolve().parents[1]
DAY='2026-11-01'
q=lambda x:D(x).quantize(D('.01'),rounding=ROUND_HALF_UP)
load=lambda p:json.loads(p.read_text(),parse_float=D)
checks=[]
def checked(name, condition):
    assert condition,name
    checks.append(name)

json_files=sorted(ROOT.glob('research/*.json'))+[ROOT/'monitor-config.json']
for path in json_files:
    load(path)
checked('all repository research/config JSON parses',True)
config=load(ROOT/'monitor-config.json')
manifest=load(ROOT/f'research/{DAY}-offers.json')
ledger=load(ROOT/f'research/{DAY}-calculations.json')
groups={key:load(ROOT/f'research/{DAY}{suffix}-http.json') for key,suffix in [('p',''),('f','-followup'),('s','-specs')]}
byid={item['id']:item for item in manifest['offers']}
checked('unique reviewed offer identifiers',len(byid)==len(manifest['offers']))
fx=json.loads(groups['p'][48]['text'],parse_float=D)['rates'][0]
rate=fx['mid']
checked('NBP preceding business-day FX',fx['effectiveDate']=='2026-10-30' and rate==D('4.3955'))

def structured_prices(product):
    offers=product.get('offers',[])
    if isinstance(offers,dict):
        offers=[offers]
    for offer in offers:
        if isinstance(offer,dict):
            for key in ('price','lowPrice','highPrice'):
                if key in offer:
                    try:
                        yield q(offer[key])
                    except Exception:
                        pass

def source(item):
    key,index=item['capture'].split(':')
    return groups[key][int(index)]

amounts={}
for item in manifest['offers']:
    cap=source(item)
    checked('offer capture URL '+item['id'],cap['url'].startswith('https://'))
    if item['price']=='unknown':
        continue
    value=q(item['price'])
    visible=''.join(unicodedata.normalize('NFKC',cap.get('text','')).split())
    candidates={f'{value:.2f}',f'{value:.2f}'.replace('.',','),f'{value:,.2f}',f'{value:,.2f}'.replace(',','@').replace('.',',').replace('@','.')}
    if value==value.to_integral_value():
        candidates.update({f'{value:.0f}zł', f'€{value:.0f}', f'{value:.0f}€'})
    metadata={value for product in cap.get('products',[]) for value in structured_prices(product)}
    checked('exact source amount '+item['id'],value in metadata or any(token in visible for token in candidates))
    if item['currency']=='EUR':
        amounts[item['id']]=q(value*rate)
    else:
        checked('known offer currency '+item['id'],item['currency']=='PLN')
        amounts[item['id']]=value

ram=q(D(byid['ramA']['price'])/D('1.19')*D('1.23')*rate)
fanA=q(6*amounts['fan140']+6*amounts['fan120'])
fanB=q(8*amounts['fan140'])
platformA=q(sum(amounts[k] for k in ('cpuA','boardA','coolA','caseA'))+ram)
platformB=q(sum(amounts[k] for k in ('cpuB','boardB','ramB','caseB','coolB')))
nonGPU=q(platformA+fanA+2*amounts['ssdA']+amounts['psu'])
A=q(nonGPU+amounts['gpu'])
A2=q(nonGPU+2*amounts['gpu'])
B1=q(platformB+fanB+amounts['ssdB']+amounts['ssdB2']+amounts['psu']+amounts['gpu'])
B2=q(B1-amounts['psu']+amounts['b2'])
Cinvalid=q(nonGPU+amounts['pairC'])
expected={'A':A,'A_two':A2,'C_non_gpu':nonGPU,'C_unqualified_stickers_no_loop':Cinvalid,'B1':B1,'B2':B2,'B1_two':q(B1+amounts['gpu']),'platform_A_C':platformA,'platform_B':platformB,'platform_premium':q(platformA-platformB),'platform_premium_pct':q((platformA-platformB)/platformB*100),'A_over_B1':q(A-B1),'A_over_B1_pct':q((A-B1)/B1*100),'A_over_B2':q(A-B2),'A_over_B2_pct':q((A-B2)/B2*100),'cpu_alternative_premium':q(amounts['cpuAlt']-amounts['cpuB']),'cpu_alternative_premium_pct':q((amounts['cpuAlt']-amounts['cpuB'])/amounts['cpuB']*100),'marketplace_gpu_surcharge':q(amounts['gpuMarket']-amounts['gpu']),'marketplace_gpu_surcharge_pct':q((amounts['gpuMarket']-amounts['gpu'])/amounts['gpu']*100),'C_unqualified_gpu_sticker_difference_A1':q(amounts['gpu']-amounts['pairC']),'C_unqualified_gpu_sticker_difference_A2':q(2*amounts['gpu']-amounts['pairC']),'A_value_ram_scenario':q(A-ram+amounts['ramValue']),'A_value_ram_potential_difference':q(ram-amounts['ramValue']),'AW420_stack_mm':q(D(27)+D(25)),'AW420_stack_nominal_margin_mm':q(D(65)-D(27)-D(25)),'AW420_three_fan_current_A':q(D('.36')*3),'gpu_heat_C_nominal_W':q(D(350)*2),'gpu_heat_A2_reference_W':q(D(575)*2)}
checked('every independent Decimal total/premium/thermal calculation',expected=={key:D(value) for key,value in ledger['results_pln'].items()})
for key,quantity in ledger['A_quantities'].items():
    checked('A component amount '+key,D(ledger['A_amounts_pln'][key])==q((ram if key=='ramA' else amounts[key])*quantity))
for key,quantity in ledger['B1_quantities'].items():
    checked('B1 component amount '+key,D(ledger['B1_amounts_pln'][key])==q(amounts[key]*quantity))
productsA={p['category']:p for p in config['tracks']['A_threadripper']['products']}
productsB={p['category']:p for p in config['tracks']['B_am5_value']['products']}
checked('locked 128GB and primary CPU preserved','128GB' in productsA['RAM']['primary'] and '128GB' in productsB['RAM']['primary'] and productsB['CPU']['primary_sku']=='100-100000719WOF' and config['tracks']['C_threadripper_dual_3090']['locked_capacity_gb']==128)
checked('C full A platform inherited',config['tracks']['C_threadripper_dual_3090']['inherits_platform_from']=='A_threadripper')
checked('C current/fit/savings remain incomplete',ledger['C_current']=='incomplete' and ledger['C_fit_validated']=='incomplete' and ledger['C_qualified_savings_A1_A2']=='undefined')
checked('all delivered totals unknown',ledger['delivered_totals']=='unknown')
checked('B2 exact revision retained','ATX 3.0' in byid['b2']['sku'] and '4711173877721' in byid['b2']['notes'])
checked('PRIME exact SKU/EAN retained',byid['psu']['sku']=='PRIME-PX-2200-ATX30' and '4711173878414' in byid['psu']['notes'])

csv_path=ROOT/'data/observations.csv'
raw=csv_path.read_bytes()
prefix=raw[:raw.index(b'2026-11-01,Track A CPU,')]
checked('pre-existing collected CSV prefix byte-identical',hashlib.sha256(prefix).hexdigest()=='8da9cc7548dbf3426783ca32c29d1951cbab8e2591abae40f3f43c8c988972f7')
baseline=subprocess.check_output(['git','show',manifest['baseline_commit']+':data/observations.csv'],cwd=ROOT)
checked('all committed historical CSV bytes preserved',raw.startswith(baseline))
rows=list(csv.reader(io.StringIO(raw.decode())))
header=rows[0]
checked('CSV uniform field counts',all(len(row)==len(header) for row in rows[1:]))
observations=list(csv.DictReader(io.StringIO(raw.decode())))
new=[row for row in observations if row['observed_at']==DAY]
checked('exact append count and historical prefix',len(new)==32 and len(observations)-len(new)==len(list(csv.DictReader(io.StringIO(prefix.decode())))))
checked('new shipping/delivered unknown, no hidden zero',all(any(word in row['shipping_to_poland'] for word in ('unknown','unverified')) and row['delivered_pln']=='unknown' for row in new))
checked('every new row track-labelled',all(row['category'].startswith(('Track A ','Track B ','Track C ','Mac ')) for row in new))
checked('new CSV LF only',b'\r' not in raw[len(prefix):])
for row in observations:
    date.fromisoformat(row['observed_at'])
    for key in ('price','pln_price','delivered_pln'):
        if row[key] not in ('unknown',''):
            D(row[key])
checked('all observation dates and numeric values parse',True)
for item in manifest['offers']:
    found=[row for row in new if row['source_url']==source(item)['url'] and row['sku']==item['sku']]
    checked('CSV source amount identity '+item['id'],len(found)==1 and found[0]['price']==('unknown' if item['price']=='unknown' else str(q(item['price']))))
    checked('CSV exact PLN conversion '+item['id'],found[0]['pln_price']==('unknown' if item['price']=='unknown' else str(amounts[item['id']])))

mac=load(ROOT/f'research/{DAY}-mac.json')
mac_offer=mac['retailer_observation']
mac_capture=next(cap for cap in groups['p'] if cap['url']==mac_offer['url'])
mac_visible=''.join(unicodedata.normalize('NFKC',mac_capture['text']).split())
checked('separate exact Mac retailer price','54499,00' in mac_visible or '54499.00' in mac_visible)
checked('Mac target memory not core count',mac['memory_request']['original_gb']==86 and [target['unified_memory_gb'] for target in mac['targets']]==[96,256])
checked('Apple configured prices not extrapolated',all(target['apple_standard_configured_pln']=='unknown' and target['apple_education_configured_pln']=='unknown' for target in mac['targets']))
checked('Mac retailer not Apple configured checkout',mac_offer['delivered_pln']=='unknown' and mac_offer['education_configured_pln']=='unknown')

report_path=ROOT/f'reports/{DAY}.md'
report=report_path.read_text()
readme=(ROOT/'README.md').read_text()
required=['## Headline','## Table A','## Table C','## Table B','## Compact comparison','## Platform-only costs','## Architecture advantages','## Independent price history','## Detailed observations']
positions=[report.index(text) for text in required]
checked('AGENTS report section order',positions==sorted(positions))
checked('RAM exact alert string','THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.' in report)
for token in ('x8/x8','M2A_CPU','M2C_SB','M2B_CPU','M2D_SB','M2E_SB','M2D_CPU','BK02','55mm','52mm','1.08A','F8','700W','48GB','12-month','30-minute','36/80','96GB','86GB','Education','NNN'):
    if token!='NNN':
        checked('compatibility/evidence requirement '+token,token in report)
checked('official Mac configured prices unknown','exact configured 96GB price **unknown**' in report and 'exact 256GB price **unknown**' in report)
checked('all reference totals visible',all(f'{value:,.2f}' in report for value in (A,A2,B1,B2,platformA,platformB,nonGPU,Cinvalid)))
for track in ('A','B1','B2'):
    history=ledger['history'][track]
    series=history['series']
    vals=[D(point['reference_pln']) for point in series]
    checked('independent extrema '+track,D(history['minimum_reference'])==min(vals) and D(history['maximum_reference'])==max(vals))
    checked('independent deltas '+track,D(history['weekly_reference_change'])==q(vals[-1]-vals[-2]) and D(history['first_to_current_reference_change'])==q(vals[-1]-vals[0]))
    checked('independent percentages '+track,D(history['weekly_reference_pct'])==q((vals[-1]-vals[-2])/vals[-2]*100) and D(history['first_to_current_reference_pct'])==q((vals[-1]-vals[0])/vals[0]*100))
    for point in series[:-1]:
        historical_report=(ROOT/f"reports/{point['date']}.md").read_text()
        checked('history report '+track+' '+point['date'],f"{D(point['reference_pln']):,.2f}" in historical_report)
    for days in ('30','90'):
        start=date.fromisoformat(DAY)-timedelta(days=int(days))
        subset=[p for p in series if start<=date.fromisoformat(p['date'])<=date.fromisoformat(DAY)]
        subset_values=[D(p['reference_pln']) for p in subset]
        window=history['windows'][days]
        checked('window bounds/count '+track+' '+days,window['start']==str(start) and window['observations']==len(subset))
        checked('window extrema/change '+track+' '+days,D(window['minimum_reference_pln'])==min(subset_values) and D(window['maximum_reference_pln'])==max(subset_values) and D(window['change_from_first_available_pln'])==q(vals[-1]-subset_values[0]))
c_history=ledger['history']['C']
checked('C no qualified history',all(c_history[key] is None for key in ('current_qualified_total','fit_validated_total','qualified_minimum','qualified_maximum','weekly_qualified_change','total_qualified_change')))
c_values=[D(point['pln']) for point in c_history['same_listing_asking_series']]
checked('C same-listing deltas',D(c_history['weekly_same_listing_ask_change'])==q(c_values[-1]-c_values[-2]) and D(c_history['first_same_listing_ask_change'])==q(c_values[-1]-c_values[0]))
checked('history not purchase-qualified','not a delivered-qualified price series' in report and 'unpublished local drafts' in report)

link_rx=re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
local_count=0
external=set()
for path in [ROOT/'README.md',report_path,ROOT/f'research/{DAY}-findings.md']:
    text=path.read_text()
    checked('no bare unavailable dash '+path.name,not re.search(r'\|\s*[—–]\s*\|',text))
    for label,target in link_rx.findall(text):
        parts=urlparse(target)
        if parts.scheme:
            checked('HTTPS link '+path.name+' '+target,parts.scheme=='https')
            external.add(target)
        else:
            dest=unquote(target.split('#')[0])
            if dest:
                checked('local link exists '+target,(path.parent/dest).resolve().exists())
                local_count+=1
for line in readme.splitlines():
    if not line.startswith('|'):
        continue
    without=link_rx.sub('',line)
    checked('all README matrix currency amounts clickable',not re.search(r'\d[\d,. ]*\s*(?:PLN|EUR|zł|€)',without))
    for label,target in link_rx.findall(line):
        if re.search(r'\d[\d,. ]*\s*(?:PLN|EUR|zł|€)',label):
            checked('matrix price direct retailer or report '+target,('/reports/' in '/'+target or target.startswith('https://')) and not any(host in target for host in ('geizhals.','ceneo.')))
checked('README current plus all archived matrices dated',f'Latest: **[{DAY} report]' in readme and 'October 25 archived' in readme and 'October 18 archived' in readme and 'October 11 archived' in readme)

capture_list=[item for values in groups.values() for item in values]
status=Counter(item.get('http','retrieval_error').split()[0] for item in capture_list)
# Classify HTTP failures without pretending all public links are healthy.
source_states=[]
for item in capture_list:
    result='fetched'
    final_url=item.get('final_url',item.get('http','').split(' ',1)[-1])
    if item.get('error') or not item.get('http','').startswith('200 '):
        result='failed_or_blocked'
    elif final_url.split('?')[0] in ('https://www.krsystem.pl/','https://www.krsystem.pl'):
        result='generic_homepage_not_product'
    elif 'captcha' in final_url.lower():
        result='challenge_not_product'
    source_states.append({'url':item['url'],'http':item.get('http','retrieval_error'),'state':result})
summary={'date':DAY,'state':'passed','checks':len(checks),'json_files':len(json_files),'observations':len(observations),'appended_rows':len(new),'historical_prefix_sha256':hashlib.sha256(prefix).hexdigest(),'captures':len(capture_list),'capture_status_counts':dict(sorted(status.items())),'reviewed_offers':len(byid),'local_links_checked':local_count,'distinct_external_links':len(external),'remote_link_note':'Remote capture states retained; historical or indexed-only URLs not asserted healthy; no live order/delivery verification.','reference_totals':{'A':str(A),'A_two_theoretical':str(A2),'B1':str(B1),'B2':str(B2),'C_current':'incomplete','C_fit_validated':'incomplete'},'source_states':source_states}
(ROOT/f'research/{DAY}-validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({key:value for key,value in summary.items() if key!='source_states'},indent=2))
