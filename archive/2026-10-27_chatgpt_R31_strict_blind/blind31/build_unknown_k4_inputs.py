from pathlib import Path
import csv
ROOT=Path(__file__).resolve().parent; AZ='ABCDEFGHIJKLMNOPQRSTUVWXYZ';KRY='KRYPTOSABCDEFGHIJLMNQUVWXZ';text=(ROOT/'carter_az.txt').read_text()
ct=(ROOT/'ciphertext.txt').read_text().strip()
def ck(p):
 k=[int(x) for x in f'{p:05d}']
 while len(k)<97:k.append((k[-5]+k[-4])%10)
 return k[:97]
with (ROOT/'unknown_k4_inputs.txt').open('w') as f:
 for name in ('G5','CARTER'):
  s=list(csv.DictReader((ROOT/f'K4_{name}_BLIND.tsv').open(),delimiter='\t'))[:2]
  for i,row in enumerate(s):
   parts=dict(x.split('=',1) for x in row['setting'].split('/') if '=' in x)
   if name=='G5':k=ck(int(parts['PRIMER']))
   else:
    b=text if parts['DIR']=='FORWARD' else text[::-1]
    a=AZ if parts['KEYNUM']=='AZ' else KRY
    off=int(row['offset']); k=[a.index(ch) for ch in b[off:off+97]]
   key=''.join(chr(65+v)for v in k)
   f.write(f"K4_{name}_R{i+1} {key} {ct} {'?'*97} {310031300+i+(0 if name=='G5' else 10)} -\n")
print('Prepared 4 K4 blind settings selected only from ciphertext-only ranking')
