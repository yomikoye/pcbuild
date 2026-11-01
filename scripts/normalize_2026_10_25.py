"""Normalize only newly appended 2026-10-25 CSV lines to LF; preserve history byte-for-byte."""
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'data/observations.csv'
data = p.read_bytes()
needle = b'2026-10-25,Track A CPU,'
pos = data.index(needle)
assert data[:pos].endswith(b'\n') and data[pos:].count(b'\r\n') == 23
assert b'\r\n' not in data[:pos] or data[:pos].endswith(b'\r\n')
p.write_bytes(data[:pos] + data[pos:].replace(b'\r\n', b'\n'))
print('Preserved historical prefix and normalized 23 new rows')
