#!/usr/bin/env node
"use strict";
/*
R54 - Ciphertext-ONLY method-family fingerprints; no known K4 plaintext.
Input: ORIGINAL 97-letter ciphertext, independently public K1-K3 plain-text
reference corpus. The 24 artist-confirmed K4 letters and their positions
are NEVER supplied, imported, parsed, referenced or scored here.
No K4 key/shift search or plaintext guessing is done.

Observation is exploratory; cannot identify one cipher uniquely from 97 letters.
Statistical nulls are calibration, not a decipherment/solution.
*/
const fs = require("fs");
const crypto = require("crypto");
const AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const ENGLISH = [
 .0817,.0149,.0278,.0425,.1270,.0223,.0202,.0609,.0697,.0015,
 .0077,.0403,.0241,.0675,.0751,.0193,.0010,.0599,.0633,.0906,
 .0276,.0098,.0236,.0015,.0197,.0007
];
const N=97;
const seed=540054;
function rng32(seed) {
 let x=seed|0;
 return () => {
  x=(x+0x6D2B79F5)|0;
  let t=Math.imul(x^(x>>>15),1|x);
  t^=t+Math.imul(t^(t>>>7),61|t);
  return ((t^(t>>>14))>>>0)/4294967296;
 };
}
function sha(s) { return crypto.createHash("sha256").update(s).digest("hex"); }
function toVec(s) {
 if(s.length!==N || !/^[A-Z]+$/.test(s)) throw Error("Ciphertext must be exactly 97 uppercase A-Z letters");
 return Uint8Array.from(s,c=>c.charCodeAt(0)-65);
}
function icAndUnique(vec) {
 const count=new Int32Array(26);
 for(let j=0;j<vec.length;j++)count[vec[j]]++;
 let numerator=0,entropy=0,uniq=0;
 for(let j=0;j<26;j++) {
  numerator+=count[j]*(count[j]-1);
  if(count[j]) {uniq++;let p=count[j]/vec.length;entropy-=p*Math.log2(p);}
 }
 return {ic:numerator/(vec.length*(vec.length-1)),unique:uniq,entropy,count:Array.from(count)};
}
function lagStats(vec,maxLag=48){
 let out=[];
 for(let d=1;d<=maxLag;d++){
  let n=vec.length-d,match=0;
  for(let j=0;j<n;j++)if(vec[j]===vec[j+d])match++;
  let expected=n/26;
  let z=(match-expected)/Math.sqrt(n*(1/26)*(25/26));
  out.push({lag:d,matches:match,positions_compared:n,z});
 }
 return out;
}
function shortRepeats(text,len){
 let seen=new Map(),dups=[];
 for(let i=0;i+len<=text.length;i++){
  const v=text.slice(i,i+len);
  const arr=seen.get(v)||[];
  arr.push(i);
  seen.set(v,arr);
 }
 for(let [token,positions] of seen)if(positions.length>1)dups.push({text:token,indices:positions});
 return dups.sort((a,b)=>b.indices.length-a.indices.length||a.text.localeCompare(b.text));
}
function percentile(sorted,q) {
 if(!sorted.length)throw Error("empty");
 const p=(sorted.length-1)*q,lo=Math.floor(p),hi=Math.ceil(p);
 return sorted[lo]+(sorted[hi]-sorted[lo])*(p-lo);
}
function summary(a){const sorted=a.slice().sort((x,y)=>x-y);
 const mean=a.reduce((x,y)=>x+y,0)/a.length;
 return {count:a.length,mean,minimum:sorted[0],p05:percentile(sorted,.05),median:percentile(sorted,.5),p95:percentile(sorted,.95),maximum:sorted.at(-1)};
}
function modelPeriods(plain, obsIC, rng){
 const periods=[1,2,3,5,7,11,17,31,97];
 const n=6000;
 const result={};
 for(let period of periods){
  const vals=[],unique26=0;
  let near=0,all26=0;
  for(let j=0;j<n;j++){
   let start=Math.floor(rng()*(plain.length-N+1));
   const key=Array.from({length:period},()=>Math.floor(rng()*26));
   const out=new Uint8Array(N);
   for(let k=0;k<N;k++){
    out[k]=(plain[start+k]+key[k%period])%26;
   }
   let x=icAndUnique(out);
   vals.push(x.ic);
   if(x.ic<=obsIC+1e-12)near++;
   if(x.unique===26)all26++;
  }
  result[period]={simulated:n,p_at_or_below_observed_IC:(near+1)/(n+1),
    fraction_all_26_letters:all26/n,ic_stats:summary(vals)};
 }
 return result;
}
function main(){
 if(process.argv.length!==5)throw Error("Usage: node method_fingerprint.js K4_CIPHERTEXT_FILE REFERENCE_PLAINTEXT_FILE OUT_JSON");
 const fileCT=process.argv[2],filePlain=process.argv[3],fileOut=process.argv[4];
 if(fs.existsSync(fileOut))throw Error("Never overwrite a previously frozen method report");
 const ctRaw=fs.readFileSync(fileCT),corpusRaw=fs.readFileSync(filePlain);
 const ct=ctRaw.toString("utf8").trim();
 if(ct.length!==97||!/^[A-Z]+$/.test(ct))throw Error("bad original ciphertext");
 const plainString=corpusRaw.toString("utf8").toUpperCase().replace(/[^A-Z]/g,"");
 if(plainString.length<97)throw Error("independent English reference must be >=97 letters");
 const input=toVec(ct),c=icAndUnique(input);
 const corpus=Uint8Array.from(plainString,letter=>letter.charCodeAt(0)-65);
 const windows=[];
 for(let i=0;i+N<=corpus.length;i++){
  windows.push(icAndUnique(corpus.slice(i,i+N)));
 }
 const plainICs=windows.map(w=>w.ic);
 const observedLags=lagStats(input,48).sort((a,b)=>b.z-a.z);
 const maxPeak=observedLags[0];
 // Frequency-preserving nulls use the ORIGINAL UNMODIFIED ciphertext's
 // letter histogram, not any K4 known plaintext or crib positions.
 const randShuffle=rng32(seed+3);
 const nNull=40000;
 let peakExceed=0,lag7Exceed=0;
 const maxZs=[];
 const original=Uint8Array.from(input);
 const lag7=observedLags.find(s=>s.lag===7).z;
 for(let t=0;t<nNull;t++){
  let copy=Uint8Array.from(original);
  for(let i=N-1;i>0;i--){
   let j=Math.floor(randShuffle()*(i+1));
   let q=copy[i];copy[i]=copy[j];copy[j]=q;
  }
  let m=-1e30,s7=0;
  for(let lag=1;lag<=48;lag++){
   const n=N-lag;
   let hit=0;for(let j=0;j<n;j++)hit+=copy[j]===copy[j+lag];
   const z=(hit-n/26)/Math.sqrt(n*(1/26)*(25/26));
   if(z>m)m=z;
   if(lag===7)s7=z;
  }
  maxZs.push(m);
  peakExceed+=m>=maxPeak.z-1e-12;
  lag7Exceed+=s7>=lag7-1e-12;
 }
 // Fixed generic English unigrams; not a fitted language model of K4.
 const p=ENGLISH.map(v=>v/ENGLISH.reduce((a,b)=>a+b,0));
 const cum=[];let s=0;for(let q of p){s+=q;cum.push(s);}
 function lookup(rand) {
  let lo=0,hi=25;while(lo<hi){let mid=(lo+hi)>>1;if(rand<cum[mid])hi=mid;else lo=mid+1;}return lo;
 }
 const randIid=rng32(seed+4), nIid=200000;
 let pEng=0,engAll26=0;
 for(let k=0;k<nIid;k++){
  let counts=new Int32Array(26);for(let j=0;j<N;j++)counts[lookup(randIid())]++;
  let ic=0,nuniq=0;
  for(let v of counts){ic+=v*(v-1);nuniq+=v>0;}
  ic/=N*(N-1);
  pEng+=ic<=c.ic+1e-12;
  engAll26+=nuniq===26;
 }
 const periodic=modelPeriods(corpus,c.ic,rng32(seed+8));
 const result={
  classification:"EXPLORATORY_CIPHERTEXT_ONLY_METHOD_FINGERPRINTS_NO_DECRYPTION",
  ciphertext_sha256:sha(ctRaw),
  reference_k1k3_plaintext_sha256:sha(corpusRaw),
  target_letters:N,
  independent_reference_characters:corpus.length,
  original_ciphertext:{
   index_of_coincidence:c.ic,
   unique_letters:c.unique,
   shannon_entropy_bits_per_letter:c.entropy,
   letter_counts:Object.fromEntries(AZ.split("").map((a,i)=>[a,c.count[i]])),
   repeated_bigrams:shortRepeats(ct,2),
   repeated_trigrams:shortRepeats(ct,3),
   top_lag_coincidence_peaks:observedLags.slice(0,12),
  },
  english_reference:{
   description:"All 97-letter contiguous windows of independently known K1-K3 plaintext; windows heavily overlap, not independent trials",
   windows:windows.length,
   window_ic_statistics:summary(plainICs),
   count_ic_at_or_below_ciphertext:windows.filter(x=>x.ic<=c.ic+1e-12).length,
   count_full_26_letter_alphabet:windows.filter(x=>x.unique===26).length
  },
  english_marginal_null:{
   description:"Independent identically distributed letters with generic English letter marginals (ignores word/correlation effects)",
   replicates:nIid,
   count_ic_at_or_below_ciphertext:pEng,
   empirical_tail_probability:(pEng+1)/(nIid+1),
   count_full_26_letter_alphabet:engAll26
  },
  shuffled_ciphertext_lag_null:{
   description:"40,000 frequency-preserving permutations of original ciphertext; 48 lags searched each; no K4 plaintext used",
   replicates:nNull,
   tested_lags:"1..48",
   observed_best_lag:maxPeak.lag,
   observed_max_z:maxPeak.z,
   observed_best_lag_matches:maxPeak.matches,
   familywise_exceedances:peakExceed,
   familywise_p:(peakExceed+1)/(nNull+1),
   lag7_uncorrected_exceedances:lag7Exceed,
   lag7_uncorrected_p:(lag7Exceed+1)/(nNull+1),
   maximum_z_null_distribution:summary(maxZs)
  },
  independent_synthetic_cipher_models:{
   description:"Generic independent K1-K3 plaintext 97-character windows encrypted using random periodic Vigenere AZ keys. This is a model-family calibration, NOT an inferred K4 key.",
   lengths_tested:[1,2,3,5,7,11,17,31,97],
   simulated_per_length:6000,
   by_period:periodic
  },
  interpretation:{
   attenuates:["pure columnar/route transposition of ordinary English","single fixed bijective substitution of ordinary English","ordinary unencrypted English"],
   consistent_but_unproven:["polyalphabetic substitution","variable-shift or running key","two-layer or changing-alphabet mechanism","homophonic or otherwise frequency-flattening cipher"],
   warning:"Exact method and order of operations are not statistically identified by 97 ciphertext letters. The 48-lag maximum must be multiple-comparison calibrated; a period-7 look is NOT an independently discovered cipher key."
  }
 };
 fs.writeFileSync(fileOut,JSON.stringify(result,null,2)+"\n",{flag:"wx"});
 console.log("R54 K4 IC",c.ic,"all letters",c.unique,"real-English windows at/below",result.english_reference.count_ic_at_or_below_ciphertext,"/",windows.length);
 console.log("R54 max autocorrelation lag",maxPeak.lag,"familywise p",result.shuffled_ciphertext_lag_null.familywise_p);
 console.log("R54 method fingerprint frozen without any published plaintext, plaintext positions or actual K4 key search");
}
main();
