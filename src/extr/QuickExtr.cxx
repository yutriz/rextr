#include "extr/Block.hxx"
#include "extr/Extract.hxx"
#include "extr/QuickExtr.hxx"
#include "extr/Read.hxx"
#include "utils/Hash.hxx"

#include <iostream>

// offset 
void quickExtrJson(const char *fn, std::ostream &os, const Encoding &enc) {
    Json q; 

    q["md5"] = MD5sum(fn);
    std::ifstream fp(fn, std::ios::binary | std::ios_base::in);
    assert(fp.good());
    
    while(fp) {
        auto nblk = newBlock(fp, enc, 1);

        //  
        if(nblk.m_len == 11 && nblk.m_orig_hex->begin()->val == 0x0a) {
            nblk.m_uni_hex->erase(nblk.m_uni_hex->begin());
            nblk.m_offset += 1;
            nblk.m_len -= 1;
        }

        if(nblk.m_Tl)
            q["blocks"].push_back(Block2Json_offset(nblk));

    }
    fp.close();
    writeJson(q, os);
}


void quickExtrJson_SN1ps1(const char *fn, std::ostream &os, const Encoding &enc) {
    Json q; 

    q["md5"] = MD5sum(fn);
    std::ifstream fp(fn, std::ios::binary | std::ios_base::in);
    assert(fp.good());
    
    while(fp) {
        auto nblk = newBlock(fp, enc, 1);
        if(nblk.m_Tl)
            q["blocks"].push_back(Block2Json_offset(nblk));
    }
    fp.close();
    writeJson(q, os);
}

