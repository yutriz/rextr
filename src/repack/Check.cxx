#include "src/repack/Check.hxx"
#include "src/utils/Hash.hxx"

#include <cassert>
#include <fstream>
#include <iostream>


// write different check funcs for different games 
// SN1 
int checkSceneR_offset(SceneR_offset &scnro, const char *rawfile) {
    assert(scnro.m_hash == MD5sum(rawfile));

    std::ifstream rfp(rawfile);
    rfp.seekg(0, std::ios::beg);

    auto blks = scnro.m_blks.get();
    for (auto iter=blks->begin(); iter!=blks->end(); ++iter) {
        if(iter->m_Tl == false) 
            continue;
        
        rfp.seekg(iter->m_offset - 2, std::ios::beg);
        auto c1 = static_cast<unsigned char>(rfp.get()); // c1 (can be anything)
        char c2 = static_cast<unsigned char>(rfp.get()); // count
        if(c1 != 0xc1)
            fprintf(stderr, "at offset %lxh, char should be c1 instead of %02xh.\n", iter->m_offset-2, c1);
        if(c2 != iter->m_len)
            fprintf(stderr, "at offset %lxh, char should be %02lxh instead of %02xh.\n", iter->m_offset-1, iter->m_len, c2);
        
    }
    return 0;
}
