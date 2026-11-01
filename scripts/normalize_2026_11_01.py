"""Correct only November 1 CSV newline encoding; preserve all prior evidence bytes."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/observations.csv'
data=p.read_bytes()
pos=data.index(b'2026-11-01,Track A CPU,')
assert data[:pos].endswith(b'\n')
assert data[pos:].count(b'\r\n')==32
p.write_bytes(data[:pos]+data[pos:].replace(b'\r\n',b'\n'))
print('Preserved historical prefix; normalized only 32 November 1 row terminators.')
