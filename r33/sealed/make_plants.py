#!/usr/bin/env python3
"""Pre-scan positive controls, independent ciphertext generation.

Outputs only plant ciphertexts in runs/. Ground truth stays in sealed/.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
AZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
KRY = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'
assert len(KRY) == 26 and len(set(KRY)) == 26
SOURCE = (ROOT/'runs/carter_az.txt').read_text().strip()


def key_g5(primer):
    k = [int(x) for x in str(primer).zfill(5)]
    while len(k) < 97:
        k.append((k[-5] + k[-4]) % 10)
    return k


def key_carter(off, num, reverse=False):
    s = SOURCE[::-1] if reverse else SOURCE
    alph = AZ if num == 'AZ' else KRY
    return [alph.index(ch) for ch in s[off:off + 97]]


def crypt(plain, route, order, key, pa, ca, op):
    q = [0] * 97
    for j, t in enumerate(route):
        q[t] = j
    ct = [''] * 97
    for i, ch in enumerate(plain):
        j = i if order == 'ID' else q[i]
        ki = q[i] if order == 'T_then_S' else i
        p = pa.index(ch)
        k = key[ki]
        v = (p + k) % 26 if op == 'VIG' else ((k - p) % 26 if op == 'BEAU' else (p - k) % 26)
        ct[j] = ca[v]
    return ''.join(ct)


def main():
    refs = json.loads((ROOT/'data/reference_messages.json').read_text())['r20_templates']
    specs = [
        dict(tag='PLANT_G5', family='G5', plain=refs[3], route='PALIMPSEST/F1S1O0V0/FWD', order='T_then_S', key_spec='primer51427', pa='KRY', ca='AZ', op='BEAU'),
        dict(tag='PLANT_CARTER', family='CARTER', plain=refs[8], route='KRYPTOS/F0S0O1V1/FWD', order='S_then_T', key_spec='rev/KRY/off17921', pa='AZ', ca='KRY', op='VIG')
    ]
    for sp in specs:
        matches = []
        file = ROOT/'runs'/('routes_g5.txt' if sp['family'] == 'G5' else 'routes_carter.txt')
        for ln in file.read_text().splitlines():
            name, order, vals = ln.split()
            if name == sp['route'] and order == sp['order']:
                matches.append([int(x) for x in vals.split(',')])
        assert len(matches) == 1, sp
        key = key_g5(51427) if sp['family'] == 'G5' else key_carter(17921, 'KRY', True)
        assert len(sp['plain']) == 97
        sp['ciphertext'] = crypt(sp['plain'], matches[0], sp['order'], key, AZ if sp['pa']=='AZ' else KRY, AZ if sp['ca']=='AZ' else KRY, sp['op'])
        (ROOT/'runs'/(sp['tag']+'.txt')).write_text(sp['ciphertext']+'\n')
    (HERE/'TRUTHS_SEALED.json').write_text(json.dumps(specs, indent=2)+'\n')
    print('2 plant ciphertexts generated, plaintexts sealed')


if __name__ == '__main__':
    main()
