// R55 blind affine-feedback cipher search. This compilation unit knows no K4 plaintext.
 // Only inputs: 97-letter uppercase ciphertexts and generic pre-existing quadgram score file.
 // C_i = (a P_i + b + d*i + (i>=L ? sign * SOURCE_(i-L) : 0)) mod 26,
 // SOURCE is previous plaintext or previous ciphertext, never external known plaintext.
#include <algorithm>
#include <array>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
using namespace std;
constexpr int N = 97;
constexpr int ALPH = 26;
constexpr int NUM_FAMILIES = 29952;
constexpr int TOP = 12;
constexpr int QCOUNT = 26*26*26*26;
constexpr array<int,12> MULT = {1,3,5,7,9,11,15,17,19,21,23,25};
int mod(int x) { x %= 26; return x < 0 ? x + 26 : x; }
struct Candidate {
  double score;
  string plain;
  int mode, lag, a, sign, offset, step;
};
bool better(const Candidate& x, const Candidate& y) {
  if (x.score != y.score) return x.score > y.score;
  return tie(x.mode,x.lag,x.a,x.sign,x.offset,x.step)
       < tie(y.mode,y.lag,y.a,y.sign,y.offset,y.step);
}
int inv26(int x) {
  for (int y=1;y<26;y++) if ((x*y)%26==1) return y;
  throw runtime_error("noninvertible multiplier");
}
void verify_forward(const array<int,N>& ct,const Candidate& z) {
  array<int,N> p{},c{};
  if (int(z.plain.size())!=N) throw runtime_error("invalid candidate length");
  for (int i=0;i<N;i++) {
    p[i]=z.plain[i]-'A';
    int feedback=i>=z.lag ? (z.mode==0 ? p[i-z.lag]:c[i-z.lag]):0;
    c[i]=mod(z.a*p[i]+z.offset+z.step*i+z.sign*feedback);
    if(c[i]!=ct[i]) throw runtime_error("forward re-encryption witness failed");
  }
}
void solve_one(const string& id,const string& raw,const vector<float>& Q,ostream& out) {
  if (id.empty() || id.size()>32 ||
      !all_of(id.begin(),id.end(),[](char c){
          return (c>='A'&&c<='Z') || (c>='0'&&c<='9') || c=='_';
      })) throw runtime_error("invalid record id");
  if (raw.size()!=N || !all_of(raw.begin(),raw.end(),[](char c){ return c>='A'&&c<='Z';}))
    throw runtime_error("invalid ciphertext; exact 97 uppercase A-Z required");
  array<int,N> ct{}; for(int i=0;i<N;i++) ct[i]=raw[i]-'A';
  vector<Candidate> top;
  top.reserve(TOP);
  int tried=0;
  for(int mode=0;mode<2;mode++) for(int lag=1;lag<=8;lag++)
    for(int a : MULT) for(int sign : {-1,1})
    for(int offset=0;offset<26;offset++)
    for(int step=-1;step<=1;step++) {
      int ia=inv26(a);
      array<int,N> p{};
      for(int i=0;i<N;i++) {
        int source = (i>=lag) ? (mode==0 ? p[i-lag] : ct[i-lag]) : 0;
        p[i]=mod(ia*mod(ct[i]-offset-step*i-sign*source));
      }
      double score=0;
      for(int i=0;i+3<N;i++) {
        int at=((p[i]*26+p[i+1])*26+p[i+2])*26+p[i+3];
        score+=Q[at];
      }
      if(!isfinite(score)) throw runtime_error("non-finite language-model score");
      tried++;
      Candidate z;
      z.score=score; z.mode=mode; z.lag=lag; z.a=a; z.sign=sign;
      z.offset=offset; z.step=step;
      if(top.size()<TOP || score>=top.back().score) {
        z.plain.resize(N);
        for(int i=0;i<N;i++) z.plain[i]=char('A'+p[i]);
        if(top.size()<TOP || better(z,top.back())) {
          auto pos=lower_bound(top.begin(),top.end(),z,better);
          top.insert(pos,std::move(z));
          if(top.size()>TOP) top.pop_back();
        }
      }
    }
  if(tried!=NUM_FAMILIES || top.size()!=TOP) throw runtime_error("incorrect search scope");
  for(const auto& z:top) verify_forward(ct,z);
  out<<"{\"id\":\""<<id<<"\",\"tested\":"<<tried<<",\"candidates\":[";
  for(size_t j=0;j<top.size();j++) {
    const auto& z=top[j]; if(j) out<<",";
    out<<"{\"method\":\"affine_feedback\",\"mode\":\""
       <<(z.mode==0 ? "plaintext":"ciphertext")
       <<"\",\"lag\":"<<z.lag<<",\"multiplier\":"<<z.a
       <<",\"sign\":"<<z.sign<<",\"offset\":"<<z.offset
       <<",\"step\":"<<z.step<<",\"score\":"<<fixed<<setprecision(8)<<z.score
       <<",\"plaintext\":\""<<z.plain<<"\"}";
  }
  out<<"]}\n";
}
int main(int argc,char** argv) {
  try {
    if(argc!=4) throw runtime_error("usage: r55_blind INPUT.tsv QUAD.f32 OUTPUT.jsonl");
    if(filesystem::exists(argv[3])) throw runtime_error("refuse to overwrite frozen output");
    ifstream model(argv[2],ios::binary|ios::ate);
    if(!model || model.tellg()!=streampos(QCOUNT*sizeof(float)))
      throw runtime_error("incorrect generic quadgram model length");
    model.seekg(0);vector<float> Q(QCOUNT);
    model.read(reinterpret_cast<char*>(Q.data()),Q.size()*sizeof(float));
    if(!model) throw runtime_error("incomplete model");
    ifstream input(argv[1]);if(!input)throw runtime_error("no input");
    ofstream output(argv[3]);if(!output)throw runtime_error("no output");
    string row; int count=0;
    while(getline(input,row)) {
      if(row.empty())throw runtime_error("empty record");
      auto tab=row.find('\t');
      if(tab==string::npos || row.find('\t',tab+1)!=string::npos)
        throw runtime_error("input must have exactly two TSV fields");
      string id=row.substr(0,tab),ct=row.substr(tab+1);
      solve_one(id,ct,Q,output);
      ++count;
      if(count>64)throw runtime_error("too many ciphertexts in batch");
    }
    if(count==0)throw runtime_error("no ciphertexts");
    if(!output)throw runtime_error("write failed");
    cerr<<"R55 blind complete: "<<count<<" inputs, all "<<NUM_FAMILIES
        <<" predeclared method/keys searched each, "<<TOP<<" full results per input\n";
  }catch(const exception& e) {
    cerr<<"R55 BLIND ERROR: "<<e.what()<<"\n";return 1;
  }
}
