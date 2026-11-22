"""Independent scalar references for the two SYNTHETIC-ONLY capability screens."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPH = {"AZ": AZ, "KRY": KRY}


def linked_encrypt(plain, key, width):
    k = [AZ.index(c) for c in key]
    out = []
    for i, p in enumerate(plain):
        mid = KRY[(AZ.index(p) + k[i % len(k)]) % 26]
        out.append(AZ[(AZ.index(mid) + k[(i + i // width) % len(k)]) % 26])
    return "".join(out)


def linked_decrypt(cipher, key, width):
    k = [AZ.index(c) for c in key]
    out = []
    for i, c in enumerate(cipher):
        mid = AZ[(AZ.index(c) - k[(i + i // width) % len(k)]) % 26]
        out.append(AZ[(KRY.index(mid) - k[i % len(k)]) % 26])
    return "".join(out)


def ptak_encrypt(plain, key, conv, perm, model):
    a, b, op = conv
    ap, ac = ALPH[a], ALPH[b]
    p = plain if model == "M1" else unpermute(plain, perm)
    shifts = [AZ.index(c) for c in key]
    path_ct = []
    for i, ch in enumerate(p):
        x = ap.index(ch)
        k = shifts[i] if i < len(shifts) else ap.index(p[i-len(shifts)])
        y = x + k if op == "VIG" else k - x if op == "BEAU" else x - k
        path_ct.append(ac[y % 26])
    return "".join(path_ct[t] for t in perm)


def unpermute(text, perm):
    out = [None] * len(text)
    for i, t in enumerate(perm):
        out[t] = text[i]
    return "".join(out)


def ptak_decrypt(cipher, key, conv, perm, model):
    a, b, op = conv
    ap, ac = ALPH[a], ALPH[b]
    y = unpermute(cipher, perm)
    shifts = [AZ.index(c) for c in key]
    path_pt = []
    for i, ch in enumerate(y):
        k = shifts[i] if i < len(shifts) else ap.index(path_pt[i-len(shifts)])
        yy = ac.index(ch)
        x = yy - k if op == "VIG" else k - yy if op == "BEAU" else yy + k
        path_pt.append(ap[x % 26])
    return "".join(path_pt) if model == "M1" else "".join(path_pt[t] for t in perm)
