// Independent internal sanity tests for the blind mathematical graph, no K4 text or hints.
// Renames the CLI main so that the exact production EdgeGraph is tested.
#define main r43_cli_main
#include "word_constraint_beam.cpp"
#undef main
#include <cassert>
int main(){
  const string AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  {
    EdgeGraph g;
    assert(g.add(0,0,5)); // C(A)-P(A) == 5
    assert(g.add(0,0,5));
    assert(!g.add(0,0,6));
  }
  for(int trial=0;trial<10;trial++){
    mt19937 rng(43000+trial);
    string pa=AZ,ca=AZ;
    shuffle(pa.begin(),pa.end(),rng);
    shuffle(ca.begin(),ca.end(),rng);
    string p,ct;
    array<int,97> key{};
    for(int i=0;i<5;i++)key[i]=rng()%10;
    for(int i=5;i<97;i++)key[i]=(key[i-5]+key[i-4])%10;
    for(int i=0;i<97;i++){
      char x=AZ[rng()%26];p+=x;
      ct+=ca[(pa.find(x)+key[i])%26];
    }
    EdgeGraph g;
    for(int i=0;i<97;i++){
      assert(g.add(p[i]-'A',ct[i]-'A',key[i]));
      assert(g.compatible());
    }
    string gotpa,gotca;
    assert(g.alphabets(gotpa,gotca));
    assert(gotpa.size()==26&&gotca.size()==26);
    assert(gotpa.find('?')==string::npos&&gotca.find('?')==string::npos);
    for(int i=0;i<97;i++)assert(gotca[(gotpa.find(p[i])+key[i])%26]==ct[i]);
  }
  cout<<"R43 GRAPH OK: 10 random 97-letter encryptions, graph and full two-alphabet witnesses"<<endl;
}
