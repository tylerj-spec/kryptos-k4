// R40: independent ciphertext-only Gromark IC null audit.
// Reads original 97 letters, no plaintext, clues, masks or language model.
// 100,000 base-ten five-digit primers compressed by exact unit orbits.
// Usage: null_gate CT_FILE [NULL_COUNT=1000] [SEED=40001]
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int N=97, PAIRS=N*(N-1)/2, WORDS=(PAIRS+63)/64;
using Bits=array<uint64_t,WORDS>;
struct Class {Bits same{}; int den=0,prime=0;};
struct Hit {int n,d,prime,ties;double score()const{return double(n)/d;}};
int scale(int p,int u) {
  int a[5];for(int i=4;i>=0;--i){a[i]=p%10;p/=10;}
  int q=0;for(int x:a)q=10*q+(u*x)%10;return q;
}
array<int,N> stream(int p) {
  array<int,N> k{};for(int i=4;i>=0;--i){k[i]=p%10;p/=10;}
  for(int i=5;i<N;++i)k[i]=(k[i-5]+k[i-4])%10;
  return k;
}
string read_ct(const char* f) {
  ifstream in(f,ios::binary);if(!in)throw runtime_error("ciphertext read failed");
  string s((istreambuf_iterator<char>(in)),{});
  for(char& c:s)if(c>='a'&&c<='z')c=char(c-'a'+'A');
  s.erase(remove_if(s.begin(),s.end(),[](char c){return c<'A'||c>'Z';}),s.end());
  if(s.size()!=N)throw runtime_error("ciphertext must be exactly 97 letters");
  return s;
}
vector<array<int,2>> pairs() {
  vector<array<int,2>> ps;for(int i=0;i<N;++i)for(int j=i+1;j<N;++j)ps.push_back({i,j});
  if(ps.size()!=PAIRS)throw runtime_error("invalid pairs");return ps;
}
Bits equal_letters(const string& ct,const vector<array<int,2>>& ps) {
  Bits b{};for(int t=0;t<PAIRS;++t)if(ct[ps[t][0]]==ct[ps[t][1]])b[t/64]|=1ULL<<(t%64);return b;
}
vector<Class> make_classes(const vector<array<int,2>>& ps) {
  vector<Class> ret;
  for(int p=0;p<100000;++p) {
    if(p!=min({scale(p,1),scale(p,3),scale(p,7),scale(p,9)}))continue;
    Class c;c.prime=p;auto k=stream(p);
    for(int t=0;t<PAIRS;++t)if(k[ps[t][0]]==k[ps[t][1]])c.same[t/64]|=1ULL<<(t%64);
    for(auto w:c.same)c.den+=__builtin_popcountll(w);
    if(!c.den)throw runtime_error("zero denominator");ret.push_back(c);
  }
  if(ret.size()!=25024)throw runtime_error("expected 25024 equivalence classes");
  return ret;
}
pair<int,int> direct(const string& ct,int primer) {
  auto k=stream(primer);int group[10]{},m[10][26]{};
  for(int i=0;i<N;++i){int g=k[i],x=ct[i]-'A';++group[g];++m[g][x];}
  int n=0,d=0;for(int g=0;g<10;++g){
    d+=group[g]*(group[g]-1);
    for(int x=0;x<26;++x)n+=m[g][x]*(m[g][x]-1);
  }
  return {n/2,d/2};
}
Hit scan(const Bits& letters,const vector<Class>& classes) {
  Hit best{-1,1,-1,0};
  for(const auto& c:classes) {
    int n=0;for(int w=0;w<WORDS;++w)n+=__builtin_popcountll(letters[w]&c.same[w]);
    auto a=int64_t(n)*best.d,b=int64_t(best.n)*c.den;
    if(a>b)best={n,c.den,c.prime,1};else if(a==b)++best.ties;
  }
  return best;
}
int main(int argc,char** argv) {
 try{
  if(argc<2||argc>4)throw runtime_error("usage: null_gate CT [COUNT] [SEED]");
  string ct=read_ct(argv[1]);int count=argc>2?stoi(argv[2]):1000;
  if(count<1||count>100000)throw runtime_error("invalid null count");
  uint64_t seed=argc>3?stoull(argv[3]):40001ULL;
  auto ps=pairs(),classes=make_classes(ps);
  for(int p:{0,42,27641,49287,61823,83469,99999}) {
    auto k=stream(p);int n=0,d=0;
    for(auto ij:ps)if(k[ij[0]]==k[ij[1]]){++d;n+=ct[ij[0]]==ct[ij[1]];}
    if(direct(ct,p)!=make_pair(n,d))throw runtime_error("bitset/reference disagreement");
  }
  auto k4=scan(equal_letters(ct,ps),classes);
  if(k4.prime!=27641||fabs(k4.score()-0.07510729613733906)>1e-14)
    throw runtime_error("independent R39 K4 maximum mismatch");
  for(int u:{3,7,9})if(direct(ct,scale(27641,u))!=direct(ct,27641))
    throw runtime_error("unit-equivalence check failed");
  mt19937_64 rng(seed);int ge=0,eq=0;
  vector<double> values;values.reserve(count);
  cout<<setprecision(17)<<"kind\tindex\tmax_ic\tcanonical_primer\ttied_classes\n";
  cout<<"K4\t0\t"<<k4.score()<<"\t"<<setw(5)<<setfill('0')<<k4.prime<<setfill(' ')<<"\t"<<k4.ties<<"\n";
  for(int j=0;j<count;++j) {
    string shuffled=ct;shuffle(shuffled.begin(),shuffled.end(),rng);
    auto found=scan(equal_letters(shuffled,ps),classes);values.push_back(found.score());
    if(int64_t(found.n)*k4.d>=int64_t(k4.n)*found.d){++ge;
      if(int64_t(found.n)*k4.d==int64_t(k4.n)*found.d)++eq;}
    cout<<"NULL\t"<<j<<"\t"<<found.score()<<"\t"<<setw(5)<<setfill('0')
        <<found.prime<<setfill(' ')<<"\t"<<found.ties<<"\n";
  }
  sort(values.begin(),values.end());
  auto quant=[&](double q){return values[size_t((count-1)*q)];};
  cerr<<setprecision(17)<<"R40 n_null="<<count<<" seed="<<seed
      <<" n_classes="<<classes.size()<<" k4_ic="<<k4.score()
      <<" n_ge="<<ge<<" n_equal="<<eq<<" empirical_exceedance_p="<<double(ge+1)/(count+1)
      <<" null_p05="<<quant(.05)<<" null_p50="<<quant(.5)<<" null_p95="<<quant(.95)<<"\n";
 }catch(const exception& e){cerr<<"R40 ERROR "<<e.what()<<"\n";return 1;}
}
