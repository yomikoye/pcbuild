"""Oct 11 publication gates; call from repository root on main."""
import csv
import json
from decimal import Decimal as D
from pathlib import Path
import re
import subprocess
root = Path(__file__).resolve().parents[1]
raw = (root/'data/observations.csv').read_text()
rows = list(csv.reader(raw.splitlines()))
assert all(len(r) == len(rows[0]) == 17 for r in rows), [(i,len(r)) for i,r in enumerate(rows,1) if len(r)!=17]
prior = subprocess.check_output(['git','show','HEAD:data/observations.csv'],cwd=root,text=True)
assert raw.startswith(prior), 'Historical CSV was rewritten'
assert sum(r[0]=='2026-10-11' for r in rows[1:]) >= 20
for f in (root/'monitor-config.json',*root.glob('research/2026-10-11-*.json')):
    json.loads(f.read_text())
ledger = json.loads((root/'research/2026-10-11-calculations.json').read_text())
a = {k:D(v) for k,v in ledger['inputs_A'].items()}
b = {k:D(v) for k,v in ledger['inputs_B'].items()}
assert D(ledger['A_one']) == sum(a.values())
assert D(ledger['C_non_gpu']) == sum(a.values())-a['gpu_sold_out']
assert D(ledger['B1_one']) == sum(b.values()) + a['psu']
assert D(ledger['B2_one']) == sum(b.values()) + D('1179')
assert D(ledger['A_two_theoretical']) == D(ledger['A_one'])+a['gpu_sold_out']
assert D(ledger['B1_two_theoretical']) == D(ledger['B1_one'])+b['gpu_sold_out']
assert D(ledger['platform_A_C']) == sum(a[x] for x in ('cpu','board','ram','cooler','case'))
assert D(ledger['platform_B']) == sum(b[x] for x in ('cpu_prior_direct_2026_09_27','board','ram','cooler','case_prior_direct_2026_09_27'))
assert D(ledger['platform_premium_pln']) == D(ledger['platform_A_C'])-D(ledger['platform_B'])
assert D(ledger['ram_german_vat_pln']) == (D('5866')*D('4.3775')).quantize(D('.01'))
for path in (root/'README.md',root/'reports/2026-10-11.md'):
    text = path.read_text()
    for url in re.findall(r'\]\(([^)]+)\)',text):
        if not url.startswith(('https://','http://','#')):
            assert (path.parent/url).exists(), (path,url)
    assert 'THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.' in text if 'reports/' in str(path) else True
report = (root/'reports/2026-10-11.md').read_text()
for key in ('Table A','Table C','Table B','Compact comparison','Platform','historical context','Mac Studio'):
    assert key.lower() in report.lower(),key
readme = (root/'README.md').read_text().split('## October 4 archived evidence')[0]
for line in readme.splitlines():
    if line.startswith('|') and 'PLN' in line:
        assert '](' in line,line
assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='main'
print('PASS: CSV append-only/fixed width, JSON, arithmetic, report sections, README current price links, local links, main')
