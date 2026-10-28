// POST-HOC check: after original 100-candidate blind output was SHA-256 frozen.
// Counts how many of all 1.2M fixed-alphabet Gromark decryptions satisfy two known plaintext fragments.
// NOT used to filter/rank any blind solver output.
#include <iostream>
#include <array>
#include <string>
#include <algorithm>
using namespace std;
const string CT="OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR";
const string AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ",KRY="KRYPTOSABCDEFGHIJLMNQUVWXZ";
int md(int x){x%=26;return x<0?x+26:x;}
int main(){int hits=0,mx=0;long long cnt=0;array<int,25> hist{};
 for(int primer=0;primer<100000;primer++){
   int k[97],v=primer;for(int j=4;j>=0;j--){k[j]=v%10;v/=10;}for(int j=5;j<97;j++)k[j]=(k[j-5]+k[j-4])%10;
   for(auto &pa:{AZ,KRY})for(auto &ca:{AZ,KRY})for(int op=0;op<3;op++){
     int ok=0;for(int i=0;i<24;i++){
       int pos=i<13?21+i:63+i-13;
       char truth=i<13?string("EASTNORTHEAST")[i]:string("BERLINCLOCK")[i-13];
       int c=ca.find(CT[pos]);int idx=md(op==0?c-k[pos]:op==1?k[pos]-c:c+k[pos]);
       if(pa[idx]==truth)ok++;
     }
     hist[ok]++;mx=max(mx,ok);if(ok==24)hits++;cnt++;
   }
 }
 cout<<"Full post-hoc G5 fixed family: total="<<cnt<<", max="<<mx<<"/24, exactly_24="<<hits<<"\n";
 cout<<"Histogram:";for(int i=0;i<25;i++)if(hist[i])cout<<" "<<i<<":"<<hist[i];cout<<"\n";
}
