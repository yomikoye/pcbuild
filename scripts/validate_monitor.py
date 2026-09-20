"""Validate recovered publication without network access or changing tracked data.
Usage: python3 scripts/validate_monitor.py [baseline-commit]
Outputs a JSON validation ledger to stdout. Baseline defaults to HEAD before commit.
"""
import csv
import io
import json
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]
DATE='2026-09-20'
BASE=sys.argv[1] if len(sys.argv)>1 else 'HEAD'
def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args])
def q(n): return n.quantize(D('.01'),rounding=ROUND_HALF_UP)

def main():
    baseline=git('rev-parse',BASE).decode().strip()
    json_paths=list(ROOT.glob('*.json'))+list((ROOT/'research').glob('*.json'))
    for p in json_paths:
        if p.name == DATE+'-validation.json':
            continue  # This invocation's output may be shell-redirected here.
        json.loads(p.read_text())
    data=(ROOT/'data/observations.csv').read_bytes();previous=git('show',BASE+':data/observations.csv')
    assert data.startswith(previous), 'Historical CSV changed'
    rows=list(csv.reader(io.StringIO(data.decode()),strict=True));assert all(len(r)==17 for r in rows)
    observations=list(csv.DictReader(io.StringIO(data.decode())))
    fresh=[r for r in observations if r['observed_at']==DATE]
    assert fresh and all(r['category'].startswith(('Track A','Track B','Track C')) for r in fresh)
    for r in fresh:
        assert all(v!='' for v in r.values()),r
        for f in ['price','pln_price','delivered_pln']:
            assert r[f]=='unknown' or D(r[f])>=0
        assert r['source_url'].startswith('https://')
        if r['shipping_to_poland']=='unknown': assert r['delivered_pln']=='unknown'
    for p in sorted((ROOT/'reports').glob('2026-08-*.md')):
        assert p.read_bytes()==git('show',BASE+':'+str(p.relative_to(ROOT))),p
    c=json.loads((ROOT/'research'/f'{DATE}-calculations.json').read_text());x=c['inputs'];t={k:D(v) for k,v in c['totals'].items()}
    v=lambda k:D(x[k]['unit_pln'])
    a=sum(v(k)*r['qtyA'] for k,r in x.items());b=sum(v(k)*r['qtyB'] for k,r in x.items())
    assert a==t['A_reference'] and b==t['B1']
    assert b-v('psu')+v('psuB2')==t['B2']
    assert a+v('gpu')==t['A_theoretical_two_gpu']
    assert b+v('gpu')==t['B1_theoretical_two_gpu']
    assert a-v('gpu')==t['A_C_non_gpu_reference']
    assert sum(v(k) for k in ['cpuA','boardA','ramA','coolA','caseA'])==t['platform_A_C']
    assert sum(v(k) for k in ['cpuB','boardB','ramB','coolB','caseB'])==t['platform_B']
    for label,base in [('B1',b),('B2',t['B2'])]:
        assert a-base==t['A_premium_'+label]
        assert q((a/base-1)*100)==t['A_premium_'+label+'_percent']
    assert q((t['platform_A_C']/t['platform_B']-1)*100)==t['platform_premium_percent']
    assert t['platform_A_C']-t['platform_B']==t['platform_premium']
    assert q(D('5488')/D('1.19')*D('1.23')*D(c['fx_eur_pln']))==v('ramA')
    assert D('3914.50')-v('cpuB')==t['9950X3D2_premium']
    assert q((D('3914.50')/v('cpuB')-1)*100)==t['9950X3D2_premium_percent']
    assert v('ramA')-D('3535.98')==t['conditional_ram_saving']
    assert v('gpu')-D('13150')==t['nonqualified_bundle_gpu_gap_one']
    assert v('gpu')*2-D('13150')==t['nonqualified_bundle_gpu_gap_two']
    assert c['C_current_qualifying_pair_total'] is None and c['C_fit_validated_pair_total'] is None
    for h in c['component_history']:
        assert D(h['current'])-D(h['previous'])==D(h['change_previous'])
        assert D(h['current'])-D(h['first'])==D(h['change_first'])
    report=(ROOT/'reports'/f'{DATE}.md').read_text();readme=(ROOT/'README.md').read_text()
    required=['Headline and RAM','Table A','Table C','Table B','Compact equal','Platform-only','Totals, Threadripper','Architecture advantages','Detailed observations','Independent history']
    positions=[report.index(h) for h in required];assert positions==sorted(positions)
    assert 'NARRATIVE_PLACEHOLDER' not in report
    for k in ['A_reference','B1','B2','A_theoretical_two_gpu','B1_theoretical_two_gpu','platform_A_C','platform_B']:
        assert f'{t[k]:,.2f}' in report and f'{t[k]:,.2f}' in readme,k
    assert 'THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.' in report
    # Every history row keeps the original cells and appends a dated column.
    old_readme=git('show',BASE+':README.md').decode()
    def track_rows(text):
        active=False;result=[]
        for s in text.splitlines():
            if s.startswith('## '):active=s.startswith('## Track ')
            if active and s.startswith('|'):result.append(s)
        return result
    old_rows=track_rows(old_readme);new_rows=track_rows(readme);assert len(old_rows)==len(new_rows)
    for old,new in zip(old_rows,new_rows):
        assert new.startswith(old),('history cells changed',old,new)
        assert new.count('|')==old.count('|')+1
    # All table rows must match their table header; all README price amounts clickable.
    for text in [readme,report]:
        width=None
        for s in text.splitlines():
            if not s.startswith('|'):width=None;continue
            if width is None:width=s.count('|')
            assert s.count('|')==width,s
    link_rx=re.compile(r'\[([^\]]+)\]\(([^\s]+)\)')
    for s in readme.splitlines():
        if s.startswith('|'):
            remainder=link_rx.sub('',s)
            assert not re.search(r'\d[\d,.]*\s*PLN',remainder),s
    # Link syntax/local target audit, plus direct HTTP classification, not fictitious all-green live links.
    docs=[ROOT/'README.md',ROOT/'reports'/f'{DATE}.md',ROOT/'research'/f'{DATE}-memory.md',ROOT/'research'/f'{DATE}-track-c.md']
    links=set();local_count=0
    for p in docs:
        for _,u in link_rx.findall(p.read_text()):
            if u.startswith('https://'):
                z=urlsplit(u);assert z.hostname and not z.username and not z.password;links.add(u)
            elif not u.startswith('#'):
                assert (p.parent/unquote(u.split('#')[0])).exists(),(p,u)
                local_count+=1
    evidence={}
    for p in (ROOT/'research').glob(f'{DATE}-*http.json'):
        for r in json.loads(p.read_text()):evidence[r['url']]=r
    for k,r in x.items():
        assert r['source_url'] in evidence,k
        if r['source_date']==DATE:
            assert evidence[r['source_url']].get('http','').startswith('200 '),k
            current=[o for o in fresh if o['source_url']==r['source_url'] and o['pln_price']!='unknown']
            assert current,k
            if k!='ramA':assert any(D(o['pln_price'])==v(k) for o in current),k
    classification=[]
    for u in sorted(links):
        r=evidence.get(u)
        if not r:state='historical or indexed/research-note evidence; no persisted HTTP batch verification'
        elif 'Captcha' in r.get('http',''):state='challenge, not live offer verification'
        elif r.get('http','').startswith('200 '):state='fetched; offer meaning manually assessed in report'
        else:state='blocked/error/not found: '+r.get('http',r.get('error','unknown'))
        classification.append({'url':u,'state':state})
    subprocess.run(['git','-C',str(ROOT),'diff','--check'],check=True)
    result={'date':DATE,'baseline_commit':baseline,'result':'PASS','json_files':len(json_paths),'csv_rows':len(observations),'appended_rows':len(fresh),'historical_csv_prefix':'unchanged','historical_reports':'unchanged','README_historical_cells':'unchanged','arithmetic':'Decimal recomputed and cross-checked against observations','local_link_references_checked':local_count,'unique_external_links':len(links),'link_results':classification,'limitations':'HTTP blocks and indexed/historical links explicitly classified; not all external pages accessible. No checkout/hardware tests or unattended approval guarantee.'}
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
