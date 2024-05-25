#ifndef REXTR_ENC_CODEPOINT_HXX
#define REXTR_ENC_CODEPOINT_HXX

#include <cstdint>

enum class CodePoint_t {
    ERR = 0,    /* Error */
    B8,         /* 8 bits */
    CJK,        /* 2 Bytes CJK, 16 bits*/
    EXT,        /* >2 */
};

using cp_basic = uint_least32_t;

struct CodePoint {
    CodePoint_t t;
    cp_basic val;

    CodePoint() : t(CodePoint_t::ERR), val(0) {}
    CodePoint(CodePoint_t t_, cp_basic val_) : t(t_), val(val_) {}

    CodePoint& operator=(const CodePoint &cp) { this->t=cp.t; this->val=cp.val; return *this; }
    bool operator==(const CodePoint &cp) const { return this->t==cp.t && this->val==cp.val;}
};


#endif