"""Validate the dated weekly publication and historical prefix; does not modify repository."""
import csv
import json
import re
import subprocess
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlsplit
root=Path(__file__).resolve().parents[1]
date='2026-09-27'
ledger=json.loads((root/f'research/{date}-calculations.json').read_text())
config=json.loads((root/'monitor-config.json').read_text());assert config['tracks']['C_threadripper_dual_3090']['locked_capacity_gb']==128
for p in (root/'research').glob(f'{date}-*.json'):json.loads(p.read_text())
old=subprocess.check_output(['git','show','HEAD:data/observations.csv'],cwd=root,text=True)
new=(root/'data/observations.csv').read_text();assert new.startswith(old),'historical observations altered'
rows=list(csv.DictReader(new.splitlines()));fields=list(rows[0]);assert all(set(r)==set(fields) and None not in r for r in rows)
today=[r for r in rows if r['observed_at']==date];assert len(today)==30
assert all(r['category'].startswith(('Track A','Track B','Track C')) and r['delivered_pln']=='unknown' and r['source_url'].startswith('https://') for r in today)
assert sum(r['category'].startswith('Track C') for r in today)>=5
inputs={k:D(v) for k,v in ledger['unit_inputs'].items()}
T=ledger['totals_product_only']
calc=lambda quantities:sum((inputs[k]*v for k,v in quantities.items()),D(0)).quantize(D('.01'),rounding=ROUND_HALF_UP)
assert calc(ledger['quantities']['A'])==D(T['A'])
assert calc(ledger['quantities']['B1'])==D(T['B1'])
assert D(T['B2'])==D(T['B1'])-inputs['psu']+inputs['psuB2']
assert D(T['A_two_theoretical'])==D(T['A'])+inputs['gpu']
assert D(T['B1_two_theoretical'])==D(T['B1'])+inputs['gpu']
assert D(T['A_non_gpu_reference'])==D(T['A'])-inputs['gpu']
assert calc({k:1 for k in ('cpuA','boardA','ramA_pl','coolA','caseA')})==D(T['A_C_platform_only'])
assert calc({k:1 for k in ('cpuB','boardB','ramB','coolB','caseB')})==D(T['B_platform_only'])
assert T['C_current'] is None and T['C_fit_validated'] is None
assert (inputs['ramA']/D('1.19')*D('1.23')*D(ledger['fx']['EUR_PLN'])).quantize(D('.01'),rounding=ROUND_HALF_UP)==inputs['ramA_pl']
readme=(root/'README.md').read_text();report=(root/f'reports/{date}.md').read_text()
for heading in ('Headline and RAM anomaly state','Table A','Table C','Table B','Compact equal-128GB comparison','Platform-only','Threadripper premium','Architecture advantages','Detailed observations','Independent price history'):
    assert heading in report,heading
assert all(report.index(h)<report.index(j) for h,j in [('## Table A','## Table C'),('## Table C','## Table B'),('## Table B','## Compact'),('## Compact','## Platform-only')])
assert 'THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.' in readme and report
for k in ('A','A_two_theoretical','A_non_gpu_reference','B1','B2','B1_two_theoretical','A_C_platform_only','B_platform_only'):
    assert f'{D(T[k]):,.2f}' in report,(k,T[k])
assert '48GB aggregate' in report and 'x8/x8' in report and 'M2A_CPU' in report
for text in (readme,report):
    for label,link in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',text):
        if link.startswith('https://'):
            assert urlsplit(link).hostname,(label,link)
        elif not link.startswith('#'):
            assert (root/'README.md').parent.joinpath(link).exists() if text==readme else (root/'reports').joinpath(link).exists(),(label,link)
for section in ('Track A —','Track C —','Track B —'):
    assert section in readme
# Check every current Markdown matrix row retains fixed-width cells (URLs contain no pipe).
for text in (readme,report):
    group=[]
    for line in text.splitlines()+['']:
        if line.startswith('|'):
            group.append(line)
        elif group:
            widths={len(x.split('|')) for x in group}
            assert len(widths)==1,(group[0][:80],widths)
            group=[]
for line in readme.splitlines():
    if line.startswith('| Component | Qty |') or line.startswith('| Component / state | Qty |'):
        assert line.count('| 2026-09-27 |')==1,line
        assert '| |' not in line
    if line.startswith('| **') and ('total' in line.lower() or 'state' in line.lower()):assert f'](reports/{date}.md)' in line,line
print(json.dumps({'status':'ok','new_observations':len(today),'history_rows':len(rows)-len(today),'totals':T,'json_files':len(list((root/'research').glob(f'{date}-*.json')))},indent=2))
