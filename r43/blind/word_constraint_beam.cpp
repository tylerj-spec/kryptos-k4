// R43 experimental BLIND solver. No K4 ciphertext, masks, clue words, or known plaintext input.
// Input TSV: id<TAB>ciphertext<TAB>97 decimal key digits (comma-separated).
// Word candidates are selected only from a general language model.
// Model: CA_index(cipher_i) - PA_index(plain_i) == k_i (mod 26).
// Every candidate must have a complete pair of bijective alphabets and forward encrypt exactly.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int N=97, V=52;
static int mod(int v){v%=26;return v<0?v+26:v;}
struct EdgeGraph {
  array<uint8_t,V> parent{},shift{};
  uint8_t components=V;
  EdgeGraph(){for(int i=0;i<V;i++)parent[i]=(uint8_t)i;shift.fill(0);}
  pair<int,int> find(int v)const{
    int p=0;while(parent[v]!=v){p=mod(p+shift[v]);v=parent[v];}
    return {v,p};
  }
  bool add(int plain,int cipher,int delta){
    auto [a,pa]=find(plain);
    auto [b,pb]=find(cipher+26);
    int diff=mod(delta+pa-pb);
    if(a==b)return diff==0;
    parent[b]=(uint8_t)a;shift[b]=(uint8_t)diff;--components;return true;
  }
  bool compatible()const{
    unsigned used[V][2]={};
    for(int i=0;i<V;i++){
      auto [r,p]=find(i);unsigned bit=1u<<p;
      auto &mask=used[r][i>=26];
      if(mask&bit)return false;
      mask|=bit;
    }
    return true;
  }
  bool alphabets(string &pa,string &ca)const{
    struct Comp {int r;int members=0;unsigned mask[2]={};};
    vector<Comp> cs;array<int,V> lookup{};lookup.fill(-1);
    for(int i=0;i<V;i++){
      auto [r,off]=find(i);
      int idx=lookup[r];if(idx<0){idx=(int)cs.size();lookup[r]=idx;cs.push_back({r,0,{0,0}});}
      auto &co=cs[idx];unsigned bit=1u<<off;
      if(co.mask[i>=26]&bit)return false;
      co.mask[i>=26]|=bit;co.members++;
    }
    sort(cs.begin(),cs.end(),[](const Comp&a,const Comp&b){return a.members>b.members;});
    array<int,V> chosen{};chosen.fill(-1);
    const auto rotate=[&](unsigned mask,int offset){
      if(offset==0)return mask;
      return ((mask<<offset)|(mask>>(26-offset)))&((1u<<26)-1);
    };
    auto recurse=[&](auto &&self,int j,unsigned u0,unsigned u1)->bool{
      if(j==(int)cs.size())return true;
      const auto &co=cs[j];
      // Fix a harmless global rotation to zero; valid because only differences matter.
      for(int off=0;off<(j==0?1:26);off++){
        unsigned m0=rotate(co.mask[0],off),m1=rotate(co.mask[1],off);
        if((m0&u0)||(m1&u1))continue;
        chosen[co.r]=off;
        if(self(self,j+1,u0|m0,u1|m1))return true;
      }
      chosen[co.r]=-1;return false;
    };
    if(!recurse(recurse,0,0,0))return false;
    pa.assign(26,'?');ca.assign(26,'?');
    for(int i=0;i<V;i++){
      auto [root,off]=find(i);
      int rank=mod(off+chosen[root]);char letter='A'+(i%26);
      auto &a=i<26?pa:ca;
      if(a[rank]!='?')return false;
      a[rank]=letter;
    }
    return pa.find('?')==string::npos&&ca.find('?')==string::npos;
  }
};
struct Word {string s;double w;};
struct State {
  EdgeGraph g;
  string plain,seg;
  double score=0,priority=0;
};
struct Options {int width=256,per_length=128,max_len=17;double cycle_weight=0.0;};
static vector<vector<Word>> model_words(const string&path,const Options&opt){
  ifstream in(path);if(!in)throw runtime_error("word model unavailable");
  vector<vector<Word>> out(opt.max_len+1);
  string word;double ex,ed;
  while(in>>word>>ex>>ed){
    if(word.empty()||word.size()>(size_t)opt.max_len||!isfinite(ex)||ex < -1e50)continue;
    bool valid=all_of(word.begin(),word.end(),[](char c){return c>='A'&&c<='Z';});
    if(valid)out[word.size()].push_back({word,ex});
  }
  int count=0;
  for(int l=1;l<=opt.max_len;l++){
    auto &ws=out[l];
    sort(ws.begin(),ws.end(),[](const Word&a,const Word&b){
      return a.w==b.w?a.s<b.s:a.w>b.w;});
    if((int)ws.size()>opt.per_length)ws.resize(opt.per_length);
    count+=(int)ws.size();
  }
  // The 97-character ciphertext can end mid-word, and real texts have proper
  // names. The existing ORTH language model permits unmatched letters at -7.
  // Retain that exact fallback so we do not require a fully word-segmentable text.
  for(int v=0;v<26;v++) {
    string one(1,char('A'+v));
    auto it=find_if(out[1].begin(),out[1].end(),
       [&](const Word &w){return w.s==one;});
    if(it==out[1].end())out[1].push_back({one,-7.0});
    else it->w=max(it->w,-7.0);
  }
  count=0;for(int l=1;l<=opt.max_len;l++)count+=(int)out[l].size();
  if(count<100)throw runtime_error("word model too small");
  cerr<<"R43 dictionary words "<<count<<" per_length "<<opt.per_length<<"\n";
  return out;
}
static bool sort_by_score(const State&a,const State&b){
  return a.priority>b.priority||(a.priority==b.priority&&a.plain<b.plain);
}
static void push_bounded(vector<State>&v,State&&s,int limit){
  v.push_back(move(s));
  if((int)v.size()>=limit*2){
    nth_element(v.begin(),v.begin()+limit,v.end(),sort_by_score);
    v.resize(limit);
  }
}
struct Answer {string plain,pa,ca,seg;double score;long long proposed,valid_graph,full_graph,full_bijections;};
static Answer solve(const string&ct,const vector<int>&key,
                   const vector<vector<Word>>&dictionary,const Options&opt){
  vector<vector<State>> at(N+1);
  at[0].emplace_back();
  long long proposed=0,passed=0,full=0,full_bij=0;Answer answer{"","","","",-1e100,0,0,0,0};
  for(int pos=0;pos<N;pos++){
    auto &cur=at[pos];if(cur.empty())continue;
    if((int)cur.size()>opt.width){
      nth_element(cur.begin(),cur.begin()+opt.width,cur.end(),sort_by_score);
      cur.resize(opt.width);
    }
    for(const State &state:cur){
      for(int len=1;len<=opt.max_len&&pos+len<=N;len++){
        for(const Word &w:dictionary[len]){
          proposed++;
          EdgeGraph next=state.g;
          bool ok=true;
          for(int j=0;j<len;j++){
            if(!next.add(w.s[j]-'A',ct[pos+j]-'A',key[pos+j])){
              ok=false;break;
            }
          }
          if(!ok||!next.compatible())continue;
          passed++;
          State s;
          s.g=next;s.plain=state.plain+w.s;
          s.seg=state.seg.empty()?w.s:state.seg+" "+w.s;
          s.score=state.score+w.w;
          int cycles=(pos+len)-(V-int(s.g.components));
          s.priority=s.score+opt.cycle_weight*cycles;
          if(pos+len==N){
            ++full;
            if(s.score<=answer.score)continue;
            string pa,ca;
            if(!s.g.alphabets(pa,ca))continue;
            ++full_bij;
            // Independent forward encryption (not a reward signal).
            bool forward=true;
            for(int i=0;i<N;i++){
              size_t idx=pa.find(s.plain[i]);
              if(idx==string::npos||ca[(idx+key[i])%26]!=ct[i]){
                forward=false;break;
              }
            }
            if(forward)answer={s.plain,pa,ca,s.seg,s.score,proposed,passed,full,full_bij};
          }else push_bounded(at[pos+len],move(s),opt.width);
        }
      }
    }
  }
  answer.proposed=proposed;answer.valid_graph=passed;
  answer.full_graph=full;answer.full_bijections=full_bij;
  return answer;
}
static vector<int> key_parse(string raw){
  vector<int> key;
  for(char &c:raw)if(c==',')c=' ';
  stringstream s(raw);int x;
  while(s>>x){if(x<0||x>9)throw runtime_error("key digits must be in 0..9");key.push_back(x);}
  if(key.size()!=N)throw runtime_error("expected exactly 97 key digits");
  return key;
}
static vector<string> tab(const string&l){
  vector<string> r;stringstream ss(l);string x;
  while(getline(ss,x,'\t'))r.push_back(x);
  return r;
}
static string json_escape(const string&s){
  string out;for(char c:s){if(c=='"'||c=='\\')out+='\\';out+=c;}return out;
}
int main(int argc,char**argv){
 try{
  if(argc<4||argc>8)throw runtime_error("usage: solver MODEL.tsv INPUT.tsv OUTPUT.jsonl [BEAM_WIDTH=256] [PER_LEN=128] [MAX_LEN=17] [CYCLE_BONUS=0]");
  Options o;if(argc>=5)o.width=stoi(argv[4]);if(argc>=6)o.per_length=stoi(argv[5]);if(argc>=7)o.max_len=stoi(argv[6]);if(argc>=8)o.cycle_weight=stod(argv[7]);
  if(o.width<1||o.width>20000||o.per_length<1||o.per_length>20000||o.max_len<1||o.max_len>24||o.cycle_weight<0||o.cycle_weight>20)throw runtime_error("invalid budget");
  auto dictionary=model_words(argv[1],o);
  ifstream fin(argv[2]);ofstream out(argv[3]);
  if(!fin||!out)throw runtime_error("input or output inaccessible");
  string l;int count=0;
  while(getline(fin,l)){
    if(l.empty()||l[0]=='#'||l.rfind("id\t",0)==0)continue;
    auto col=tab(l);
    if(col.size()!=3)throw runtime_error("expected TSV id, ct, digits: "+l.substr(0,50));
    const string &id=col[0],&ct=col[1];
    if(ct.size()!=N||!all_of(ct.begin(),ct.end(),[](char c){return c>='A'&&c<='Z';}))throw runtime_error("invalid ciphertext");
    auto key=key_parse(col[2]);
    auto ans=solve(ct,key,dictionary,o);
    out<<"{\"id\":\""<<json_escape(id)<<"\",\"plaintext\":\""<<ans.plain
       <<"\",\"plaintext_alphabet\":\""<<ans.pa<<"\",\"ciphertext_alphabet\":\""<<ans.ca
       <<"\",\"segmented\":\""<<ans.seg<<"\",\"score\":"<<setprecision(12)<<ans.score
       <<",\"proposals\":"<<ans.proposed<<",\"compatible\":"<<ans.valid_graph
       <<",\"full_graph\":"<<ans.full_graph<<",\"full_bijections\":"<<ans.full_bijections<<"}\n";
    out.flush();
    cerr<<"R43 "<<id<<" valid="<<(!ans.pa.empty())<<" proposals="<<ans.proposed
        <<" graph_pass="<<ans.valid_graph<<" full_graph="<<ans.full_graph
        <<" full_bijections="<<ans.full_bijections
        <<" best_score="<<ans.score<<"\n";
    count++;
  }
  if(!count)throw runtime_error("no input ciphertexts");
 }catch(const exception&e){cerr<<"R43 ERROR "<<e.what()<<"\n";return 1;}
 return 0;
}
