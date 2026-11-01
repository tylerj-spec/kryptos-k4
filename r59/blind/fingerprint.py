#!/usr/bin/env python3
"""R59 strict ciphertext-only uniform-vs-structured-masking diagnostics.

- NO guessed plaintext or known K4 clue letters/positions anywhere in source.
- NO fitted 97-position pads or plaintext-generation functions.
- Separate IID calibration cohorts (4k each) and fixed English monograms.
- Exactly the preregistered four feature families and familywise p values.
"""
from pathlib import Path
import json
import math
import sys
import numpy as np

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N = 97
CAL_N = 4000
CAL_SEED = 590061
LAGS = tuple(range(1, 25))
PERIODS = tuple(range(2, 13))
FEATURES = (
    "abs_IC_deviation_from_uniform",
    "max_pooled_periodic_IC_m2_to12",
    "max_lag_equality_z_lag1_to24",
    "max_column_best_shift_log_likelihood_m2_to12",
)
MAX_FAMILYWISE_P = 0.01
BATCH = 1024

def load_freq(filename):
    data = Path(filename).read_text(encoding="ascii").splitlines()
    counts = {}
    for line in data:
        cols = line.split(chr(9))
        if len(cols) != 2 or cols[0] not in AZ or cols[0] in counts:
            raise ValueError("generic monogram prior format invalid")
        value = float(cols[1])
        if not math.isfinite(value) or value <= 0:
            raise ValueError("generic English monogram score invalid")
        counts[cols[0]] = value
    if set(counts) != set(AZ):
        raise ValueError("must cover all 26 English letters exactly")
    weight = np.asarray([counts[ch] for ch in AZ], dtype=np.float64)
    weight /= weight.sum()
    # Lookup [cipher_letter_index, subtractive Caesar keyshift].
    # With ciphertext c and shift k, plaintext p=(c-k) %26.
    return np.log(26.0 * weight[np.mod(
        np.arange(26, dtype=np.int32)[:, None]
        - np.arange(26, dtype=np.int32)[None, :], 26
    )])

def to_matrix(texts):
    if not texts:
        raise ValueError("empty batch")
    out = np.empty((len(texts),N), dtype=np.uint8)
    for r,text in enumerate(texts):
        if len(text) != N or any(ch not in AZ for ch in text):
            raise ValueError("ciphertext must be exactly 97 A-Z uppercase letters")
        out[r] = np.frombuffer(text.encode("ascii"), dtype=np.uint8) - 65
    return out

def count_by_letter(a):
    count = a.shape[0]
    offset = (26 * np.arange(count,dtype=np.int32))[:,None]
    return np.bincount((a.astype(np.int32) + offset).ravel(),
                       minlength=26*count).reshape(count,26)

def compute_chunk(a, shift_lookup):
    """Vectorized exact 97-letter statistics on a batch. No knowledge of family."""
    count = a.shape[0]
    out = np.empty((count,4),dtype=np.float64)
    global_counts = count_by_letter(a)
    IC = np.sum(global_counts * (global_counts - 1),axis=1)/(N*(N-1))
    out[:,0]=np.abs(IC - 1.0/26.0)

    best_pooled_ic = np.zeros(count,dtype=np.float64)
    best_shift_ll = np.full(count,-np.inf,dtype=np.float64)
    for m in PERIODS:
        numerator = np.zeros(count,dtype=np.float64)
        denominator = 0
        m_likelihood = np.zeros(count,dtype=np.float64)
        for j in range(m):
            col = a[:,j::m]
            length = col.shape[1]
            if length <= 1:
                raise ValueError("column too short for pooled IC")
            cc = count_by_letter(col)
            numerator += np.sum(cc * (cc-1),axis=1)
            denominator += length*(length-1)
            # Maximize independent letter shift for each period phase, without cribs.
            scores = cc @ shift_lookup
            m_likelihood += scores.max(axis=1)
        pooled = numerator/denominator
        best_pooled_ic = np.maximum(best_pooled_ic, pooled)
        best_shift_ll = np.maximum(best_shift_ll, m_likelihood)
    out[:,1]=best_pooled_ic
    out[:,3]=best_shift_ll

    highest = np.full(count,-np.inf,dtype=np.float64)
    for lag in LAGS:
        n=N-lag
        observed=np.count_nonzero(a[:,lag:] == a[:,:N-lag],axis=1)
        expect=n/26.0
        variance=n*(1/26)*(25/26)
        z=(observed-expect)/math.sqrt(variance)
        highest=np.maximum(highest,z)
    out[:,2]=highest
    if not np.all(np.isfinite(out)):
        raise ValueError("feature calculation produced nonfinite result")
    return out

def all_features(a, shift_lookup):
    chunks = [compute_chunk(a[i:i+BATCH],shift_lookup)
              for i in range(0,a.shape[0],BATCH)]
    return np.concatenate(chunks,axis=0)

def empirical_component_p(ref, samples):
    """Upper-tail p values with correct plus-one finite Monte Carlo calibration."""
    if ref.shape[0] != CAL_N or ref.shape[1] != 4:
        raise ValueError("wrong independent calibration cohort shape")
    if samples.ndim != 2 or samples.shape[1] != 4:
        raise ValueError("wrong feature array shape")
    result=np.empty_like(samples)
    for j in range(4):
        sorted_ref=np.sort(ref[:,j])
        ge=CAL_N - np.searchsorted(sorted_ref,samples[:,j],side="left")
        result[:,j]=(1+ge)/(CAL_N+1)
    return result

def evaluate(ciphertexts, prior):
    rng = np.random.default_rng(CAL_SEED)
    ref1 = rng.integers(0,26,size=(CAL_N,N),dtype=np.uint8)
    ref2 = rng.integers(0,26,size=(CAL_N,N),dtype=np.uint8)
    # These two Monte Carlo cohorts were selected before any K4 statistics.
    print("R59: calibration cohort A features",file=sys.stderr,flush=True)
    a_features = all_features(ref1,prior)
    print("R59: independent omnibus calibration cohort B features",file=sys.stderr,flush=True)
    b_features = all_features(ref2,prior)
    b_p = empirical_component_p(a_features,b_features)
    b_stat = -np.log10(b_p.min(axis=1))
    print("R59: 91 blind ciphertext fingerprints",file=sys.stderr,flush=True)
    actual = all_features(to_matrix(ciphertexts),prior)
    comp = empirical_component_p(a_features,actual)
    maxima = -np.log10(comp.min(axis=1))
    omnibus = (1 + np.count_nonzero(
        b_stat[:,None] >= maxima[None,:],axis=0))/(CAL_N+1)
    return actual,comp,maxima,omnibus

def main():
    if len(sys.argv)!=4:
        raise ValueError("usage: fingerprint.py INPUT.tsv ENGLISH_FREQ.tsv OUTPUT.jsonl")
    input_path,prior_path,out_path=sys.argv[1:]
    if Path(out_path).exists():
        raise FileExistsError("refuse output overwrite")
    lines=Path(input_path).read_text(encoding="ascii").splitlines()
    if len(lines)!=91:
        raise ValueError("R59 blind input must be 90 controls plus K4")
    pairs=[]
    for line in lines:
        f=line.split(chr(9))
        if len(f)!=2:
            raise ValueError("exactly two blind input TSV fields; no truth/key/mask")
        pairs.append(f)
    ids=[x[0] for x in pairs]
    if len(set(ids))!=len(ids):
        raise ValueError("repeated record ID")
    if ids != [f"CASE_{i:03d}" for i in range(90)] + ["K4"]:
        raise ValueError("no missing cases or non-neutral IDs")
    ciphers=[x[1] for x in pairs]
    prior=load_freq(prior_path)
    features,pvalues,maxima,p_omni=evaluate(ciphers,prior)

    path=Path(out_path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="ascii") as out:
        for j,ident in enumerate(ids):
            row={
                "id":ident,
                "n":N,
                "null_cohort_size":CAL_N,
                "omnibus_cohort_size":CAL_N,
                "feature_names":list(FEATURES),
                "feature_values":[round(float(v),10) for v in features[j]],
                "feature_upper_tail_p_values":[round(float(v),10) for v in pvalues[j]],
                "maximum_feature_surprise_log10":round(float(maxima[j]),10),
                "familywise_uniform_null_p":round(float(p_omni[j]),10),
                "departure_flag":bool(p_omni[j]<=MAX_FAMILYWISE_P),
                "conclusion":"STATISTICAL_NONUNIFORMITY_ONLY_NO_DECRYPTION",
            }
            out.write(json.dumps(row,sort_keys=True,separators=(",",":"))+chr(10))
    print("R59: raw complete blind stats frozen next, 91 records")
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("R59 blind fatal:",type(e).__name__,str(e),file=sys.stderr)
        sys.exit(1)
