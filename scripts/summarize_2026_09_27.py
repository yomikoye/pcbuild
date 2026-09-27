"""Bounded display of the dated HTTP evidence (no mutation)."""
import json
from pathlib import Path
import sys
rows=json.loads(Path(sys.argv[1] if len(sys.argv)>1 else 'research/2026-09-27-http.json').read_text())
for i,r in enumerate(rows):
    lines=r.get('text','').splitlines()
    p=r.get('products',[None])[0] if r.get('products') else {}
    o=p.get('offers',{})
    if isinstance(o,list): o=o[0] if o else {}
    seller=next((' '.join(lines[j:j+2]) for j,x in enumerate(lines) if 'Sprzedaje i wysyła przedsiębiorca:' in x), 'unknown')
    print(i, r['url'],r.get('http','').split(' ')[0],p.get('mpn'),o.get('price'),o.get('availability'),o.get('seller'),seller)
    if i in (18,25):
        for j,x in enumerate(lines):
            if any(k in x for k in ('13 150','13\u00a0150','Stan','Kod producenta','kody kart','nie dysponujemy','netto','brutto')) and j>1040:
                print(' ',j,' '.join(lines[max(0,j-1):j+4])[:240])
