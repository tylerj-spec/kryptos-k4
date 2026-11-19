// R85 local RX pilot: strictly ciphertext-only; no K4 clues or known positions in this program.
// Computes max-likelihood plaintext under a rotating arbitrary permutation (AZ/AZ contact alphabet).
// Frame: z_i = (c_i + d floor(i/n)) mod 26, p_i = (invW[z_i] - d floor(i/n)) mod 26.
// This is a bounded heuristic solver, not a whole-family exclusion.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <unordered_map>
using namespace std;
using Perm=array<unsigned char,26>;
const int SZ=97;
float *bi=new float[676],*tri=new float[17576],*quad=new float[456976];
unordered_map<string,double> logwords;
void loadwords(const string &fname){
 ifstream in(fname);if(!in)throw runtime_error("missing generic word model");
 string w;double z;double sum=0;vector<pair<string,double>> entries;
 while(in>>w>>z){if(w.empty()||z<=0)continue;bool clean=true;for(char c:w)if(c<'a'||c>'z')clean=false;
 if(!clean)continue;for(char &c:w)c=(char)toupper(c);entries.emplace_back(w,z);sum+=z;}
 for(auto &v:entries)logwords[v.first]=log(v.second/sum);
}
double wordscore(const string& txt){
 double dp[SZ+1];for(int i=0;i<=SZ;i++)dp[i]=-1e30;dp[0]=0;
 for(int i=0;i<SZ;i++){
  if(dp[i]<-1e20)continue;
  string w;
  for(int j=i;j<SZ&&j<i+22;j++){
   w+=txt[j];auto it=logwords.find(w);
   double z=(it!=logwords.end()?it->second:-13.0*(j-i+1));
   if(j==i&&w!="A"&&w!="I")z=-15.;
   dp[j+1]=max(dp[j+1],dp[i]+z);
  }
 }
 return dp[SZ];
}
void load(const string& f,float *dst,int size){ifstream is(f,ios::binary); if(!is||!is.read((char*)dst,size*sizeof(float)))throw runtime_error("missing model "+f);}
int m26(int x){return (x+2600)%26;}
struct Solver {
 array<int,SZ> x{},s{};
 array<unsigned char,SZ> plain{};
 mt19937_64 rng;
 Solver(const string& ct, int n,int d,uint64_t seed):rng(seed){if(ct.size()!=SZ)throw runtime_error("cipher length not 97");for(int i=0;i<SZ;i++){int c=ct[i]-'A';if(c<0||c>=26)throw runtime_error("non A-Z ciphertext");s[i]=m26(d*(i/n));x[i]=m26(c+s[i]);}}
 double score(const Perm& inv){int v0=0,v1=0,v2=0;double q=0;for(int i=0;i<SZ;i++){int v=m26((int)inv[x[i]]-s[i]); if(i>=1)q+=0.10*bi[v1*26+v]; if(i>=2)q+=0.30*tri[(v0*26+v1)*26+v]; if(i>=3)q+=quad[((v2*26+v0)*26+v1)*26+v]; v2=v0;v0=v1;v1=v;}return q;}
 string decode(const Perm& inv){string p;for(int i=0;i<SZ;i++)p+=(char)('A'+m26((int)inv[x[i]]-s[i]));return p;}
 tuple<double,string,string> run(int starts,int iters){
  double best=-1.e99;Perm bestkey{};
  for(int start=0;start<starts;start++){
    Perm w{};iota(w.begin(),w.end(),0);shuffle(w.begin(),w.end(),rng);
    double z=score(w);int same=0;
    for(int it=0;it<iters;it++){
      int a=rng()%26,b=rng()%26;if(a==b)continue;
      swap(w[a],w[b]);double cand=score(w),delta=cand-z;
      // 5 reheating ramps: cooling avoids being stuck at shallow maxima.
      double frac=(it%(iters/5))/(double)(iters/5);
      double temp=5.0*pow(0.035,frac);
      if(delta>=0||generate_canonical<double,32>(rng)<exp(delta/temp)){z=cand;if(delta>0)same=0;}else {swap(w[a],w[b]);same++;}
      if(z>best){best=z;bestkey=w;}
    }
    // deterministic greedy polishing
    for(int it=0;it<350;it++){
      double dz=0;int ba=-1,bb=-1;
      for(int a=0;a<26;a++)for(int b=a+1;b<26;b++){
        swap(w[a],w[b]);double cand=score(w);swap(w[a],w[b]); if(cand-z>dz+1e-9){dz=cand-z;ba=a;bb=b;}
      }
      if(ba<0)break;swap(w[ba],w[bb]);z+=dz;
      if(z>best){best=z;bestkey=w;}
    }
  }
  // Lexical re-ranking and limited local refinement; no planted truth or published clue used.
  double comb=best+0.70*wordscore(decode(bestkey));
  for(int pass=0;pass<3;pass++){
   int ba=-1,bb=-1;double next=comb;
   for(int a=0;a<26;a++)for(int b=a+1;b<26;b++){
    swap(bestkey[a],bestkey[b]);auto z=score(bestkey)+0.70*wordscore(decode(bestkey));swap(bestkey[a],bestkey[b]);
    if(z>next+1e-8){next=z;ba=a;bb=b;}
   }
   if(ba<0)break;
   swap(bestkey[ba],bestkey[bb]);comb=next;
  }
  best=score(bestkey);
  string inv;for(int i=0;i<26;i++)inv+=(char)('A'+bestkey[i]);
  return {best,decode(bestkey),inv};
 }
};
int main(int argc,char**argv){
 try {
  if(argc!=9){cerr<<"Usage: rotor INPUT.tsv OUTPUT.tsv MODEL_DIR NMIN NMAX STARTS ITERS SEED\n";return 2;}
  string in=argv[1],out=argv[2],mdl=argv[3];int nmin=stoi(argv[4]),nmax=stoi(argv[5]),starts=stoi(argv[6]),iters=stoi(argv[7]);uint64_t seed=stoull(argv[8]);
  if(nmin<1||nmax<nmin||nmax>96||starts<1||starts>200||iters<2000||iters>500000)throw runtime_error("bounds rejected");
  load(mdl+"/gram2.bin",bi,676);load(mdl+"/gram3.bin",tri,17576);load(mdl+"/gram4.bin",quad,456976);loadwords(mdl+"/generic_words.txt");
  ifstream f(in);ofstream g(out);if(!f||!g)throw runtime_error("input or output open failed");g<<"ID\tRANK\tSCORE\tN\tD\tINVW\tPLAINTEXT\n";
  string line;while(getline(f,line)){
   auto tab=line.find('\t');if(tab==string::npos)throw runtime_error("missing tab");string id=line.substr(0,tab),ct=line.substr(tab+1);
   struct R{double z;string p,w;int n,d;};vector<R> all;
   for(int n=nmin;n<=nmax;n++)for(int d:{-1,1}){
    uint64_t salt=seed;for(char c:id)salt=salt*131+(unsigned char)c;salt=salt*65537+n*3+(d+1);
    Solver sol(ct,n,d,salt);auto [z,p,w]=sol.run(starts,iters);all.push_back({z,p,w,n,d});
   }
   sort(all.begin(),all.end(),[](const R&a,const R&b){return a.z>b.z;});
   for(int k=0;k<min(6,(int)all.size());k++)g<<id<<'\t'<<k+1<<'\t'<<setprecision(10)<<all[k].z<<'\t'<<all[k].n<<'\t'<<all[k].d<<'\t'<<all[k].w<<'\t'<<all[k].p<<'\n';
   cerr<<id<<" best score "<<fixed<<setprecision(2)<<all[0].z<<" model n "<<all[0].n<<" d "<<all[0].d<<"\n";
  }
 }catch(const exception& e){cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
