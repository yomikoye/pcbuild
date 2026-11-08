"""Independent November 8 publication gate; no network or external-state changes.
Writes only the dated validation ledger after all assertions pass.
"""
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
DAY='2026-11-08'
q=lambda x:D(x).quantize(D('.01'),rounding=ROUND_HALF_UP)
load=lambda p:json.loads(p.read_text(),parse_float=D)
checks=[]
def check(name,condition):
    assert condition,name
    checks.append(name)

json_paths=sorted(ROOT.glob('research/*.json'))+[ROOT/'monitor-config.json']
for path in json_paths:
    load(path)
check('all research/config JSON parses',True)
manifest=load(ROOT/f'research/{DAY}-offers.json')
calc=load(ROOT/f'research/{DAY}-calculations.json')
config=load(ROOT/'monitor-config.json')
groups={k:load(ROOT/f'research/{d}{s}-http.json') for k,d,s in [('p',DAY,''),('f',DAY,'-followup'),('s',DAY,'-specs'),('old','2026-11-01','')]}
byid={x['id']:x for x in manifest['offers']+manifest['references']}
check('unique offer IDs',len(byid)==len(manifest['offers'])+len(manifest['references']))
fx=json.loads(groups['p'][49]['text'],parse_float=D)['rates'][0]
check('NBP last business day explicit',fx['effectiveDate']=='2026-11-06' and fx['mid']==D('4.3925'))
rate=fx['mid']
def source(x):
    group,i=x['capture'].split(':')
    return groups[group][int(i)]
def metadata_prices(node):
    if isinstance(node,dict):
        for key,value in node.items():
            if key=='price':
                try:yield q(value)
                except Exception:pass
            else:yield from metadata_prices(value)
    elif isinstance(node,list):
        for child in node:yield from metadata_prices(child)
amounts={}
for key,x in byid.items():
    cap=source(x)
    check('dated capture '+key,cap['retrieved_at'].startswith('2026-11-01' if x['capture'].startswith('old:') else DAY))
    check('successful priced product HTTP '+key,cap['http'].startswith('200 ') and not cap.get('error'))
    identity=cap['text']+json.dumps(cap.get('products',[]),default=str)
    if key not in ('pairOld','pairNew'):
        check('exact identity '+key,x['sku'] in identity or x['product'] in identity)
    if x['seller']=='Morele.net Sp. z o.o.':
        check('visible direct seller '+key,'Sprzedaje i wysyła przedsiębiorca:\nMorele.net\n' in cap['text'])
    if x['price']=='unknown':continue
    value=q(x['price'])
    normalized=''.join(unicodedata.normalize('NFKC',cap['text']).split())
    tokens={str(value),str(value).replace('.',','),f'{value:,.2f}',f'{value:,.2f}'.replace(',','@').replace('.',',').replace('@','.')}
    if value==value.to_integral_value():tokens.update({f'{value:.0f}zł',f'{value:.0f}€',f'€{value:.0f}'})
    check('exact source amount '+key,value in set(metadata_prices(cap.get('products',[]))) or any(t in normalized for t in tokens))
    check('explicit known currency '+key,x['currency'] in ('PLN','EUR'))
    amounts[key]=q(value*(rate if x['currency']=='EUR' else D(1)))

# Independent platform-first recomputation, not importing the publisher.
ram=q(D(byid['ramA']['price'])*D(123)/D(119)*rate)
platformA=sum(amounts[k] for k in ('cpuA','boardA','coolA','caseA'))+ram
platformB=sum(amounts[k] for k in ('cpuB','boardB','ramB','coolB','caseB'))
non=platformA+amounts['psu']+amounts['ssd']*2+amounts['fan140']*6+amounts['fan120']*6
A=non+amounts['gpu']
B1=platformB+amounts['gpu']+amounts['psu']+amounts['ssd']+amounts['ssdB2']+amounts['fan140']*8
B2=B1-amounts['psu']+amounts['b2']
expected={'A':A,'A_two':A+amounts['gpu'],'C_non_gpu':non,'B1':B1,'B2':B2,'B1_two':B1+amounts['gpu'],
          'platform_A_C':platformA,'platform_B':platformB,'platform_premium':platformA-platformB,'platform_premium_pct':(platformA-platformB)/platformB*100,
          'A_over_B1':A-B1,'A_over_B1_pct':(A-B1)/B1*100,'A_over_B2':A-B2,'A_over_B2_pct':(A-B2)/B2*100,
          'cpu_alternative_premium':amounts['cpuAlt']-amounts['cpuB'],'cpu_alternative_premium_pct':(amounts['cpuAlt']-amounts['cpuB'])/amounts['cpuB']*100,
          'cpuAlt_same_seller_weekly_change':amounts['cpuAlt']-D('3951.74'),'cpuAlt_same_seller_weekly_pct':(amounts['cpuAlt']-D('3951.74'))/D('3951.74')*100,
          'A_value_ram_scenario':A-ram+amounts['ramValue'],'A_value_ram_difference':ram-amounts['ramValue'],'A_fan120_group_reference':amounts['fan120']*6,
          'C_nominal_GPU_heat_W':D(700),'A2_reference_GPU_heat_W':D(1150),'AW420_stack_mm':D(52),'AW420_nominal_margin_mm':D(13),'AW420_group_current_A':D('1.08')}
check('every independent Decimal result', {k:q(v) for k,v in expected.items()}=={k:D(v) for k,v in calc['results_pln'].items()})
for track,quantities,component_amounts in [('A',calc['A_quantities'],calc['A_amounts_pln']),('B1',calc['B1_quantities'],calc['B1_amounts_pln'])]:
    for key,n in quantities.items():
        check('component arithmetic '+track+' '+key,D(component_amounts[key])==q((ram if key=='ramA' else amounts[key])*n))
check('quantities preserve separate PSU cases',calc['B1_quantities']['psu']==1 and 'b2' not in calc['B1_quantities'])
check('historical PSU explicit',byid['psu']['capture']=='old:19' and 'Historical November 1' in byid['psu']['stock'])
check('current unqualified PSU not in basket','psuMarket' not in calc['A_quantities'] and 'psuMarket' not in calc['B1_quantities'])
check('all delivered totals unknown',calc['delivered_totals']=='unknown')
check('C current fit savings not fabricated',calc['C_current']=='incomplete' and calc['C_fit_validated']=='incomplete' and calc['C_savings_A1_A2'].startswith('undefined'))
check('PRIME exact EAN and revision',byid['psu']['sku']=='PRIME-PX-2200-ATX30' and '4711173878414' in byid['psu']['notes'])
check('B2 exact revision not upgraded','ATX 3.0' in byid['b2']['sku'] and '4711173877721' in byid['b2']['notes'])
check('pair ended notice today and prior', 'Przedmiot został sprzedany' in source(byid['pairOld'])['text'] and 'Przedmiot został sprzedany' in groups['old'][40]['text'])

raw=(ROOT/'data/observations.csv').read_bytes()
baseline=subprocess.check_output(['git','show',manifest['baseline_commit']+':data/observations.csv'],cwd=ROOT)
check('append-only full committed historical prefix',raw.startswith(baseline))
rows=list(csv.reader(io.StringIO(raw.decode())))
check('CSV fixed width',all(len(row)==len(rows[0]) for row in rows[1:]))
obs=list(csv.DictReader(io.StringIO(raw.decode())))
new=[row for row in obs if row['observed_at']==DAY]
check('exact dated append count',len(new)==len(manifest['offers'])==calc['current_observation_count'])
check('no unintended older observations appended',len(obs)==len(list(csv.DictReader(io.StringIO(baseline.decode()))))+len(new))
check('new rows LF only',b'\r' not in raw[len(baseline):])
for row in obs:
    date.fromisoformat(row['observed_at'])
    for key in ('price','pln_price','delivered_pln'):
        if row[key] not in ('unknown',''):D(row[key])
check('CSV all dates and numeric fields parse',True)
for row in new:
    check('dated rows track and delivered unknown',row['category'].startswith(('Track A ','Track B ','Track C ')) and row['delivered_pln']=='unknown')
for x in manifest['offers']:
    matches=[r for r in new if r['source_url']==source(x)['url'] and r['sku']==x['sku']]
    check('new row unique identity '+x['id'],len(matches)==1)
    row=matches[0]
    check('new row source amount '+x['id'],row['price']==('unknown' if x['price']=='unknown' else str(q(x['price']))))
    check('new row PLN FX '+x['id'],row['pln_price']==('unknown' if x['price']=='unknown' else str(amounts[x['id']])))

# Cross-check launch alternative's claimed recorded low against all prior observations.
prior=[D(r['price']) for r in obs if r['observed_at']<DAY and r['sku']=='100-100001978WOF' and r['currency']=='PLN' and r['price']!='unknown']
check('CPU alternative new recorded asking-price low',prior and amounts['cpuAlt']<min(prior))
A_products={p['category']:p for p in config['tracks']['A_threadripper']['products']}
B_products={p['category']:p for p in config['tracks']['B_am5_value']['products']}
check('locked architectures capacities primary CPU','128GB' in A_products['RAM']['primary'] and '128GB' in B_products['RAM']['primary'] and B_products['CPU']['primary_sku']=='100-100000719WOF' and config['tracks']['C_threadripper_dual_3090']['locked_capacity_gb']==128)
check('C full A inheritance',config['tracks']['C_threadripper_dual_3090']['inherits_platform_from']=='A_threadripper')
check('separate Mac prices not inferred',all(config['integrated_mac_comparison']['latest_check'][k]=='unknown' for k in ('apple_standard_96gb_configured_pln','apple_education_96gb_configured_pln','apple_standard_256gb_configured_pln','apple_education_256gb_configured_pln')))
mac_cap=groups['p'][56]
check('exact separate Mac identity and visible delay','MHL64ZE/A/P3/R5/D1' in mac_cap['text'] and '2-8 tygodni' in mac_cap['text'] and '54\u00a0499,00' in mac_cap['text'])

report_path=ROOT/f'reports/{DAY}.md'
report=report_path.read_text();readme=(ROOT/'README.md').read_text()
required=['## Headline','## Table A','## Table C','## Table B','## Compact comparison','## Platform-only costs','## Architecture advantages','## Independent price history','## Detailed observations']
positions=[report.index(s) for s in required]
check('all AGENTS sections in required order',positions==sorted(positions))
check('all headline and platform totals visible',all(f'{v:,.2f}' in report for v in (A,A+amounts['gpu'],B1,B2,B1+amounts['gpu'],platformA,platformB,non)))
for text in ('THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.','M2A_CPU','M2C_SB','M2B_CPU','M2D_SB','M2E_SB','M2D_CPU','PCIEX4','x8/x8','not x16/x16','F8','55mm','52mm','1.08A','BK02','quad-channel','dual-channel','12-month','30-minute','700W','48GB','96GB','86GB','Education','2–8','door-to-door','not a delivered-qualified price series'):
    check('required audit statement '+text,text in report)
check('no unqualified current C sticker arithmetic','C_unqualified_stickers_no_loop' not in calc['results_pln'] and 'current_pair_ask' in calc['history']['C'])
for track in ('A','B1','B2'):
    h=calc['history'][track];series=h['series'];vals=[D(p['reference_pln']) for p in series]
    check('history extrema '+track,D(h['minimum'])==min(vals) and D(h['maximum'])==max(vals))
    check('history independent deltas '+track,D(h['weekly_change'])==q(vals[-1]-vals[-2]) and D(h['total_change'])==q(vals[-1]-vals[0]))
    check('history independent percentages '+track,D(h['weekly_pct'])==q((vals[-1]-vals[-2])/vals[-2]*100) and D(h['total_pct'])==q((vals[-1]-vals[0])/vals[0]*100))
    for point in series[:-1]:check('history dated report '+track+' '+point['date'],f"{D(point['reference_pln']):,.2f}" in (ROOT/f"reports/{point['date']}.md").read_text())
    for days,w in h['windows'].items():
        start=date.fromisoformat(DAY)-timedelta(days=int(days))
        subset=[p for p in series if start<=date.fromisoformat(p['date'])<=date.fromisoformat(DAY)]
        sv=[D(p['reference_pln']) for p in subset]
        check('window dates count '+track+' '+days,w['start']==str(start) and w['observations']==len(subset) and w['first_available']==subset[0]['date'])
        check('window arithmetic '+track+' '+days,D(w['minimum'])==min(sv) and D(w['maximum'])==max(sv) and D(w['change_from_first_available'])==q(vals[-1]-sv[0]))
check('C independent qualified history remains absent',all(calc['history']['C'][k] is None for k in ('current_qualified_total','fit_validated_total','minimum_qualified_total','maximum_qualified_total','weekly_qualified_change','total_qualified_change')))

# Validate Markdown local files and fragment destinations; all matrix amounts clickable.
link_rx=re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
def slug(text):
    text=text.lower().replace('`','')
    text=re.sub(r'[^\w\- ]','',text,flags=re.UNICODE)
    return text.replace(' ','-')
externals=set();local_count=0
for path in (ROOT/'README.md',report_path,ROOT/f'research/{DAY}-findings.md'):
    text=path.read_text()
    check('no bare unavailable dash '+path.name,not re.search(r'\|\s*[—–]\s*\|',text))
    for label,target in link_rx.findall(text):
        parts=urlparse(target)
        if parts.scheme:
            check('HTTPS only external '+target,parts.scheme=='https')
            externals.add(target)
        else:
            dest=unquote(target.split('#')[0])
            destination=(path.parent/dest).resolve() if dest else path
            # The validator emits this exact artifact only after all gates pass.
            # Other missing links still fail; no placeholder success file is written.
            check('local target '+target,destination.exists() or destination==ROOT/f'research/{DAY}-validation.json')
            if parts.fragment and destination.suffix=='.md':
                headings={slug(line.lstrip('#').strip()) for line in destination.read_text().splitlines() if line.startswith('#')}
                check('local fragment '+target,unquote(parts.fragment) in headings)
            local_count+=1
for line in readme.splitlines():
    if line.startswith('|'):
        check('README currency amounts clickable',not re.search(r'\d[\d,. ]*\s*(?:PLN|EUR|zł|€)',link_rx.sub('',line)))
        for label,target in link_rx.findall(line):
            if re.search(r'\d[\d,. ]*\s*(?:PLN|EUR|zł|€)',label):
                check('matrix direct product/report link',target.startswith('https://') or target.startswith('reports/'))
                check('no aggregator masquerading as seller',not any(host in target for host in ('geizhals.','ceneo.')))
check('README latest and archives retained',f'Latest: **[{DAY} report]' in readme and 'November 1 archived' in readme and 'October 25 archived' in readme and 'October 18 archived' in readme)

captures=[cap for key,items in groups.items() if key!='old' for cap in items]
statuses=Counter(cap.get('http','error').split()[0] for cap in captures)
source_states=[]
for cap in captures:
    state='fetched_public_HTML_not_order_verified'
    if cap.get('error') or not cap.get('http','').startswith('200 '):state='failed_or_blocked'
    elif len(cap.get('text','').splitlines())<3:state='empty_or_JS_shell_not_product_evidence'
    elif 'Przedmiot został sprzedany' in cap.get('text',''):state='sold_ended_notice_conflicts_with_retained_controls_not_live_offer'
    source_states.append({'url':cap['url'],'http':cap.get('http'),'state':state})
lookup={x['url']:x['state'] for x in source_states}
external_states=[{'url':url,'state':lookup.get(url,'historical_or_indexed_only_not_live_checked_this_run')} for url in sorted(externals)]
result={'date':DAY,'state':'passed','checks':len(checks),'json_files':len(json_paths),'observations':len(obs),'appended_rows':len(new),
        'historical_prefix_sha256':hashlib.sha256(baseline).hexdigest(),'captures':len(captures),'http_status_counts':dict(statuses),'local_links_checked':local_count,
        'distinct_external_links':len(externals),'reference_totals':{k:str(q(expected[k])) for k in ('A','A_two','B1','B2','B1_two','platform_A_C','platform_B')},
        'weekly_reference_deltas':{k:calc['history'][k]['weekly_change'] for k in ('A','B1','B2')},
        'CPU_alternative_prior_min_PLN':str(min(prior)),'CPU_alternative_current_PLN':str(amounts['cpuAlt']),
        'C_current':'incomplete','C_fit_validated':'incomplete','delivered_totals':'unknown','source_states':source_states,'external_link_states':external_states}
(ROOT/f'research/{DAY}-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
load(ROOT/f'research/{DAY}-validation.json')
print(json.dumps({k:v for k,v in result.items() if k not in ('source_states','external_link_states')},indent=2))
