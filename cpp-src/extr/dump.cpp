#include "extr/dump.hpp"

#include "enc/unicode.hpp"
#include "extr/extract.hpp"
#include "utils/hex_utils.hpp"
#include "utils/exceptions.hpp"

#include <exception>

/**
 * 0x1234 to "1234"
 */
static inline std::string toString(const CodePoint &cp) {
    int l;
    if (cp.t == CodePointType::B8)
        l = 2;
    else if (cp.t == CodePointType::CJK)
        l = 4;
    // else if (cp.t == CodePointType::EXT)
    return hex2Str(cp.val, l); 
}

static std::string toString(const std::list<CodePoint> &lcp){
    std::string ret("");
    for(auto iter=lcp.begin(); iter!=lcp.end(); ++iter)
        ret += toString(*iter);
    return ret;
}

Json dumpBlock(const Block &blk) {
    switch (blk.m_pointer_type) {
    case PointerType::OFFSET:
        return Json{
            {SPEC_KEYNAME_BLOCK_NUM, blk.m_num},
            {SPEC_KEYNAME_POINTER_TYPE, static_cast<int>(blk.m_pointer_type)},
            {SPEC_KEYNAME_OFFSET, hexLong2Str(blk.m_offset)},
            {SPEC_KEYNAME_LEN, blk.m_len},
            {SPEC_KEYNAME_ORIGNAL_HEX, toString(*blk.m_orig_hex)},
            {SPEC_KEYNAME_IS_RECOGNIZED, blk.m_recog}, 
            {SPEC_KEYNAME_RECOGNIZED_TEXT, Block::UnicodeCodePointToText(*blk.m_uni_hex)},
            {SPEC_KEYNAME_RECOGNIZED_UNICODE_HEX, toString(*blk.m_uni_hex)},
            {SPEC_KEYNAME_IS_TRANSLATED, blk.m_tl}, 
            {SPEC_KEYNAME_TRANSLATED_TEXT, std::string("")},
            {SPEC_KEYNAME_TRANSLATED_TEXT_EN, std::string("")},
            {SPEC_KEYNAME_LABEL, std::string("")},
            {SPEC_KEYNAME_NOTE, std::string("")},
        };
    case PointerType::STANDARD:
        throw NotImplemented();
    case PointerType::RELATIVE:
        throw NotImplemented();
    case PointerType::UNKNOWN:
        throw NotImplemented();
    }

    return Json(); // shall not reach here
}

Json dumpScene(const Scene &scn) {
    Json j;
    j[SPEC_KEYNAME_MD5SUM] = scn.m_md5;
    auto textblock = scn.m_textblocks.get();
    for(auto iter=textblock->begin(); iter!=textblock->end(); ++iter) {
        if (iter->m_recog)
            j[SPEC_KEYNAME_BLOCKS].push_back(dumpBlock(*iter));
    }

    return j;
}