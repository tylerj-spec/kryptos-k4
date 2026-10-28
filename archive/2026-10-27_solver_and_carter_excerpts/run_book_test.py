#!/usr/bin/env python3
"""Test a LOCAL supplied text as a non-repeating running key under the R26 two-free-alphabet model.

This does NOT download the Carter book or verify OCR. It scans byte-preserved input,
normalizes separately to A-Z, checks 24 known K4 positions, and writes passing
settings. Source text is not corrected or edited; record any OCR uncertainty.

Examples:
  python run_book_test.py source_excerpts/carter_1923_bodleian.txt --max-windows 300
  python run_book_test.py carter_mace_1923_UNVERIFIED_OCR.txt --max-windows 5000
  python run_book_test.py carter_mace_1923_UNVERIFIED_OCR.txt --all
"""
import argparse, csv, hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent / "claude" / "r26"))
from key_oracle import K4, ANCH, possible, checks
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY="KRYPTOSABCDEFGHIJLMNQUVWXZ"
assert len(AZ)==len(KRY)==26 and len(set(KRY))==26

def main():
 ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
 ap.add_argument("source",type=Path,help="Existing local .txt file; no network access")
 g=ap.add_mutually_exclusive_group()
 g.add_argument("--max-windows",type=int,default=None,help="Test first N windows of each orientation (bounded run)")
 g.add_argument("--all",action="store_true",help="Explicitly scan all possible 97-letter windows")
 ap.add_argument("--start",type=int,default=0,help="Starting index of normalized source for each orientation")
 ap.add_argument("--output-dir",type=Path,default=Path('book_test_results'))
 args=ap.parse_args()
 if args.max_windows is None and not args.all: args.max_windows=1000
 raw=args.source.read_bytes()
 original=raw.decode("utf-8",errors="replace")
 normalized=''.join(c for c in original.upper() if c in AZ)
 if len(normalized)<97:ap.error("Source has fewer than 97 A-Z letters")
 if args.start<0:ap.error("--start must be nonnegative")
 out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
 # Keep original byte source intact; normalization stored separately with metadata.
 (out/'normalized_AZ_only.txt').write_text(normalized+'\n',encoding='ascii')
 max_offsets=max(0,len(normalized)-96)
 upper=max_offsets if args.all else min(max_offsets,args.start+args.max_windows)
 if args.start>=upper:ap.error("--start is beyond selected search span")
 fields=['orientation','key_alphabet','offset','independent_crib_cycles','key_97']
 hits=[];t=time.time();trials=0
 for orient,characters in [('FWD',normalized),('REVERSE',normalized[::-1])]:
  for label,alphabet in [('AZ',AZ),('KRYPTOS',KRY)]:
   key_numeric=[alphabet.index(c) for c in characters]
   for i in range(args.start,upper):
    key=key_numeric[i:i+97]
    trials+=1
    # With both plaintext AND cipher alphabets unrestricted, +/- shifts are
    # equivalent by reflection of one free alphabet. Test + only.
    if possible(key,sign=1):
     hits.append({'orientation':orient,'key_alphabet':label,'offset':i,
                  'independent_crib_cycles':checks(key),
                  'key_97':characters[i:i+97]})
   print(f'{orient} {label}: tested {upper-args.start} windows; hits so far {len(hits)}',flush=True)
 with (out/'compatible_keys.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(hits)
 metadata={'source_filename':args.source.name,'sha256_raw':hashlib.sha256(raw).hexdigest(),
  'raw_bytes':len(raw),'normalized_az_letters':len(normalized),
  'sha256_normalized':hashlib.sha256(normalized.encode()).hexdigest(),
  'start_offset':args.start,'end_offset_exclusive':upper,'window_count_total':max_offsets,
  'scan_complete':args.start==0 and upper==max_offsets,
  'tested_settings':trials,'passing_settings':len(hits),
  'elapsed_seconds':round(time.time()-t,3),
  'known_clues':{'EASTNORTHEAST':'22-34, 1-based','BERLINCLOCK':'64-74, 1-based'},
  'model':'in-place running-key additive shift, both alphabets arbitrary; + and - equivalent',
  'warning':'Feasible key does not mean recovered readable plaintext. OCR may be incorrect. No matched null controls in this script.'}
 (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(metadata,indent=2))
if __name__=='__main__':main()
