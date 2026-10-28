from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
truths=json.loads((root/'sealed31/reference_messages.json').read_text())['calibration']
source=(root/'blind31/carter_az.txt').read_text();AZ='ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def enc(p,k):return ''.join(AZ[(AZ.index(x)+d)%26] for x,d in zip(p,k))

def chain(primer):
 k=[int(c)for c in f'{primer:05d}']
 while len(k)<97:k.append((k[-5]+k[-4])%10)
 return k[:97]

for name,p,k in [('G5',truths[0],chain(54321)),('CARTER',truths[1],[AZ.index(x) for x in source[12345:12442]])]:
 assert len(p)==97
 c=enc(p,k)
 (root/'blind31'/f'PLANT_{name}_CIPHERTEXT.txt').write_text(c+'\n')
 print(name,'ciphertext SHA',hashlib.sha256(c.encode()).hexdigest())
