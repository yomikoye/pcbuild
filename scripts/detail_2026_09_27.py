import json
from pathlib import Path
for filename,urls in [('research/2026-09-27-http.json',('allegrolokalnie.pl/oferta/zestaw','phanteks.com/product','senetic.pl/product')),('research/2026-09-27-fallback-http.json',('phs-memory.com','alternate.de/G-Skill'))]:
    for r in json.loads(Path(filename).read_text()):
        if any(u in r['url'] for u in urls):
            print('\n###',r['url'])
            lines=r['text'].splitlines()
            if 'allegrolokalnie' in r['url']:
                for j in range(1054,min(1165,len(lines))):print(j,lines[j][:290])
            elif 'phanteks' in r['url']:
                for j,x in enumerate(lines):
                    if any(k in x.lower() for k in ('dimension','gpu','radiator','mm','expansion','power supply')):print(j,' '.join(lines[j:j+5])[:400])
            elif 'phs' in r['url']:
                for j,x in enumerate(lines):
                    if any(k in x for k in ('€','EUR','available','lieferbar','verfügbar','32GB','5 years')):print(j,' '.join(lines[j:j+3])[:230])
            elif 'senetic' in r['url']:
                for j in range(2650,2672):print(j,lines[j][:240])
            else:
                for j,x in enumerate(lines[:210]):
                    if '€' in x or 'lieferbar' in x.lower() or 'verfügbar' in x.lower():print(j,' '.join(lines[j:j+3])[:230])
