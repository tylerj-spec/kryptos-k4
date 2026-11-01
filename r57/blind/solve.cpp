// R57 blind exhaustive 2x2 Hill digraphic cipher search, invertible over Z26.
// Odd-length convention: fixed X padding for last character, discard second output.
// Only original ciphertext and generic quadgram scores enter this executable.
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
using namespace std;
constexpr int N=97, TOP=12, EXPECTED=97344, QCOUNT=26*26*26*26;
struct Key{int a,b,c,d;};
struct Candidate{double score;string plain;Key key;};
static bool better(const Candidate& x,const Candidate& y){
  if(x.score!=y.score)return x.score>y.score;
  return tie(x.key.a,x.key.b,x.key.c,x.key.d)
       < tie(y.key.a,y.key.b,y.key.c,y.key.d);
}
static int m26(int v){v%=26;return v<0?v+26:v;}
static int inv(int v){
  for(int a=1;a<26;a++)if(m26(v*a)==1)return a;
  return -1;
}
static int forward_at(int x,int y,int a,int b){
  return m26(a*x+b*y);
}
static bool valid_key(const Key& k){
  return inv(k.a)>=0 && inv(m26(k.a*k.d-k.b*k.c))>=0;
}
static string encrypt(const string& p,const Key& k){
  if(p.size()!=N||!valid_key(k))throw runtime_error("bad witness");
  string c; c.resize(N);
  for(int i=0;i<96;i+=2){
    const int x=p[i]-'A',y=p[i+1]-'A';
    c[i]=char('A'+forward_at(x,y,k.a,k.b));
    c[i+1]=char('A'+forward_at(x,y,k.c,k.d));
  }
  c[96]=char('A'+forward_at(p[96]-'A',23,k.a,k.b));
  return c;
}
static void solve_one(const string& id,const string& ct,const vector<float>& Q,ostream& out){
  if(id.empty()||id.size()>32||!all_of(id.begin(),id.end(),[](char c){
     return(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='_';}))
    throw runtime_error("invalid id");
  if(ct.size()!=N||!all_of(ct.begin(),ct.end(),[](char c){return c>='A'&&c<='Z';}))
    throw runtime_error("exactly 97 uppercase A-Z ciphertext letters required");
  array<int,N> cipher{},p{};
  for(int i=0;i<N;i++)cipher[i]=ct[i]-'A';
  vector<Candidate> top;top.reserve(TOP);
  int count=0;
  for(int a=1;a<26;a++) {
    int inverse_a=inv(a);
    if(inverse_a<0)continue;
    for(int b=0;b<26;b++)for(int c=0;c<26;c++)for(int d=0;d<26;d++){
      const int idet=inv(m26(a*d-b*c));
      if(idet<0)continue;
      for(int i=0;i<96;i+=2){
        const int u=cipher[i],v=cipher[i+1];
        p[i]=m26(idet*(d*u-b*v));
        p[i+1]=m26(idet*(-c*u+a*v));
      }
      p[96]=m26(inverse_a*(cipher[96]-b*23));
      double score=0;
      for(int i=0;i+3<N;i++){
        const int at=((p[i]*26+p[i+1])*26+p[i+2])*26+p[i+3];
        score+=Q[at];
      }
      if(!isfinite(score))throw runtime_error("nonfinite generic language model");
      count++;
      if(top.size()==TOP && score<top.back().score)continue;
      Candidate z;z.score=score;z.key={a,b,c,d};z.plain.resize(N);
      for(int i=0;i<N;i++)z.plain[i]=char('A'+p[i]);
      if(top.size()<TOP||better(z,top.back())){
        auto it=lower_bound(top.begin(),top.end(),z,better);
        top.insert(it,std::move(z));
        if(top.size()>TOP)top.pop_back();
      }
    }
  }
  if(count!=EXPECTED||top.size()!=TOP)throw runtime_error("unexpected Hill key-space coverage");
  for(const auto& z:top)if(encrypt(z.plain,z.key)!=ct)
    throw runtime_error("forward witness invalid");
  out<<"{\"id\":\""<<id<<"\",\"searched\":"<<count<<",\"candidates\":[";
  for(size_t j=0;j<top.size();j++){
    const auto& z=top[j];if(j)out<<",";
    out<<"{\"method\":\"hill_2x2_mod26_padded_truncation\","
       <<"\"a\":"<<z.key.a<<",\"b\":"<<z.key.b<<",\"c\":"<<z.key.c<<",\"d\":"<<z.key.d
       <<",\"score\":"<<fixed<<setprecision(8)<<z.score
       <<",\"plaintext\":\""<<z.plain<<"\"}";
  }
  out<<"]}\n";
}
int main(int argc,char**argv){
  try{
    if(argc!=4)throw runtime_error("usage: solve INPUT.tsv QUAD.f32 OUTPUT.jsonl");
    if(ifstream(argv[3]).good())throw runtime_error("do not overwrite frozen output");
    ifstream q(argv[2],ios::binary|ios::ate);
    if(!q||q.tellg()!=streampos(QCOUNT*sizeof(float)))throw runtime_error("invalid quad score file");
    q.seekg(0);vector<float> quad(QCOUNT);
    q.read(reinterpret_cast<char*>(quad.data()),quad.size()*sizeof(float));
    if(!q)throw runtime_error("model read failure");
    ifstream in(argv[1]);if(!in)throw runtime_error("missing ciphertext input");
    ofstream out(argv[3]);if(!out)throw runtime_error("cannot create raw output");
    string row;int n=0;
    while(getline(in,row)){
      const auto tab=row.find('\t');
      if(tab==string::npos||row.find('\t',tab+1)!=string::npos)
         throw runtime_error("two-field ciphertext TSV only");
      solve_one(row.substr(0,tab),row.substr(tab+1),quad,out);
      n++;if(n>64)throw runtime_error("too many inputs");
    }
    if(n==0||!out)throw runtime_error("empty or failed output");
    cerr<<"R57 complete: "<<n<<" inputs x "<<EXPECTED
        <<" exhaustive invertible Hill keys, "<<TOP<<" raw plaintexts each\n";
  }catch(const exception& e){cerr<<"R57 ERROR: "<<e.what()<<"\n";return 1;}
}
