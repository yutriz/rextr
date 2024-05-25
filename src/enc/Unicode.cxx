#include "src/enc/Unicode.hxx"
#include "src/utils/Unicode.hxx"

std::string utf8Character(const CodePoint &cp) {
    return utf8Character_basic(cp.val);
}

CodePoint utf8CodePoint(const std::string &u) {
    cp_basic val = utf8CodePoint_basic(u);
    
    if (val == 0xfffff)
        return CodePoint{CodePoint_t::ERR, 0};

    if (val < 0x100) 
        return CodePoint{CodePoint_t::B8, val};
    
    if (val < 0x10000) 
        return CodePoint{CodePoint_t::CJK, val};
    
    return CodePoint{CodePoint_t::EXT, val};
}
