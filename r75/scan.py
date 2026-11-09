"""R75: ciphertext-only exhaustive scanner for 2,880 40-period transforms.

Uses the repo's pinned R59 letter model; no K4 ciphertext, clue letters or
known clue offsets appear in this source. On any valid 97-symbol ciphertext,
returns exactly one deterministic full-length decryption per setting.
Requires numpy and existing R59 LM binary (sha256 checked by caller).
"""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import reference as R

class Scanner:
    def __init__(self,lm_path):
        mm=np.memmap(lm_path,dtype=np.uint8,mode='r')
        if bytes(mm[:5])!=b'R59LM':
            raise ValueError('not the R59 order-6 model')
        self.order=int(mm[5])
        off,size,self.lm=8,26,{}
        for k in range(1,self.order+1):
            self.lm[k]=np.memmap(lm_path,dtype=np.float32,mode='r',offset=off,shape=(size,))
            off+=size*4
            size*=26
        self.labels=list(R.settings())
        self.inv=np.empty((len(self.labels),40,26),dtype=np.uint8)
        for q,s in enumerate(self.labels):
            for j,m in enumerate(R.maps40(s)):
                for p,c in enumerate(m):
                    self.inv[q,j,c]=p
        assert len(self.labels)==2880

    def decrypt_all(self,ct):
        if len(ct)!=R.N or any(ch not in R.AZ for ch in ct):
            raise ValueError('expected exactly 97 uppercase A-Z letters')
        c=np.frombuffer(ct.encode('ascii'),dtype=np.uint8).astype(np.int16)-65
        return self.inv[:,np.arange(R.N)%40,c].astype(np.int64)

    def lm_score(self,P):
        tot=np.zeros(len(P),dtype=np.float64)
        for i in range(R.N):
            L=min(i,self.order-1)
            ctx=np.zeros(len(P),dtype=np.int64)
            for j in range(i-L,i):
                ctx=ctx*26+P[:,j]
            tot+=np.asarray(self.lm[L+1][ctx*26+P[:,i]],dtype=np.float64)
        return tot/R.N

    def scan(self,ct):
        P=self.decrypt_all(ct)
        s=self.lm_score(P)
        order=np.argsort(-s,kind='stable')
        return P,s,order

    def text(self,row):
        return ''.join(R.AZ[int(n)] for n in row)

    def best(self,ct,top=10):
        p,s,order=self.scan(ct)
        return [{
            'index':int(k),'plaintext':self.text(p[k]),
            'setting':self.labels[int(k)].__dict__,
            'r59_log10_per_letter':float(s[k])
        } for k in order[:top]]
