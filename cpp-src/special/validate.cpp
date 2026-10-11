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
        
        // e.g. recog text starts with 0x0a, in the json looks like:
        //     {len: 11, recog_text: "\n{a 10 bytes}", ...}
        // but can be sure the starting 0a indicates '\n' or the length of 10
        // so needed to check byte before 0x0a, 
        // if it is 0xc1, the 0xc10a tells the leading is '\n' is a miss recog
        // the correct one should be: 
        //     len: 10, recog_text: "{a 10 bytes}", ...}

        if (countBytes(iter->m_recognized_text) != iter->m_len)
            fprintf(stdout, 
                "[WARN]In block with offset 0x%lx, "
                "length of \"regconized_text\" and \"len\" do not match.\n", 
                iter->m_offset);

        ifs.seekg(iter->m_offset - 2, std::ios::beg);
        auto c1 = static_cast<unsigned char>(ifs.get()); // c1 (can be anything)
        auto c2 = static_cast<unsigned char>(ifs.get()); // count

        if (c1 == 0xc1 && c2 == iter->m_len) 
            continue;
        
        // 0a problem
        ifs.seekg(iter->m_offset - 1, std::ios::beg);
        auto c1_ = static_cast<unsigned char>(ifs.get()); // c1 (can be anything)
        auto c2_ = static_cast<unsigned char>(ifs.get()); // count

        if (c1_ == 0xc1 && c2_ == iter->m_len) {
            fprintf(stdout, 
                "[WARN]In block with 0x%lx, \"offset\" should be 0x%lx. "
                "This might be caused by a leading \"0x0a\", "
                "and will be fixed in the process of repacking.\n",
                iter->m_offset, iter->m_offset-1
            );
            iter->m_offset = iter->m_offset + 1;
        } else {
            fprintf(stdout,
                "[WARN]In block with 0x%lx, the 2 bytes before should be "
                "0xc1%02x instead of 0x%02x%02x. Maybe they are edited by "
                "accident?\n", 
                iter->m_offset, iter->m_len, c1, c2
            );
        }
    }
    
    return 0;
}