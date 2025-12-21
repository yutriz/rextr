#include "special/validate.hpp"
#include "utils/hash_utils.hpp"
#include "utils/unicode_utils.hpp"
#include "utils/string_utils.hpp"
#include "utils/exceptions.hpp"

#include <cassert>
#include <fstream>
#include <iostream>

int Validator::validateScene(const std::string &game, RepackScene &rscn, const std::string &filename) {
    assert(rscn.m_md5 == MD5sum(filename));

    if (game == SN1_GAME_NAME)
        return Validator::_validateScene_NDS_SN1(rscn, filename);
    else
        throw NotImplemented();
}   

int Validator::_validateScene_NDS_SN1(RepackScene &rscn, const std::string &filename) {
    std::ifstream ifs(filename);
    ifs.seekg(0, std::ios::beg);

    auto blks = rscn.m_textblocks.get(); // unique ptr cant be referenred
    for (auto iter=blks->begin(); iter!=blks->end(); ++iter) {
        if(iter->m_tl == false) 
            continue;
        
        if (countBytes(iter->m_recognized_text) != iter->m_recognized_text.length())
            fprintf(stdout, "at offset %lxh, regconized_text contains fullwidth character.\n", iter->m_offset);

        ifs.seekg(iter->m_offset - 2, std::ios::beg);
        auto c1 = static_cast<unsigned char>(ifs.get()); // c1 (can be anything)
        auto c2 = static_cast<unsigned char>(ifs.get()); // count
        if(c1 != 0xc1) // 0xc1 + length
            fprintf(stderr, "at offset %lxh, char should be c1 instead of %02xh.\n", iter->m_offset-2, c1);
        if(c2 != iter->m_len)
            fprintf(stderr, "at offset %lxh, char should be %02lxh instead of %02xh.\n", iter->m_offset-1, iter->m_len, c2);
    }
    
    return 0;
}