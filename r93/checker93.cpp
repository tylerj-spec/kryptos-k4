// R93 exact compatibility kernel. No plaintext decoding or wiring completion.
// A result contains omission bits 0..k-1 and EXACT in bit k. It is not a key.
#include <array>
#include <cstdint>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

static int mod(int x, int q) { int r=x%q; return r<0 ? r+q : r; }

static uint32_t compatibility(const std::vector<int>& x, const std::vector<int>& y) {
    const size_t k=x.size();
    if (k!=y.size() || k<1 || k>24) throw std::runtime_error("bad pair count");
    uint32_t omissions=(uint32_t(1)<<k)-1;
    bool conflict=false;
    for (size_t a=0; a<k; ++a) {
        for (size_t b=a+1; b<k; ++b) {
            if ((x[a]==x[b]) != (y[a]==y[b])) {
                conflict=true;
                omissions &= (uint32_t(1)<<a) | (uint32_t(1)<<b);
                if (!omissions) return 0;
            }
        }
    }
    return omissions | (conflict ? 0 : (uint32_t(1)<<k));
}

static void append_word(std::vector<char>& bytes, uint32_t word) {
    for (int shift=0; shift<32; shift+=8) bytes.push_back(char((word>>shift)&255));
}

static std::array<int,256> index_alphabet(const std::string& alphabet, int q) {
    if (int(alphabet.size())!=q) throw std::runtime_error("bad alphabet length");
    std::array<int,256> index;
    index.fill(-1);
    for (int j=0; j<q; ++j) {
        unsigned char c=alphabet[j];
        if (index[c]!=-1) throw std::runtime_error("duplicate alphabet symbol");
        index[c]=j;
    }
    return index;
}

static uint32_t one_setting(int q, int length, const std::vector<int>& positions,
        const std::string& observed, const std::string& ciphertext,
        const std::string& input_alphabet, const std::string& output_alphabet,
        int n, int phase, int direction) {
    if (q<2 || q>26 || n<1 || phase<0 || phase>=n || (direction!=-1 && direction!=1))
        throw std::runtime_error("bad structural input");
    if (int(ciphertext.size())!=length || observed.size()!=positions.size())
        throw std::runtime_error("bad text length");
    auto in=index_alphabet(input_alphabet,q), out=index_alphabet(output_alphabet,q);
    std::vector<int> x, y;
    std::vector<bool> used(length,false);
    for (size_t j=0; j<positions.size(); ++j) {
        int position=positions[j];
        if (position<0 || position>=length || used[position]) throw std::runtime_error("bad position");
        used[position]=true;
        int p=in[static_cast<unsigned char>(observed[j])];
        int c=out[static_cast<unsigned char>(ciphertext[position])];
        if (p<0 || c<0) throw std::runtime_error("symbol outside alphabet");
        int offset=direction*((position+phase)/n);
        x.push_back(mod(p+offset,q));
        y.push_back(mod(c+offset,q));
    }
    return compatibility(x,y);
}

static void pair_mode() {
    std::string line;
    std::vector<char> bytes;
    while (std::getline(std::cin,line)) {
        if (line.empty()) continue;
        std::istringstream stream(line);
        int q,k;
        if (!(stream>>q>>k) || q<2 || q>26 || k<1 || k>24) throw std::runtime_error("bad pair header");
        std::vector<int> x(k),y(k);
        for (int j=0; j<k; ++j)
            if (!(stream>>x[j]>>y[j]) || x[j]<0 || x[j]>=q || y[j]<0 || y[j]>=q)
                throw std::runtime_error("bad numeric pair");
        std::string extra;
        if (stream>>extra) throw std::runtime_error("extra input field");
        append_word(bytes,compatibility(x,y));
        if (bytes.size()>=65536) { std::cout.write(bytes.data(),bytes.size()); bytes.clear(); }
    }
    std::cout.write(bytes.data(),bytes.size());
}

static void setting_mode() {
    std::string line;
    std::vector<char> bytes;
    while (std::getline(std::cin,line)) {
        if (line.empty()) continue;
        std::istringstream stream(line);
        int q,length,k,n,phase,direction;
        std::string ia,oa,ciphertext,observed;
        if (!(stream>>q>>length>>k>>n>>phase>>direction>>ia>>oa>>ciphertext>>observed)
            || k<1 || k>24 || length<1 || length>1000) throw std::runtime_error("bad setting header");
        std::vector<int> positions(k);
        for (int& position:positions) if (!(stream>>position)) throw std::runtime_error("missing position");
        std::string extra;
        if (stream>>extra) throw std::runtime_error("extra input field");
        append_word(bytes,one_setting(q,length,positions,observed,ciphertext,ia,oa,n,phase,direction));
        if (bytes.size()>=65536) { std::cout.write(bytes.data(),bytes.size()); bytes.clear(); }
    }
    std::cout.write(bytes.data(),bytes.size());
}

static void scan_mode() {
    std::string magic;
    int count,length,k;
    if (!(std::cin>>magic>>count>>length>>k) || magic!="R93SCAN1" || count<1 || count>201
        || length!=97 || k!=24) throw std::runtime_error("bad scan header");
    std::array<std::string,4> alphabets;
    std::array<std::array<int,256>,4> indices;
    for (int a=0;a<4;++a) { std::cin>>alphabets[a]; indices[a]=index_alphabet(alphabets[a],26); }
    std::vector<int> positions(k);
    std::vector<bool> used(length,false);
    for (int& p:positions) {
        if (!(std::cin>>p) || p<0 || p>=length || used[p]) throw std::runtime_error("bad scan position");
        used[p]=true;
    }
    std::string observations;
    std::cin>>observations;
    if (int(observations.size())!=k) throw std::runtime_error("bad observation length");
    std::array<std::array<int,24>,4> plain_index;
    for (int a=0;a<4;++a) for (int j=0;j<k;++j) {
        plain_index[a][j]=indices[a][static_cast<unsigned char>(observations[j])];
        if (plain_index[a][j]<0) throw std::runtime_error("bad observed symbol");
    }
    for (int item=0;item<count;++item) {
        std::string id,ciphertext;
        if (!(std::cin>>id>>ciphertext) || int(ciphertext.size())!=length) throw std::runtime_error("bad input item");
        for (char c:ciphertext) if (c<'A' || c>'Z') throw std::runtime_error("bad ciphertext symbol");
        std::array<std::array<int,24>,4> cipher_index;
        for (int a=0;a<4;++a) for (int j=0;j<k;++j) {
            cipher_index[a][j]=indices[a][static_cast<unsigned char>(ciphertext[positions[j]])];
            if (cipher_index[a][j]<0) throw std::runtime_error("bad cipher alphabet");
        }
        std::vector<char> bytes;
        bytes.reserve(145728*4);
        std::vector<int> x(k),y(k),offset(k);
        for (int n=5;n<=96;++n) for (int phase=1;phase<n;++phase) for (int direction:{-1,1}) {
            for (int j=0;j<k;++j) offset[j]=mod(direction*((positions[j]+phase)/n),26);
            for (int a=0;a<4;++a) {
                for (int j=0;j<k;++j) x[j]=(plain_index[a][j]+offset[j])%26;
                for (int b=0;b<4;++b) {
                    for (int j=0;j<k;++j) y[j]=(cipher_index[b][j]+offset[j])%26;
                    append_word(bytes,compatibility(x,y));
                }
            }
        }
        if (bytes.size()!=145728*4) throw std::runtime_error("wrong labeled scan length");
        std::cout.write(bytes.data(),bytes.size());
        std::cout.flush();
    }
    std::string extra;
    if (std::cin>>extra) throw std::runtime_error("extra scan input");
}

int main(int argc,char** argv) {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    try {
        if (argc!=2) throw std::runtime_error("one mode required");
        std::string mode=argv[1];
        if (mode=="--pairs") pair_mode();
        else if (mode=="--settings") setting_mode();
        else if (mode=="--scan") scan_mode();
        else throw std::runtime_error("unknown mode");
        if (!std::cout) throw std::runtime_error("output failure");
        return 0;
    } catch (const std::exception& e) {
        std::cerr<<"R93 INCOMPLETE: "<<e.what()<<"\n";
        return 2;
    }
}
