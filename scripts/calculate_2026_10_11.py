"""Dated, non-purchasable product-only basket arithmetic; source audit in Oct 11 report."""
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
D = Decimal
q = lambda x: x.quantize(D('.01'), rounding=ROUND_HALF_UP)
fx = D('4.3775')  # NBP 197/A/NBP/2026, effective Oct 9
ram_eur = D('5866')
case_eur = D('499.95')
ram_pl = q(ram_eur * fx * D('1.23') / D('1.19'))  # illustrative PL VAT, not checkout
case_pl = q(case_eur * fx)  # French displayed VAT, NOT Polish checkout
A = {'cpu':D('6654.39'),'board':D('4409.99'),'ram':ram_pl,'cooler':D('1884.29'),'case':case_pl,'psu':D('2407.67'),'ssd_2':D('4419.38')*2,'fans_140_6':D('168.93')*6,'fans_120_6':D('179.80')*6,'gpu_sold_out':D('32890')}
B = {'cpu_prior_direct_2026_09_27':D('2669'),'board':D('2169.19'),'ram':D('10999'),'cooler':D('1499.17'),'case_prior_direct_2026_09_27':D('1139'),'ssd':D('4419.38'),'ssd2':D('4068.23'),'fans_140_8':D('168.93')*8,'gpu_sold_out':D('32890')}
ap = sum(A[k] for k in ('cpu','board','ram','cooler','case'))
bp = sum(B[k] for k in ('cpu_prior_direct_2026_09_27','board','ram','cooler','case_prior_direct_2026_09_27'))
a = sum(A.values())
bbase = sum(B.values())
b1 = bbase + D('2407.67')
b2 = bbase + D('1179')
result = {'date':'2026-10-11','class':'mixed-date product-only illustrations, NOT current/delivered offers', 'fx_source':'https://api.nbp.pl/api/exchangerates/rates/a/eur/2026-10-09/?format=json','eur_pln':str(fx),'ram_gross_eur_out_of_stock':str(ram_eur),'ram_german_vat_pln':str(q(ram_eur*fx)),'ram_illustrative_pl_vat_pln':str(ram_pl),'case_gross_eur_in_stock_pl_delivery_unknown':str(case_eur),'case_fr_vat_pln_reference':str(case_pl),'inputs_A':{k:str(q(v)) for k,v in A.items()},'inputs_B':{k:str(q(v)) for k,v in B.items()},'platform_A_C':str(q(ap)),'platform_B':str(q(bp)),'A_one':str(q(a)),'A_two_theoretical':str(q(a+A['gpu_sold_out'])),'C_non_gpu':str(q(a-A['gpu_sold_out'])),'C_pair_advertised_only':str(D('13150')),'C_arithmetic_excludes_loop':str(q(a-A['gpu_sold_out']+D('13150'))),'C_installed':'incomplete','C_fit_validated':'incomplete','B1_one':str(q(b1)),'B2_one':str(q(b2)),'B1_two_theoretical':str(q(b1+B['gpu_sold_out'])),'platform_premium_pln':str(q(ap-bp)),'platform_premium_pct':str(q((ap-bp)/bp*100)),'A_over_B1_pln':str(q(a-b1)),'A_over_B1_pct':str(q((a-b1)/b1*100)),'A_over_B2_pln':str(q(a-b2)),'A_over_B2_pct':str(q((a-b2)/b2*100)),'x3d2_premium_over_current_unqualified_x3d_metadata':str(q(D('3998.47')-D('2928'))),'x3d2_premium_pct':str(q((D('3998.47')-D('2928'))/D('2928')*100)),'weekly_change':'undefined; mixed-date baskets not comparable'}
path = Path('research/2026-10-11-calculations.json')
if path.exists():
    raise FileExistsError(path)
path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
