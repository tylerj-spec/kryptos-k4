#!/usr/bin/env python3
"""R67 structure-preserving control preparation (NO K4 plaintext/clues).

Usage: python3 r67/sealed/make_controls.py ENGLISH_LETTERS GERMAN_LETTERS OUTDIR
Requires repository root with r61/routes.txt and r39/ic_gate/k4_ciphertext.txt.
OUTDIR/BLIND.tsv is the ONLY file to supply to r65/blind/run.py.
OUTDIR/SEALED_TRUTH.json MUST stay outside the solver until all scores are frozen.
"""
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = ROOT / 'r61/routes.txt'
K4 = ROOT / 'r39/ic_gate/k4_ciphertext.txt'
K4_HASH = '2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3'
AZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
KRY = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'
SEED = 670001
N_PER_FAMILY = 32
N_POS = 24
IC_TOLERANCE = 0.004
MIN_DISTINCT = 25
MAX_ATTEMPTS = 40000
FAMILIES = ('OTP', 'PERIODIC_VIG', 'QUAG_III', 'PLAINTEXT_AUTOKEY',
            'QUAG_III_ROUTE', 'HOMOPHONIC_ROUTE')


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def letterstream(path):
    raw = path.read_bytes()
    # Follow R63 G-DE1 normalisation for umlauts, before discarding nonletters.
    text = raw.decode('utf-8').upper().replace('Ä', 'AE').replace('Ö', 'OE').replace('Ü', 'UE')
    s = ''.join(c for c in text if c in AZ)
    if len(s) < 300:
        raise ValueError('source must contain at least 300 A-Z letters: ' + str(path))
    return s, sha_bytes(raw)


def load_routes():
    out = []
    for line in ROUTES.read_text().splitlines():
        name, order, numbers = line.split()
        p = tuple(int(n) for n in numbers.split(','))
        if order != 'S_then_T' or len(p) != 97 or sorted(p) != list(range(97)):
            raise ValueError('invalid route: ' + name)
        out.append((name, p))
    if len(out) != 10 or sum(name == 'SNAKE_L' for name, _ in out) != 1:
        raise ValueError('expected 10 fixed R61 routes including SNAKE_L')
    return out


def encrypt(p, k, alphabet=AZ, operation='VIG'):
    # Same conventions as r63/blind/rk2_solve.cpp. Independent implementation.
    index = {c: i for i, c in enumerate(alphabet)}
    out = []
    for a, b in zip(p, k):
        x, y = index[a], index[b]
        j = {'VIG': x + y, 'BEAU': y - x, 'VARB': x - y}[operation] % 26
        out.append(alphabet[j])
    return ''.join(out)


def transpose(s, route):
    return ''.join(s[i] for i in route[1])


def homophonic(p, rng):
    symbols = list(AZ)
    rng.shuffle(symbols)
    seen = sorted(set(p))
    cmap = dict(zip(seen, symbols[:len(seen)]))
    inv = {x: [cmap[x]] for x in seen}
    counts = Counter(p)
    for letter in symbols[len(seen):]:
        options = [x for x in seen if len(inv[x]) < 4]
        if not options:
            break
        chosen = rng.choices(options, weights=[counts[x] / len(inv[x]) for x in options])[0]
        inv[chosen].append(letter)
    return ''.join(rng.choice(inv[x]) for x in p), {x: ''.join(v) for x, v in inv.items()}


def sample_source(s, rng):
    start = rng.randrange(len(s) - 96)
    return s[start:start + 97], start


def make_case(family, en, de, rng, routes):
    p, start = sample_source(en, rng)
    metadata = {'family': family, 'plaintext': p, 'plaintext_start': start}
    if family == 'OTP':
        key = ''.join(rng.choices(AZ, k=97))
        ct = encrypt(p, key)
        metadata['key'] = key
    elif family == 'PERIODIC_VIG':
        key = ''.join(rng.choices(AZ, k=rng.randint(5, 18)))
        ct = encrypt(p, (key * 20)[:97])
        metadata['key'] = key
    elif family in ('QUAG_III', 'QUAG_III_ROUTE'):
        key = ''.join(rng.choices(AZ, k=rng.randint(5, 18)))
        intermediate = encrypt(p, (key * 20)[:97], KRY)
        metadata.update({'key': key, 'alphabet': KRY})
        if family.endswith('_ROUTE'):
            route = rng.choice(routes)
            ct = transpose(intermediate, route)
            metadata['route'] = route[0]
        else:
            ct = intermediate
    elif family == 'PLAINTEXT_AUTOKEY':
        lag = rng.randint(5, 24)
        primer = ''.join(rng.choices(AZ, k=lag))
        ct = encrypt(p, (primer + p)[:97])
        metadata.update({'primer': primer, 'lag': lag})
    elif family == 'HOMOPHONIC_ROUTE':
        intermediate, cmap = homophonic(p, rng)
        route = rng.choice(routes)
        ct = transpose(intermediate, route)
        metadata.update({'homophones': cmap, 'route': route[0]})
    else:
        raise ValueError(family)
    return ct, metadata


def ic(s):
    hist = Counter(s)
    return sum(n * (n - 1) for n in hist.values()) / (len(s) * (len(s) - 1))


def positive_case(en, de, rng, route, convention):
    p, start = sample_source(en, rng)
    key, kstart = sample_source(de, rng)
    alphabet, operation = convention
    intermediate = encrypt(p, key, alphabet, operation)
    ct = transpose(intermediate, route)
    return ct, {'family': 'POS_GERMAN', 'plaintext': p, 'key': key,
                'plaintext_start': start, 'key_start': kstart,
                'alphabet': alphabet, 'operation': operation, 'route': route[0]}


def produce(en, de, routes, target_ic, rng):
    records = []
    report = {}
    used = set()
    for family in FAMILIES:
        attempts = 0
        accepted = 0
        while accepted < N_PER_FAMILY and attempts < MAX_ATTEMPTS:
            attempts += 1
            ct, truth = make_case(family, en, de, rng, routes)
            if ct in used or not (abs(ic(ct) - target_ic) <= IC_TOLERANCE and
                                  len(set(ct)) >= MIN_DISTINCT):
                continue
            used.add(ct)
            records.append((ct, truth))
            accepted += 1
        report[family] = {'attempts': attempts, 'accepted': accepted}
        if accepted != N_PER_FAMILY:
            raise RuntimeError(f'Family {family} has only {accepted} accepted controls '
                               f'in {attempts} tries; revise BEFORE looking at scores.')
    snake = next(r for r in routes if r[0] == 'SNAKE_L')
    others = [r for r in routes if r[0] != 'SNAKE_L']
    for i in range(N_POS):
        route = snake if i < N_POS // 2 else rng.choice(others)
        alph = AZ if i % 2 == 0 else KRY
        op = ('VIG', 'BEAU', 'VARB')[i % 3]
        ct, truth = positive_case(en, de, rng, route, (alph, op))
        if ct in used:
            raise RuntimeError('duplicate positive control')
        records.append((ct, truth))
        used.add(ct)
    rng.shuffle(records)
    return records, report


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    en_path, de_path, output = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    if output.exists():
        raise SystemExit('Refusing to overwrite output directory')
    raw_k4 = K4.read_bytes()
    if sha_bytes(raw_k4) != K4_HASH:
        raise SystemExit('K4 ciphertext file SHA-256 mismatch')
    k4_ct = raw_k4.decode().strip()
    if len(k4_ct) != 97 or not k4_ct.isupper():
        raise SystemExit('Invalid original K4 ciphertext')
    # Both streams must be the normalized held-out corpus files produced
    # exclusively by the SHA-256-pinned r67/sealed/build_sources.py.
    if (en_path.name, de_path.name) != ('hold_pt.txt', 'de_hold.txt') or en_path.parent != de_path.parent:
        raise SystemExit('expected hold_pt.txt and de_hold.txt in the same pinned source directory')
    source_manifest_path = en_path.parent / 'SOURCE_MANIFEST.json'
    source_manifest = json.loads(source_manifest_path.read_text())
    if source_manifest.get('experiment') != 'R67':
        raise SystemExit('unrecognized corpus provenance manifest')
    if ([e.get('sha256') for e in source_manifest.get('english_books', [])] != [
            '7b3e855dbc4e9833b0281a0bc1d527379d85c14f8dfb389ef916022d6e4d888c',
            'c8a61868388cafca2c76d1d82ee610d24b2bb09913ba6da936c4aca94eb1d1e4']
            or source_manifest.get('german_archive_sha256') !=
            'ad553e177baac263840c10980e6f3e76d5d15f7f7a078bd98520b36edb69b27c'
            or source_manifest.get('builder_sha256') !=
            sha_bytes((ROOT / 'r67/sealed/build_sources.py').read_bytes())):
        raise SystemExit('source archive or builder provenance mismatch')
    english, en_hash = letterstream(en_path)
    german, de_hash = letterstream(de_path)
    for name, actual in (('hold_pt.txt', en_hash), ('de_hold.txt', de_hash)):
        if source_manifest['normalized'][name]['sha256'] != actual:
            raise SystemExit('normalized source hash mismatch: ' + name)
    protocol = ROOT / 'r67/PREREGISTRATION.md'
    declared = (ROOT / 'r67/PREREGISTRATION.sha256').read_text().split()
    if not declared or sha_bytes(protocol.read_bytes()) != declared[0]:
        raise SystemExit('R67 frozen preregistration SHA-256 missing or mismatch')
    routes = load_routes()
    rng = random.Random(SEED)
    records, counts = produce(english, german, routes, ic(k4_ct), rng)
    output.mkdir(parents=True)
    blind = ['id\tciphertext']
    truth = []
    for i, (ct, item) in enumerate(records):
        name = f'CTRL_{i:03d}'
        blind.append(name + '\t' + ct)
        truth.append({'id': name, 'ciphertext': ct, **item})
    (output / 'BLIND.tsv').write_text('\n'.join(blind) + '\n')
    (output / 'SEALED_TRUTH.json').write_text(json.dumps(truth, indent=2) + '\n')
    manifest = {'seed': SEED, 'preregistration_sha256': declared[0],
                'source_manifest_sha256': sha_bytes(source_manifest_path.read_bytes()),
                'en_source_sha256': en_hash, 'de_source_sha256': de_hash,
                'k4_ciphertext_sha256': K4_HASH, 'k4_ct_ic': ic(k4_ct),
                'k4_distinct': len(set(k4_ct)), 'family_counts': counts,
                'blind_sha256': sha_bytes((output / 'BLIND.tsv').read_bytes()),
                'truth_sha256': sha_bytes((output / 'SEALED_TRUTH.json').read_bytes()),
                'generator_sha256': sha_bytes(Path(__file__).read_bytes()),
                'routes_sha256': sha_bytes(ROUTES.read_bytes())}
    (output / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Created', len(records), 'controls; BLIND.tsv only to isolated solver')
    print('Accepted family attempt counts:', counts)
    print('BLIND sha256', manifest['blind_sha256'])


if __name__ == '__main__':
    main()
