// R54 supplementary METHOD-ONLY test: within-column coincidence for periods 2..24.
// This file NEVER reads any published K4 plaintext, positions or candidate keys.
// Fixed independent null: 30,000 frequency-preserving ciphertext shuffles.
// A failure to detect periodicity is NOT proof a repeated-key cipher is impossible.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;

static constexpr int N=97, LO=2, HI=24, P=HI-LO+1, TRIALS=30000;

double column_ic(const array<int,N>&x,int period){
    int freq[HI][26]={};
    for(int i=0;i<N;i++)freq[i%period][x[i]]++;
    int hits=0,denominator=0;
    for(int residue=0;residue<period;residue++){
        const int n=(N+period-residue-1)/period;
        denominator+=n*(n-1);
        for(int a=0;a<26;a++)hits+=freq[residue][a]*(freq[residue][a]-1);
    }
    if(denominator<=0)throw runtime_error("no comparable pairs");
    return double(hits)/double(denominator);
}

int main(int argc,char**argv){
    try{
      if(argc!=3)throw runtime_error("usage: period_columns CT_FILE OUTPUT.json");
      ifstream in(argv[1]);if(!in)throw runtime_error("ciphertext not accessible");
      string ct;char ch;
      while(in.get(ch)){
        if(ch=='\n'||ch=='\r')continue;
        if(ch<'A'||ch>'Z')throw runtime_error("only uppercase original ciphertext allowed");
        ct.push_back(ch);
      }
      if(ct.size()!=N)throw runtime_error("97-letter original ciphertext required");
      array<int,N> input{};
      for(int i=0;i<N;i++)input[i]=ct[i]-'A';
      vector<array<double,P>> sims(TRIALS);
      mt19937_64 generator(5410731ULL);
      for(int t=0;t<TRIALS;t++){
        auto shuffled=input;
        shuffle(shuffled.begin(),shuffled.end(),generator);
        for(int period=LO;period<=HI;period++){
            sims[t][period-LO]=column_ic(shuffled,period);
        }
      }
      array<double,P> means{},sds{},observed{},zs{};
      double maxz=-1e9;int best=-1;
      for(int j=0;j<P;j++){
        observed[j]=column_ic(input,j+LO);
        for(int t=0;t<TRIALS;t++)means[j]+=sims[t][j]/double(TRIALS);
        for(int t=0;t<TRIALS;t++)sds[j]+=pow(sims[t][j]-means[j],2)/double(TRIALS);
        sds[j]=sqrt(sds[j]);
        if(sds[j]<=0.0)throw runtime_error("null variance zero");
        zs[j]=(observed[j]-means[j])/sds[j];
        if(zs[j]>maxz){maxz=zs[j];best=j+LO;}
      }
      int exceeded=0;
      for(int t=0;t<TRIALS;t++){
        double m=-1e9;
        for(int j=0;j<P;j++)
            m=max(m,(sims[t][j]-means[j])/sds[j]);
        if(m>=maxz)exceeded++;
      }
      const double familywise=double(exceeded+1)/double(TRIALS+1);
      ofstream out(argv[2]);if(!out)throw runtime_error("report output not writable");
      out<<setprecision(16);
      out<<"{\n";
      out<<"  \"classification\": \"METHOD_ONLY_WITHIN_COLUMN_PERIOD_SCAN_NOT_DECRYPTION\",\n";
      out<<"  \"ciphertext_length\": 97,\n";
      out<<"  \"searched_period_range\": \"2..24\",\n";
      out<<"  \"shuffle_null_trials\": "<<TRIALS<<",\n";
      out<<"  \"null_seed\": 5410731,\n";
      out<<"  \"best_period\": "<<best<<",\n";
      out<<"  \"best_z\": "<<maxz<<",\n";
      out<<"  \"familywise_exceedances\": "<<exceeded<<",\n";
      out<<"  \"familywise_empirical_p\": "<<familywise<<",\n";
      out<<"  \"periods\": [\n";
      for(int j=0;j<P;j++){
        out<<"    {\"period\": "<<j+LO<<", \"observed_column_IC\": "<<observed[j]
           <<", \"null_mean\": "<<means[j]<<", \"null_sd\": "<<sds[j]
           <<", \"z\": "<<zs[j]<<"}"<<(j+1<P?",":"")<<"\n";
      }
      out<<"  ],\n";
      out<<"  \"interpretation\": \"No key or plaintext recovered. A non-significant periodogram does not exclude periodic substitution with 97 letters.\"\n";
      out<<"}\n";
      if(!out)throw runtime_error("failed writing report");
      cerr<<"R54 column IC periods 2..24: best "<<best<<" z "<<maxz
          <<" corrected p "<<familywise<<"\\n";
      return 0;
    }catch(const exception&e){
      cerr<<"R54 method-only periodogram error: "<<e.what()<<"\\n";
      return 1;
    }
}
