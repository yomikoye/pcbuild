"""Validate 2026-10-18 publication without changing repository content."""
import csv
import json
import re
import subprocess
from decimal import Decimal as D
from pathlib import Path
from urllib.parse import urlsplit

root = Path(__file__).resolve().parents[1]
original = subprocess.check_output(['git', 'show', 'HEAD:data/observations.csv'], cwd=root)
current = (root/'data/observations.csv').read_bytes()
assert current.startswith(original), 'Historical CSV was changed'
with (root/'data/observations.csv').open(newline='') as f:
    rows = list(csv.reader(f))
assert all(len(r) == 17 for r in rows)
new = [r for r in rows[1:] if r[0] == '2026-10-18']
assert len(new) == 23
assert all(r[1].startswith(('Track A ', 'Track B ', 'Track C ')) and r[11] == 'unknown' and r[15].startswith('https://') for r in new)
for p in (root/'research').glob('2026-10-18*.json'):
    json.loads(p.read_text())
json.loads((root/'monitor-config.json').read_text())
ledger = json.loads((root/'research/2026-10-18-calculations.json').read_text())
rate = D(ledger['eur_pln_nbp_oct16'])
assert rate == D('4.3661')
assert (D('5866')*rate).quantize(D('.01')) == D(ledger['g5_converted_german_gross_pln'])
assert (D('5866')/D('1.19')*D('1.23')*rate).quantize(D('.01')) == D(ledger['g5_illustrative_polish_23pct_pln'])
assert (D('499.95')*rate).quantize(D('.01')) == D(ledger['case_french_gross_pln'])
by_sku = {}
for r in new:
    by_sku.setdefault(r[3], r)
pl = lambda sku: D(by_sku[sku][8])
a = (pl('100-100001595WOF') + D('4409.99') + D(ledger['g5_illustrative_polish_23pct_pln']) + pl('CL-W445-PL14BL-A') + D(ledger['case_french_gross_pln']))
assert a == D(ledger['a_c_platform_only'])
non_gpu = a + pl('PRIME-PX-2200-ATX30') + pl('MZ-VAP4T0BW')*2 + pl('NF-A14x25 G2 PWM CH.BK')*6 + pl('NF-A12x25 G2 PWM chromax.black')*6
assert non_gpu == D(ledger['a_c_non_gpu'])
gpu = D('33945.84')
assert non_gpu + gpu == D(ledger['a_one_5090'])
assert non_gpu + gpu*2 == D(ledger['a_theoretical_two_5090'])
b = D('2669') + D('2102.99') + D('13098.98') + D('1670.16') + D('1139')
assert b == D(ledger['b_platform_only'])
b1 = b + gpu + D('2499') + D('4026.61') + D('3238.55') + D('169.86')*8
assert b1 == D(ledger['b1_one_5090'])
assert b1-D('2499')+D('1053.95') == D(ledger['b2_one_5090'])
assert D(ledger['platform_premium_pln']) == a-b
assert D(ledger['c_unqualified_pair_hardware_only']) == non_gpu+D('13050')
report = (root/'reports/2026-10-18.md').read_text()
readme = (root/'README.md').read_text()
for key in ('a_one_5090','b1_one_5090','b2_one_5090','a_c_platform_only','b_platform_only'):
    formatted = f'{D(ledger[key]):,.2f}'
    assert formatted in report and formatted in readme, (key, formatted)
assert 'THREADRIPPER TOTAL CURRENTLY DISTORTED BY RAM AVAILABILITY.' in report
assert '2026-10-18' in readme
for doc in (report,readme):
    for label, target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',doc):
        if target.startswith('http'):
            assert urlsplit(target).scheme == 'https', target
        elif target.startswith('#'):
            pass
        else:
            path = (root/'reports'/target if doc is report else root/target).resolve()
            assert path.exists(), (label,target)
# Current-table numeric component prices must be clickable, no naked price placeholder.
current_matrix = readme.split('## October 18 current evidence matrix')[1].split('## Separate Apple')[0]
assert '| — |' not in current_matrix
assert len(re.findall(r'\]\(https://',current_matrix)) > 20
print('Validated append-only CSV, exact 23 rows, all JSON, independent Decimal baskets, report, README and local links.')
