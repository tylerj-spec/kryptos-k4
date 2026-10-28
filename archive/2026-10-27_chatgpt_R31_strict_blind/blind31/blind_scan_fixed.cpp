// R31: NO CRIBS OR KNOWN PLAINTEXT. Reads ONLY ciphertext, Carter AZ, quadgram log score.
// All candidate selection from original ciphertext + independent language model, not from known answers.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int N=97; constexpr int TOP=100;
const string AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const string KRY="KRYPTOSABCDEFGHIJLMNQUVWXZ";
struct Hit { double score; string plain, setting, key; int off; };
struct MinScore { bool operator()(const Hit& a,const Hit& b)const{return a.score>b.score;} };
string readall(const string& f){ifstream in(f,ios::binary);if(!in)throw runtime_error("no file "+f);return string(istreambuf_iterator<char>(in),{});}
int md(int x){x%=26;return x<0?x+26:x;}
vector<float> Q;
int main(int argc, char** argv){
  try {
  if(argc!=6) throw runtime_error("usage: blind_scan_fixed G5|CARTER CIPHERTEXT.txt QUAD.f32 CARTER_AZ.txt|- OUTPUT.tsv");
  string family=argv[1],ciph=readall(argv[2]),book = family=="CARTER"?readall(argv[4]):"";
  ciph.erase(remove_if(ciph.begin(),ciph.end(),[](char x){return x=='\n'||x=='\r'||x==' ';}),ciph.end());
  if(ciph.size()!=N||any_of(ciph.begin(),ciph.end(),[](char c){return c<'A'||c>'Z';}))throw runtime_error("original CT must be 97 A-Z letters");
  if(family!="G5"&&family!="CARTER")throw runtime_error("bad family");
  if(family=="CARTER"&&(book.size()<97||any_of(book.begin(),book.end(),[](char c){return c<'A'||c>'Z';})))throw runtime_error("bad book source");
  {ifstream f(argv[3],ios::binary);Q.resize(26*26*26*26);f.read(reinterpret_cast<char*>(Q.data()),Q.size()*4);if(!f) throw runtime_error("bad quad table");}
  int map_p[2][26],map_c[2][26], map_key[2][26];
  for(int h=0;h<2;h++){
    auto a=(h?KRY:AZ);
    for(int i=0;i<26;i++){map_p[h][i]=a[i]-'A';map_c[h][a[i]-'A']=i;map_key[h][a[i]-'A']=i;}
  }
  priority_queue<Hit,vector<Hit>,MinScore> best;
  auto eval=[&](const array<int,N>& k, const string& setting,int off){
    for(int pa=0;pa<2;pa++)for(int ca=0;ca<2;ca++)for(int op=0;op<3;op++){
      int vals[N]; char letters[N+1];
      for(int j=0;j<N;j++){
        int c=map_c[ca][ciph[j]-'A'];
        int idx=md(op==0?(c-k[j]):(op==1?(k[j]-c):(c+k[j])));
        vals[j]=map_p[pa][idx];letters[j]=char('A'+vals[j]);
      }
      letters[N]=0;
      double sc=0;for(int i=3;i<N;i++) sc+=Q[((vals[i-3]*26+vals[i-2])*26+vals[i-1])*26+vals[i]];
      if(best.size()<TOP || sc>best.top().score){
        Hit x{sc,string(letters),setting+"/PA="+(pa?"KRY":"AZ")+"/CA="+(ca?"KRY":"AZ")+"/OP="+(op==0?"VIG":op==1?"BEAU":"VARB"),"",off};
        if(best.size()>=TOP)best.pop();best.push(move(x));
      }
    }
  };
  size_t sets=0;
  if(family=="G5"){
    for(int primer=0;primer<100000;primer++){
      array<int,N> k{};int n=primer;for(int i=4;i>=0;i--){k[i]=n%10;n/=10;}
      for(int i=5;i<N;i++)k[i]=(k[i-5]+k[i-4])%10;
      eval(k,"G5/PRIMER="+to_string(primer),primer);sets+=12;
    }
  } else {
    int num_windows=int(book.size())-96;
    for(int reverse=0;reverse<2;reverse++){
      const string& b=(reverse?string(book.rbegin(),book.rend()):book);
      for(int kn=0;kn<2;kn++){
        for(int offset=0;offset<num_windows;offset++){
          array<int,N> k;
          for(int i=0;i<N;i++)k[i]=map_key[kn][b[offset+i]-'A'];
          eval(k,string("CARTER/DIR=")+(reverse?"REVERSE":"FORWARD")+"/KEYNUM="+(kn?"KRY":"AZ"),offset);
          sets+=12;
        }
      }
    }
  }
  vector<Hit> rows;while(!best.empty()){rows.push_back(best.top());best.pop();}
  sort(rows.begin(),rows.end(),[](auto& a,auto& b){if(a.score!=b.score)return a.score>b.score;return a.setting<b.setting;});
  ofstream o(argv[5]);o<<"rank\tscore_quad\tmodel\tsetting\toffset\tplaintext\n"<<setprecision(11);
  for(size_t i=0;i<rows.size();i++)o<<(i+1)<<"\t"<<rows[i].score<<"\t"<<family<<"\t"<<rows[i].setting<<"\t"<<rows[i].off<<"\t"<<rows[i].plain<<"\n";
  cerr<<"BLIND RUN family="<<family<<" settings="<<sets<<" top score="<<rows[0].score<<" top plaintext="<<rows[0].plain<<"\n";
  } catch(const exception& e){cerr<<"ERROR "<<e.what()<<"\n";return 1;}return 0;
}
