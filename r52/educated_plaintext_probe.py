#!/usr/bin/env python3
"""R52 EXPLORATORY CRIB-CONDITIONED plaintext exercise, NOT a blind decryptor.

All candidate texts are invented using known EASTNORTHEAST/BERLINCLOCK positions.
For any plaintext the additive key can be computed tautologically. We do NOT
regard exact re-encryption from this fitted one-time key as evidence.

A controlled negative check: test implied AZ/KRY additive key coincidences at
lags 1..24, allowing 4 independently named alphabet combinations, against 2,000
anchor-preserving and letter-histogram-preserving shuffled nulls per candidate;
then account for selection among all eight candidate plaintexts as well.
A synthetic 9-period key serves as a positive control.
"""
from pathlib import Path
import hashlib
import json
import random
import numpy as np

ROOT=Path(__file__).resolve().parent
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY="KRYPTOSABCDEFGHIJLMNQUVWXZ"
CT="OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
ANCH={21+i:c for i,c in enumerate("EASTNORTHEAST")}
ANCH.update({63+i:c for i,c in enumerate("BERLINCLOCK")})
assert len(CT)==97 and len(ANCH)==24 and sorted(KRY)==list(AZ)
UK=[i for i in range(97) if i not in ANCH]
assert len(UK)==73

# Explicitly manually composed examples, no full K4 plaintext retrieved.
# 21 letters + 13 published + 29 letters + 11 published + 23 letters = 97.
CANDIDATES=[
 ("route_and_handoff","THEPATHTOFOLLOWPOINTS","FOLLOWTHELINEUNTILYOUREACHTHE","ANDLOOKFORANEWBEGINNING",
  "The path to follow points east northeast. Follow the line until you reach the Berlin Clock and look for a new beginning."),
 ("instruction_and_hidden_object","THEFIRSTSTEPISLOOKING","THEFINALCLUEISPOSITIONEDATTHE","THESECRETLIESUNDERNEATH",
  "The first step is looking east northeast. The final clue is positioned at the Berlin Clock. The secret lies underneath."),
 ("wall_clock_delivery","LOOKFROMTHEWALLTOWARD","ANDTHENFINDTHEHOURMARKEDONTHE","ANDTHEMESSAGEWILLAPPEAR",
  "Look from the wall toward east northeast, and then find the hour marked on the Berlin Clock, and the message will appear."),
 ("message_handoff","THEPATHTOFOLLOWPOINTS","THENPASSITTOANOTHERAGENTATTHE","THENTRANSMITTHEFINALKEY",
  "The path to follow points east northeast. Then pass it to another agent at the Berlin Clock. Then transmit the final key."),
 ("physical_layer","LOOKFROMTHEWALLTOWARD","THELASTMESSAGEWASPLACEDBESIDE","THESECONDLAYERISWAITING",
  "Look from the wall toward east northeast. The last message was placed beside Berlin Clock. The second layer is waiting."),
 ("no_literal_clock_key","THEFIRSTSTEPISLOOKING","THISISONLYONEPIECEOFTHEPUZZLE","ISTHEBEGINNINGNOTTHEEND",
  "The first step is looking east northeast. This is only one piece of the puzzle. Berlin Clock is the beginning not the end."),
 ("egypt_to_clock","FROMTHEPYRAMIDSLOOKTO","ANDRECEIVETHEMESSAGEBESIDETHE","ANDLOOKFORANEWBEGINNING",
  "From the pyramids look to east northeast and receive the message beside the Berlin Clock and look for a new beginning."),
 ("cairo_wall_message","THECAIROMESSENGERWENT","THEMESSAGEFROMEGYPTREACHEDTHE","WITNESSTHEFALLOFTHEWALL",
  "The Cairo messenger went east northeast. The message from Egypt reached the Berlin Clock. Witness the fall of the wall."),
]

def plaintext(row):
    name,a,b,c,reading=row
    assert (len(a),len(b),len(c))==(21,29,23),name
    p=a+"EASTNORTHEAST"+b+"BERLINCLOCK"+c
    assert len(p)==97 and all(p[i]==v for i,v in ANCH.items())
    assert "".join(x for x in reading.upper() if "A"<=x<="Z")==p
    return p

PAIRS=[("AZ_AZ",AZ,AZ),("KRY_KRY",KRY,KRY),("KRY_AZ",KRY,AZ),("AZ_KRY",AZ,KRY)]
PA_MAP={alphabet:np.array([alphabet.index(ch) for ch in AZ],dtype=np.int16)
        for alphabet in (AZ,KRY)}

def ciphertext_values(ct):
    return {a:np.array([a.index(ch) for ch in ct],dtype=np.int16) for a in (AZ,KRY)}

def shifts(p,cipher_index):
    v=np.array([AZ.index(ch) for ch in p],dtype=np.int16)
    return np.array([(cipher_index[ca]-PA_MAP[pa][v])%26
                     for _name,pa,ca in PAIRS])

def best_lag(k):
    best=(-1e10,0,0,0)
    for lag in range(1,25):
        n=97-lag
        counts=np.sum(k[:,:-lag]==k[:,lag:],axis=1)
        zs=(counts-n/26)/np.sqrt(n*(1/26)*(25/26))
        j=int(np.argmax(zs))
        if float(zs[j])>best[0]:
            best=(float(zs[j]),lag,j,int(counts[j]))
    return best

def shuffled(p,rng):
    chars=list(p)
    movable=[chars[i] for i in UK]
    rng.shuffle(movable)
    for i,c in zip(UK,movable):
        chars[i]=c
    return "".join(chars)

def main():
    nnull=2000
    cd=ciphertext_values(CT)
    results=[]
    obs_scores=[]
    for j,row in enumerate(CANDIDATES):
        p=plaintext(row)
        obs=best_lag(shifts(p,cd))
        obs_scores.append(obs[0])
        rng=random.Random(522026+j)
        null=[best_lag(shifts(shuffled(p,rng),cd))[0] for _ in range(nnull)]
        exceed=sum(x>=obs[0]-1e-12 for x in null)
        results.append({
          "id":row[0],"speculative_punctuation":row[4],"plaintext_97":p,
          "best_alphabet_pair":PAIRS[obs[2]][0],
          "best_lag":obs[1],"lag_equalities":obs[3],
          "max_shift_Z":round(obs[0],5),
          "null_exceedances":exceed,"null_count":nnull,
          "candidate_lookelsewhere_uncorrected_p":round((exceed+1)/(nnull+1),6),
          "note":"This is not a ciphertext solution: an additive key always exists by construction."
        })
    rngs=[random.Random(532026+j) for j in range(len(CANDIDATES))]
    nullmax=[]
    for _ in range(nnull):
        nullmax.append(max(best_lag(shifts(shuffled(plaintext(row),rngs[j]),cd))[0]
                           for j,row in enumerate(CANDIDATES)))
    observed=max(obs_scores)
    greater=sum(x>=observed-1e-12 for x in nullmax)

    # Positive control using original language candidate and forward-encrypted
    # random nine-letter periodic key. No K4 text nor true key is used.
    p=plaintext(CANDIDATES[0])
    rng=random.Random(542026)
    key=[rng.randrange(26) for _ in range(9)]
    ct9="".join(AZ[(AZ.index(c)+key[i%9])%26] for i,c in enumerate(p))
    synth=ciphertext_values(ct9)
    test=best_lag(shifts(p,synth))
    synth_null=[best_lag(shifts(shuffled(p,rng),synth))[0] for _ in range(300)]
    sp=sum(x>=test[0]-1e-12 for x in synth_null)

    report={
      "classification":"EXPLORATORY_GUESSES_CRIB_CONDITIONED_NO_K4_SOLUTION",
      "ciphertext_sha256_no_newline":hashlib.sha256(CT.encode()).hexdigest(),
      "length":97,"confirmed_plaintext_letters":24,"unknown_letters":73,
      "candidate_count":len(CANDIDATES),"nulls_each":nnull,
      "search_alphabets":[x[0] for x in PAIRS],
      "search_lags":"1..24",
      "candidates":results,
      "familywise":{
        "max_observed_Z":round(observed,5),
        "best_id":results[int(np.argmax(obs_scores))]["id"],
        "null_count":nnull,
        "null_exceedances":greater,
        "empirical_p":round((greater+1)/(nnull+1),6),
        "null_median_Z":round(float(np.median(nullmax)),5),
        "null_95th_percentile_Z":round(float(np.percentile(nullmax,95)),5),
      },
      "synthetic_positive_control":{
        "key_period":9,"found_period":test[1],
        "max_Z":round(test[0],5),
        "null_count":300,"null_exceedances":sp,
        "empirical_p":round((sp+1)/301,6),
        "forward_exact":all(AZ[(AZ.index(p[i])+key[i%9])%26]==ct9[i] for i in range(97)),
      },
      "limits":[
        "Candidates were hand-authored after knowing the published 24 letters.",
        "For any plaintext a 97-position additive key can be fitted, so re-encryption proves nothing.",
        "A candidate's small uncorrected p is invalid without a full multi-candidate lookelsewhere adjustment.",
        "Only a short-repeating shift test was tried; it has no power against arbitrary masks or transpositions.",
        "No authentic K4 plaintext was recovered, no verifier submission was made."
      ]
    }
    (ROOT/"R52_RESULTS.json").write_text(json.dumps(report,indent=2)+"\n")
    print("R52 familywise empirical p",report["familywise"]["empirical_p"])
    print("R52 synthetic period",report["synthetic_positive_control"]["found_period"])
    for c in results:
        print(c["id"],c["max_shift_Z"],c["candidate_lookelsewhere_uncorrected_p"])
if __name__=="__main__":
    main()
