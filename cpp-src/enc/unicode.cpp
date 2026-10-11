#include "enc/unicode.hpp"
#include "utils/unicode_utils.hpp"

std::string UTF8Character(const CodePoint &cp) {
    return intToUTF8Character(cp.val);
}

CodePoint UTF8CodePoint(const std::string &u) {
    cp_data_type val = UTF8CodePointToInt(u);
    
    if (val == 0xfffff)
        return CodePoint{CodePointType::ERR, 0};

    if (val < 0x100) 
        return CodePoint{CodePointType::B8, val};
    
    if (val < 0x10000) 
        return CodePoint{CodePointType::CJK, val};
    
    return CodePoint{CodePointType::EXT, val};
}
