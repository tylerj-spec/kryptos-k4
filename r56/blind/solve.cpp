// R56 blind Chaocipher-style evolving-alphabet exhaustive initial-state search.
// Input contains ONLY ciphertext IDs and ciphertext; no known plaintext/masks/oracles.
// Standard Chaocipher two-wheel postcharacter permuting updates.
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
using namespace std;
constexpr int N=97, TOP=12, QCOUNT=26*26*26*26, WORD_LIMIT=1024;
const string AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ";
struct Key { int side; string alphabet; int phase; };
struct Candidate { double score; string plain; Key key; };
static bool valid_abc(const string& s) {
  return s.size()==26 && set<char>(s.begin(),s.end())==set<char>(AZ.begin(),AZ.end());
}
static bool better(const Candidate& x,const Candidate& y) {
  if(x.score!=y.score) return x.score>y.score;
  return tie(x.key.side,x.key.alphabet,x.key.phase)<tie(y.key.side,y.key.alphabet,y.key.phase);
}
static void rotate_left(string& s,int k) {
  k%=26; rotate(s.begin(),s.begin()+k,s.end());
}
static void wheel_step(string& left,string& right,int idx) {
  rotate_left(left,idx);
  const char l=left.at(1);
  left.erase(1,1);
  left.insert(13,1,l);
  rotate_left(right,idx+1);
  const char r=right.at(2);
  right.erase(2,1);
  right.insert(13,1,r);
}
static void initial(const Key& key,string& left,string& right) {
  if(!valid_abc(key.alphabet) || key.side<0 || key.side>1 || key.phase<0 || key.phase>25)
    throw runtime_error("bad initial rotor key");
  left=key.side==0 ? key.alphabet : AZ;
  right=key.side==1 ? key.alphabet : AZ;
  rotate_left(right,key.phase);
}
static string decrypt(const string& ct,const Key& key) {
  string left,right; initial(key,left,right);
  string plain; plain.reserve(N);
  for(char ch:ct) {
    auto j=left.find(ch);
    if(j==string::npos) throw runtime_error("cipher character not in left wheel");
    plain+=right[j];
    wheel_step(left,right,int(j));
  }
  return plain;
}
static string encrypt(const string& plain,const Key& key) {
  string left,right; initial(key,left,right);
  string ct; ct.reserve(N);
  for(char ch:plain) {
    auto j=right.find(ch);
    if(j==string::npos) throw runtime_error("plaintext character not in right wheel");
    ct+=left[j];
    wheel_step(left,right,int(j));
  }
  return ct;
}
static string kw_alpha(const string& w) {
  string alpha;
  for(char ch:w+AZ) if(alpha.find(ch)==string::npos) alpha+=ch;
  if(!valid_abc(alpha)) throw runtime_error("invalid keyword alphabet");
  return alpha;
}
static vector<string> read_key_alphabets(const string& path) {
  ifstream in(path); if(!in) throw runtime_error("word model unavailable");
  vector<pair<double,string>> ws;
  string word;double freq,other;
  while(in>>word>>freq>>other) {
    if(word.size()>=5 && word.size()<=10 && isfinite(freq) && freq>-1e90 &&
       all_of(word.begin(),word.end(),[](char c){return c>='A'&&c<='Z';}))
      ws.push_back({freq,word});
  }
  if(ws.size()<WORD_LIMIT) throw runtime_error("insufficient generic word candidates");
  sort(ws.begin(),ws.end(),[](const auto& a,const auto& b) {
    if(a.first!=b.first) return a.first>b.first;
    return a.second<b.second;
  });
  ws.resize(WORD_LIMIT);
  set<string> uniq;
  for(auto& w:ws) uniq.insert(kw_alpha(w.second));
  return vector<string>(uniq.begin(),uniq.end());
}
static double ngram_score(const string& p,const vector<float>& q) {
  double score=0;
  for(int i=0;i+3<N;i++){
    const int a=p[i]-'A',b=p[i+1]-'A',c=p[i+2]-'A',d=p[i+3]-'A';
    score+=q[((a*26+b)*26+c)*26+d];
  }
  if(!isfinite(score)) throw runtime_error("nonfinite generic quadgram score");
  return score;
}
static void solve_one(const string& id,const string& ct,
                      const vector<string>& keys,const vector<float>& quad,ostream& out) {
  if(id.empty()||id.size()>32||!all_of(id.begin(),id.end(),[](char c){
    return (c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='_';}))
    throw runtime_error("id must be uppercase alphanumerics or underscore");
  if(ct.size()!=N||!all_of(ct.begin(),ct.end(),[](char c){return c>='A'&&c<='Z';}))
    throw runtime_error("cipher must have exactly 97 uppercase A-Z letters");
  vector<Candidate> top;top.reserve(TOP);
  size_t tried=0;
  for(int side=0;side<2;side++) for(const auto& alpha:keys) for(int phase=0;phase<26;phase++){
    const Key k{side,alpha,phase};
    string plain=decrypt(ct,k);
    double score=ngram_score(plain,quad);tried++;
    if(top.size()==TOP && score<top.back().score) continue;
    Candidate cand{score,std::move(plain),k};
    if(top.size()<TOP||better(cand,top.back())){
      auto it=lower_bound(top.begin(),top.end(),cand,better);
      top.insert(it,std::move(cand));
      if(top.size()>TOP) top.pop_back();
    }
  }
  if(top.size()!=TOP||tried!=52*keys.size()) throw runtime_error("incomplete key search");
  for(const auto& z:top) if(encrypt(z.plain,z.key)!=ct)
    throw runtime_error("independent reversible witness check failed");
  out<<"{\"id\":\""<<id<<"\",\"searched\":"<<tried<<",\"keyword_alphabets\":"
     <<keys.size()<<",\"candidates\":[";
  for(size_t i=0;i<top.size();i++){
    const auto& z=top[i];if(i)out<<",";
    out<<"{\"method\":\"two_wheel_evolving_alphabet\",\"keyword_side\":\""
       <<(z.key.side==0?"left":"right")<<"\",\"keyword_alphabet\":\""
       <<z.key.alphabet<<"\",\"right_initial_phase\":"<<z.key.phase
       <<",\"score\":"<<fixed<<setprecision(8)<<z.score
       <<",\"plaintext\":\""<<z.plain<<"\"}";
  }
  out<<"]}\n";
}
int main(int argc,char** argv) {
  try {
    if(argc!=5)throw runtime_error("usage: blind INPUT.tsv WORD_MODEL.tsv QUAD.f32 OUTPUT.jsonl");
    if(ifstream(argv[4]).good())throw runtime_error("refuse overwrite of prior output");
    vector<string> keys=read_key_alphabets(argv[2]);
    cerr<<"R56: top "<<WORD_LIMIT<<" words produced "<<keys.size()
        <<" unique keyed alphabets; "<<52*keys.size()<<" initial states per input\n";
    ifstream qin(argv[3],ios::binary|ios::ate);
    if(!qin||qin.tellg()!=streampos(QCOUNT*sizeof(float)))throw runtime_error("generic quadgram file size mismatch");
    qin.seekg(0);vector<float> quad(QCOUNT);
    qin.read(reinterpret_cast<char*>(quad.data()),quad.size()*sizeof(float));
    if(!qin)throw runtime_error("quadgram read failed");
    ifstream input(argv[1]);if(!input)throw runtime_error("no input");
    ofstream out(argv[4]);if(!out)throw runtime_error("cannot create output");
    string row;int count=0;
    while(getline(input,row)) {
      size_t tab=row.find('\t');
      if(tab==string::npos || row.find('\t',tab+1)!=string::npos)throw runtime_error("two-column TSV only");
      solve_one(row.substr(0,tab),row.substr(tab+1),keys,quad,out);
      count++;if(count>64)throw runtime_error("too many rows");
    }
    if(count==0||!out)throw runtime_error("empty input or output failed");
    cerr<<"R56 completed "<<count<<" ciphertext-only rows, "<<TOP<<" complete raw output candidates per row\n";
  }catch(const exception& e){cerr<<"R56 ERROR: "<<e.what()<<"\n";return 1;}
}
