"""Validate both October reports and Oct 25 arithmetic/links against append-only evidence."""
import csv
import json
import re
import subprocess
from decimal import Decimal as D
from pathlib import Path
from urllib.parse import urlsplit

root=Path(__file__).resolve().parents[1]
original=subprocess.check_output(['git','show','HEAD:data/observations.csv'],cwd=root)
current=(root/'data/observations.csv').read_bytes()
assert current.startswith(original), 'Historical CSV changed'
with (root/'data/observations.csv').open(newline='') as f:
    rows=list(csv.reader(f))
assert len(rows)==256 and all(len(row)==17 for row in rows), 'CSV width/count'
new=[r for r in rows if r[0]=='2026-10-25']
assert len(new)==23 and all(r[1].startswith(('Track A ','Track B ','Track C ')) and r[11]=='unknown' and r[15].startswith('https://') for r in new)
assert any(r[1]=='Track C GPU advertised water-block pair' for r in new)
for p in (root/'research').glob('2026-10-*.json'):
    json.loads(p.read_text())
config=json.loads((root/'monitor-config.json').read_text())
assert config['tracks']['C_threadripper_dual_3090']['inherits_platform_from']=='A_threadripper'
ledger=json.loads((root/'research/2026-10-25-calculations.json').read_text())
val=lambda x: D(x.replace(',',''))
a=list(map(val,ledger['a_parts'])); b=list(map(val,ledger['b_parts']))
assert sum(a)==val(ledger['a_one_5090']) and sum(b[:-1])==val(ledger['b1_one_5090'])
assert sum(b[:-1])-b[-2]+b[-1]==val(ledger['b2_one_5090'])
assert sum(a)-a[3]==val(ledger['a_non_gpu'])
assert sum(a[i] for i in (0,1,2,4,5))==val(ledger['a_c_platform_only'])
assert sum(b[i] for i in (0,1,2,4,5))==val(ledger['b_platform_only'])
assert val(ledger['premium'])==val(ledger['a_c_platform_only'])-val(ledger['b_platform_only'])
assert (D('5866')/D('1.19')*D('1.23')*D('4.3917')).quantize(D('.01'))==a[2]
assert (D('499.95')*D('4.3917')).quantize(D('.01'))==a[5]
assert a[7]==D('4376.59')*2 and a[8]==D('169.99')*6 and a[9]==D('153.70')*6
assert b[6]==D('169.99')*8
assert ledger['c_current']==ledger['c_fit_validated']=='incomplete' and ledger['delivered_totals']=='unknown'
report=(root/'reports/2026-10-25.md').read_text(); readme=(root/'README.md').read_text()
for key in ('a_one_5090','b1_one_5090','b2_one_5090','a_c_platform_only','b_platform_only'):
    assert ledger[key] in report and ledger[key] in readme
assert report.index('## Table A')<report.index('## Table C')<report.index('## Table B')<report.index('## Compact')<report.index('## Architecture')
assert 'THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.' in report
for text,base in ((report,root/'reports'),(readme,root)):
    for label,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',text):
        if target.startswith('http'):
            assert urlsplit(target).scheme=='https',target
        elif not target.startswith('#'):
            assert (base/target).resolve().exists(),(label,target)
matrix=readme.split('## October 25 current evidence matrix')[1].split('## October 18 current evidence matrix')[0]
assert '| — |' not in matrix and len(re.findall(r'\]\(https://',matrix))>=15
assert 'incomplete' in matrix and 'x8/x8' in matrix
print('Validated Oct 25: 23 append-only rows, fixed CSV, JSON, Decimal totals, full report, README links.')
