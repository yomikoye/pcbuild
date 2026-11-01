"""Summarise public collector captures for manual review; never selects or prices offers."""
import json
import sys
from pathlib import Path

items = json.loads(Path(sys.argv[1]).read_text())
for i, item in enumerate(items):
    if len(sys.argv) > 2 and i not in {int(x) for x in sys.argv[2:]}:
        continue
    print(f"\n[{i}] {item['url']} | {item.get('http')} | {item.get('title')}")
    print('error:', item.get('error', ''))
    for product in item.get('products', []):
        print('PRODUCT:', product.get('name'), 'MPN:', product.get('mpn'))
        offer = product.get('offers', {})
        if isinstance(offer, list):
            print('OFFERS:', offer[:2])
        else:
            print('OFFER:', {k: offer.get(k) for k in ('price','priceCurrency','availability','seller')})
    text = item.get('text', '')
    for needle in ('Sprzedaje i wysyła', 'Cena brutto', 'Cena netto', 'Cena:', '5 000,', '4 950,', 'brutto', 'netto', 'Kup teraz', 'zł', '€', 'PLN', 'In stock', 'Out of stock', 'Niedostępny', 'Dostępny', '13 050', 'Zotac', 'Kody kart', 'różnią', 'test', 'identycz', 'PROART-RTX5090', '338', '32GB'):
        pos = text.lower().find(needle.lower())
        if pos >= 0:
            print(needle, ':', text[max(0, pos-300):pos+500].replace('\n',' / '))
