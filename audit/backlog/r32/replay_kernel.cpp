// Independent post-freeze historical count audit. No plaintext outputs.
// R32: compare expected key symbols, histogram every labeled setting.
// R41: equality-signature join, followed by complete partial-bijection check.
// Signature hashes wrap deliberately; collisions are fully rechecked.
// Count totals have explicit <2^63 bounds and are re-derived as Python ints.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
static const string AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ";
static const array<string,7> AL={AZ,"KRYPTOSABCDEFGHIJLMNQUVWXZ","PALIMSETBCDFGHJKNOQRUVWXYZ",
 "ABSCIDEFGHJKLMNOPQRTUVWXYZ","KAHUOFNPDLXRBIVSGQTEMZYCJW","ACOZEJWIFRLDQMGUPBNYSHVTKX","ADJOUZBEKPVCGMRXIHNTYSFLQW"};
static int mod(int x){x%=26;return x<0?x+26:x;}
static string letters(const string&p){ifstream f(p);if(!f)throw runtime_error("input open");string s,t;while(getline(f,t))for(char c:t)if(c>='A'&&c<='Z')s+=c;return s;}
struct Route {string name,order;array<int,97> inverse;};
static vector<Route> routes(const string&p){
 ifstream f(p);if(!f)throw runtime_error("routes open");string l;vector<Route> out;
 while(getline(f,l)){if(l.empty())continue;istringstream in(l);Route r;string cells;in>>r.name>>r.order>>cells;
  if(r.order!="ID"&&r.order!="S_then_T"&&r.order!="T_then_S")throw runtime_error("route order");
  r.inverse.fill(-1);replace(cells.begin(),cells.end(),',',' ');istringstream nums(cells);int v,j=0;
  while(nums>>v){if(v<0||v>=97||j>=97||r.inverse[v]>=0)throw runtime_error("bad permutation");r.inverse[v]=j++;}
  if(j!=97)throw runtime_error("permutation length");out.push_back(r);
 }return out;
}
struct Keys {size_t n;uint64_t start,universe;vector<uint8_t> bytes;
 const uint8_t* row(int pos)const{return bytes.data()+size_t(pos)*n;}
 uint8_t at(int pos,size_t k)const{return bytes[size_t(pos)*n+k];}
};
static Keys keys(const string&family,const string&source,uint64_t start,uint64_t count){
 bool chain=family=="G5"||family=="C6";int lag=family=="G5"?5:6;string src=chain?"":letters(source);
 if(!chain&&src.size()<97)throw runtime_error("source short");uint64_t windows=chain?0:src.size()-96;
 uint64_t universe=chain?(lag==5?100000:1000000):4*windows;
 if(start>=universe)throw runtime_error("start outside key range");uint64_t n=count?min(count,universe-start):universe-start;
 if(n>UINT32_MAX||n*97>uint64_t(1500)*1024*1024)throw runtime_error("key bound");
 Keys k{size_t(n),start,universe,vector<uint8_t>(size_t(n)*97)};
 if(chain){uint64_t div=1;for(int i=lag-1;i>=0;i--){for(size_t j=0;j<n;j++)k.bytes[size_t(i)*n+j]=((start+j)/div)%10;div*=10;}
  for(int i=lag;i<97;i++){auto *dst=k.bytes.data()+size_t(i)*n;const auto*a=k.row(i-lag),*b=k.row(i-lag+1);
   for(size_t j=0;j<n;j++){unsigned x=a[j]+b[j];dst[j]=x>=10?x-10:x;}}
 }else{int inv[2][26];for(int a=0;a<2;a++)for(int i=0;i<26;i++)inv[a][AL[a][i]-'A']=i;
  for(int i=0;i<97;i++)for(size_t j=0;j<n;j++){uint64_t idx=start+j,v=idx/windows,off=idx%windows;
   uint64_t at=v/2?src.size()-1-(off+i):off+i;k.bytes[size_t(i)*n+j]=inv[v%2][src[at]-'A'];}}
 return k;
}
static uint64_t hash_step(uint64_t h,int v){return(h^uint64_t(v+1))*1099511628211ULL;}
int main(int argc,char**argv){try{
 if(argc!=10)throw runtime_error("MODE FAMILY CT WANT ROUTES SOURCE OUT START COUNT");
 auto begin=chrono::steady_clock::now();string mode=argv[1],fam=argv[2],ct=letters(argv[3]),want;
 {ifstream f(argv[4]);getline(f,want);}if(ct.size()!=97||want.size()!=97)throw runtime_error("message length");
 auto rr=routes(argv[5]);auto kk=keys(fam,argv[6],stoull(argv[8]),stoull(argv[9]));
 vector<int> pos,lab;for(int i=0;i<97;i++)if(want[i]!='?'){if(want[i]<'A'||want[i]>'Z')throw runtime_error("want character");pos.push_back(i);lab.push_back(want[i]-'A');}
 if(pos.empty())throw runtime_error("no constraints");int inv[7][26];for(int a=0;a<7;a++)for(int i=0;i<26;i++)inv[a][AL[a][i]-'A']=i;
 uint64_t factor=mode=="32"?12:14;
 if(rr.size()>uint64_t(INT64_MAX)/factor/kk.n)throw runtime_error("count overflow bound");
 uint64_t total=uint64_t(rr.size())*factor*kk.n,consistent=0,index_hits=0;
 vector<uint64_t> hist(pos.size()+1,0),byroute(rr.size(),0);vector<string> survivors;
 if(mode=="32"){
  vector<uint8_t> hits(kk.n);
  for(const auto&r:rr)for(int ca=0;ca<2;ca++)for(int pa=0;pa<2;pa++)for(int op=0;op<3;op++){
   fill(hits.begin(),hits.end(),0);
   for(size_t j=0;j<pos.size();j++){
    int p=pos[j],q=r.order=="ID"?p:r.inverse[p],kp=r.order=="T_then_S"?q:p;
    int c=inv[ca][ct[q]-'A'],v=inv[pa][lab[j]];
    uint8_t required=mod(op==0?c-v:op==1?c+v:v-c);const uint8_t *column=kk.row(kp);uint8_t *h=hits.data();
    for(size_t k=0;k<kk.n;k++)h[k]+=column[k]==required;
   }
   for(uint8_t h:hits)hist[h]++;
  }
  consistent=hist.back();
 }else if(mode=="41"){
  array<int,26> first;first.fill(-1);vector<pair<int,int>> repeated;vector<int> representatives;
  for(size_t j=0;j<lab.size();j++){int &p=first[lab[j]];if(p<0){p=j;representatives.push_back(j);}else repeated.push_back({p,int(j)});}
  vector<pair<uint64_t,uint32_t>> index;index.reserve(kk.n);
  for(size_t k=0;k<kk.n;k++){uint64_t h=1469598103934665603ULL;for(auto [a,b]:repeated)h=hash_step(h,mod(int(kk.at(pos[b],k))-kk.at(pos[a],k)));index.push_back({h,uint32_t(k)});}
  sort(index.begin(),index.end());
  for(size_t ri=0;ri<rr.size();ri++){const auto&r=rr[ri];if(r.order!="S_then_T"&&r.order!="ID")throw runtime_error("41 expects S_then_T");
   for(int ca=0;ca<7;ca++){vector<int> c(pos.size());for(size_t j=0;j<pos.size();j++)c[j]=inv[ca][ct[r.inverse[pos[j]]]-'A'];
    for(int op=0;op<2;op++){uint64_t h=1469598103934665603ULL;for(auto [a,b]:repeated)h=hash_step(h,mod(op==0?c[b]-c[a]:c[a]-c[b]));
     auto it=lower_bound(index.begin(),index.end(),pair<uint64_t,uint32_t>{h,0});
     for(;it!=index.end()&&it->first==h;++it){index_hits++;size_t k=it->second;array<int,26> f,b;f.fill(-1);b.fill(-1);bool good=true;
      for(size_t j=0;j<pos.size();j++){int v=mod(c[j]+(op==0?-1:1)*int(kk.at(pos[j],k))),p=lab[j];
       if((f[p]>=0&&f[p]!=v)||(b[v]>=0&&b[v]!=p)){good=false;break;}f[p]=v;b[v]=p;}
      if(good){consistent++;byroute[ri]++;if(survivors.size()<100)survivors.push_back(to_string(ri)+":"+to_string(ca)+":"+to_string(op)+":"+to_string(kk.start+k));}
     }
    }
   }
  }
 }else throw runtime_error("mode");
 ofstream out(argv[7]);if(!out)throw runtime_error("output open");
 out<<"{\n\"mode\":\""<<mode<<"\",\"family\":\""<<fam<<"\",\"keys\":"<<kk.n<<",\"key_start\":"<<kk.start<<",\"key_universe\":"<<kk.universe<<",\"routes\":"<<rr.size()<<",\"settings\":"<<total<<",\"consistent\":"<<consistent<<",\"index_hits\":"<<index_hits;
 out<<",\"histogram\":[";for(size_t i=0;i<hist.size();i++){if(i)out<<',';out<<hist[i];}out<<"],\"by_route_consistent\":[";
 for(size_t i=0;i<byroute.size();i++){if(i)out<<',';out<<byroute[i];}out<<"],\"survivor_structural_ids\":[";
 for(size_t i=0;i<survivors.size();i++){if(i)out<<',';out<<'"'<<survivors[i]<<'"';}out<<"],\"wall_seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-begin).count()<<"}\n";
 cerr<<mode<<" "<<fam<<" settings="<<total<<" consistent="<<consistent<<" seconds="<<chrono::duration<double>(chrono::steady_clock::now()-begin).count()<<"\n";
 return 0;
 }catch(const exception&e){cerr<<"ERROR "<<e.what()<<"\n";return 2;}}
