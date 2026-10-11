#ifndef REXTR_ENC_CODEPOINT_HPP
#define REXTR_ENC_CODEPOINT_HPP

#include <cstdint>

enum class CodePointType {
    ERR = 0,    /* Error */
    B8,         /* 8 bits */
    CJK,        /* 2 Bytes CJK, 16 bits*/
    EXT,        /* >2 */
};

using cp_data_type = uint_least32_t; // codepoint data type

struct CodePoint {
    CodePointType t;
    cp_data_type val;

    CodePoint() : t(CodePointType::ERR), val(0) {}
    CodePoint(cp_data_type val_) : val(val_) { 
        if (val < 0xff)
            t = CodePointType::B8;
        else if (val < 0xffff)
            t = CodePointType::CJK;
        else 
            t = CodePointType::EXT;        
    }
    CodePoint(CodePointType t_, cp_data_type val_) : t(t_), val(val_) {}

    CodePoint& operator=(const CodePoint &cp) { this->t=cp.t; this->val=cp.val; return *this; }
    bool operator==(const CodePoint &cp) const { return this->t==cp.t && this->val==cp.val;}
};


#endif