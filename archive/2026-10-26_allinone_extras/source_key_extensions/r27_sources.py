#!/usr/bin/env python3
"""Round27 bounded source-key experiment, independent of readability optimization.

Texts are historically attested *excerpts*, not complete scanned volumes. Their
literal normalization is frozen before the keystream feasibility tests. The CIA
transcription is treated as ciphertext alphabetic letters only; question marks
are omitted from the key stream, with the alternative 'Q' handling also tested.
"""
import argparse, csv, hashlib, json, random, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'claude' / 'r26'))
from key_oracle import possible, K4, ANCH

AZ='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
KRY='KRYPTOSABCDEFGHIJLMNQUVWXZ'
SOURCE_URLS={
 'carter_1923_bodleian':'https://visit.bodleian.ox.ac.uk/tutankhamun-audio (Stop 3.3; reproduction transcript, not full volume)',
 'carter_diary_1922_bodleian':'https://visit.bodleian.ox.ac.uk/tutankhamun-audio (Stop 3.2; editorially expanded transcript)',
 'carter_1924_lecture':'https://tutankhamun.griffith.ox.ac.uk/miscellaneous/taa-i12/taa-i1207 (edited letterforms)',
 'cia_k1k3_cipher':'https://www.cia.gov/legacy/headquarters/kryptos-sculpture/ (transcription of K1-K3 ciphertext)',
}
SOURCE_TEXT={
 'carter_1923_bodleian': """The decisive moment had arrived. With trembling hands I made a tiny breach in the upper left hand corner. Darkness and blank space, as far as an iron testing rod could reach, showed that whatever lay beyond was empty, and not filled like the passage we had just cleared. Candle tests were applied as a possible precaution against possible foul gases, and then, widening the hole a little I inserted the candle and peered in, Lord Carnarvon, Lady Evelyn and Callender standing anxiously beside me to hear the verdict. At first I could see nothing, the hot air escaping form the chamber causing the candle flame to flicker, but presently, as my eyes grew accustomed to the light, details of the room within emerged slowly from the mist, strange animals, statues, and gold everywhere the glint of gold. For the moment an eternity it must have seemed to the others standing by I was struck dumb with amazement, and when Lord Carnarvon, unable to stand the suspense any longer, inquired anxiously, Can you see anything? it was all I could do to get out the words Yes, Wonderful things. Then widening the hole a little, so that we both could see, we inserted an electric torch.""",
 'carter_diary_1922_bodleian': """Candles were procured the all important Tell Tale for foul gases when opening an ancient subterranean excavation I widened the breach and by means of the candle looked in while Lord Carnarvon Lady Evelyn and Arthur Callender with the Reises the foremen waited in anxious expectation. It was sometime before one could see, the hot air escaping caused the candle to flicker, but as soon as one's eyes became accustomed to the glimmer of light the interior of the chamber gradually loomed before one, with its strange and wonderful medley of extraordinary and beautiful objects heaped upon one another. There was naturally short suspense for those present who could not see, when Lord Carnarvon said to me Can you see anything? I replied to him Yes, it is wonderful. I then with precaution made the hole sufficiently large for both of us to see. With the light of an electric torch as well as an additional candle we looked in.""",
 'carter_1924_lecture': """With trembling hands I made a tiny breach in the upper left hand corner. Darkness and blank space as far as an iron testing rod could reach, showed that whatever lay beyond was empty and not filled like the passage we had just cleared. Candle tests were applied as a precaution against possible foul gases, and then widening the hole a little, I inserted the candle and peered in. Lord Carnarvon, Lady Evelyn, and Callender standing anxiously beside me to hear the verdict. At first I could see nothing the hot air escaping from the chamber caused the candle flame to flicker, but presently as my eyes grew accustomed to the light, details of the room within emerged slowly from the mist, strange animals statues and gold everywhere the glint of gold. For the moment an eternity it must have seemed to the others standing by I was struck dumb with amazement, and when Lord Carnarvon unable to stand the suspense any longer, inquired anxiously, Can you see anything? it was all I could do to get out the words, Yes wonderful things.""",
}
CIA_CIPHER='''
EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ
YQTQUXQBQVYUVLLTREVJYQTMKYRDMFD
VFPJUDEEHZWETZYVGWHKKQETGFQJNCE
GGWHKK?DQMCPFQZDQMMIAGPFXHQRLG
TIMVMZJANQLVKQEDAGDVFRPJUNGEUNA
QZGZLECGYUXUEENJTBJLBQCRTBJDFHRR
YIZETKZEMVDUFKSJHKFWHKUWQLSZFTI
HHDDDUVH?DWKBFUFPWNTDFIYCUQZERE
EVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDX
FLGGTEZ?FKZBSFDQVGOGIPUFXHHDRKF
FHQNTGPUAECNUVPDJMQCLQUMUNEDFQ
ELZZVRRGKFFVOEEXBDMVPNFQXEZLGRE
DNQFMPNZGLFLPMRJQYALMGNUVPDXVKP
DQUMEBEDMHDAFMJGZNUPLGEWJLLAETG
ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIA
CHTNREYULDSLLSLLNOHSNOSMRWXMNE
TPRNGATIHNRARPESLNNELEBLPIIACAE
WMTWNDITEENRAHCTENEUDRETNHAEOE
TFOLSEDTIWENHAEIOYTEYQHEENCTAYCR
EIFTBRSPAMHHEWENATAMATEGYEERLB
TEEFOASFIOTUETUAEOTOARMAEERTNRTI
BSEDDNIAAHTTMSTEWPIEROAGRIEWFEB
AECTDDHILCEIHSITEGOEAOSDDRYDLORIT
RKLMLEHAGTDHARDPNEOHMGFMFEUHE
ECDMRIPFEIMEHNLSSTTRTVDOHW?OBKR
UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO
TWTQSJQSSEKZZWATJKLUDIAWINFBNYP
VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
'''
RAW=''.join(ch for ch in CIA_CIPHER if ch in AZ+'?')
assert RAW.endswith('?' + K4), (RAW[-102:],K4)
assert RAW.count('?')==4, RAW.count('?')
CIPHER_K123=RAW[:-97]
assert len(CIPHER_K123)==772 and len(CIPHER_K123.replace('?',''))==768, (len(CIPHER_K123),len(CIPHER_K123.replace('?','')))
SOURCE_TEXT['cia_k1k3_cipher_drop_q']=CIPHER_K123.replace('?','')
SOURCE_TEXT['cia_k1k3_cipher_question_as_q']=CIPHER_K123.replace('?','Q')

def norm(s): return ''.join(c for c in s.upper() if c in AZ)

def test_sources(add_routes=False):
    # Lexically frozen search, not optimized by readability. Each source is a distinct text convention.
    variants=[]
    for name,src in SOURCE_TEXT.items():
        s=norm(src)
        assert len(s)>=97
        for backward in [False,True]:
            ss=s[::-1] if backward else s
            for alpha in [AZ,KRY]:
                try: digits=[alpha.index(c) for c in ss]
                except ValueError: raise AssertionError((name,alpha))
                variants.append((name,'REV' if backward else 'FWD','AZ' if alpha==AZ else 'KRY',s,ss,digits))
    csvrows=[]; summaries=[]
    for name in SOURCE_TEXT:
        va=[v for v in variants if v[0]==name]
        n=hits=0; passing=[]
        for source,orient,anum,normal,ss,dd in va:
            for offset in range(len(dd)-97+1):
                key=dd[offset:offset+97]
                for sign in [1,-1]:
                    n+=1
                    if possible(key,sign=sign):
                        hits+=1
                        row=dict(source=source,orientation=orient,alphabet=anum,offset=offset,sign=sign,keystream=''.join(AZ[x] for x in key))
                        passing.append(row);csvrows.append(row)
        ss=norm(SOURCE_TEXT[name])
        summaries.append(dict(source=name,url=SOURCE_URLS.get(name,'same CIA source'),n_characters=len(ss),sha256=hashlib.sha256(ss.encode()).hexdigest(),trials=n,passes=hits,expected_at_random=round(n*0.00047,3)))
    return summaries,csvrows

if __name__=='__main__':
    sm,rows=test_sources()
    out=Path(__file__).resolve().parent/'results';out.mkdir(exist_ok=True)
    (out/'R27_SOURCE_ORACLE.json').write_text(json.dumps({'models':'in-place 2-free alph shift Vigenere variants; source excerpts only','summaries':sm,'passing_keys':rows},indent=2)+'\n')
    with (out/'R27_SOURCE_PASSES.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=['source','orientation','alphabet','offset','sign','keystream']);w.writeheader();w.writerows(rows)
    print(json.dumps(sm,indent=2));print('total passing keys',len(rows))
