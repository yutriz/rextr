#include "enc/Unicode.hxx"
#include "extr/Extract.hxx"
#include "extr/Read.hxx"
#include "utils/Hex.hxx"

/**
 * 0x1234 to "1234"
 */
static inline std::string
toString(const CodePoint &cp) {
    int l;
    if (cp.t == CodePoint_t::B8)
        l = 2;
    else if (cp.t == CodePoint_t::CJK)
        l = 4;
    // else if (cp.t == CodePoint_t::EXT)
    return hex2str(cp.val, l); 
}

static std::string 
toString(const std::list<CodePoint> &lcp){
    std::string ret("");
    for(auto iter=lcp.begin(); iter!=lcp.end(); ++iter)
        ret += toString(*iter);
    return ret;
}

/** 
 * 0x30 -> 0
 * 0x3042 -> あ
 */
static std::string 
toText(const std::list<CodePoint> &lcp){
    std::string ret("");
    for(auto iter=lcp.begin(); iter!=lcp.end(); ++iter) {
        ret += utf8Character(*iter);
    }
    return ret;
}

/* full */
Json 
Block2Json_full(const BasicBlock &blk) {
    return Json{
        {"num", blk.m_num},
        {"offset", hex2String_long(blk.m_offset)},
        {"len", blk.m_len},
        {"orig_hex", toString(*blk.m_orig_hex)},
        {"translated", blk.m_Tl}, 
        {"orig_text", toText(*blk.m_uni_hex)},
        {"uni_hex", toString(*blk.m_uni_hex)},
        {"translated_text", std::string("")},
        {"note", std::string("")}
    };
}

/**
 *  Simple
 * 
 *  "offset":           string,
 *  "translated":       bool,
 *  "orig_text":        string,
 *  "translated_text":  string(""),
 */
Json 
Block2Json_simple(const BasicBlock &blk) {
    return Json{
        {"offset", hex2String_long(blk.m_offset)},
        {"translated", blk.m_Tl}, 
        {"orig_text", toText(*blk.m_uni_hex)},
        {"translated_text", std::string("")},
        {"translated_text_zh", std::string("")},
    };
}

/**
 *  Type 1: standard
 */


/**
 *  Type 2: offset 
 * 
 *  "offset":              string,
 *  "translated":          bool,
 *  "orig_text":           string,
 *  "translated_text":     string(""),
 *  "translated_text_zh":  string(""),
 *  "note",                string("")
 */
Json 
Block2Json_offset(const BasicBlock &blk) {
    return Json{
        {"offset", hex2String_long(blk.m_offset)},
        {"translated", blk.m_Tl}, 
        {"len", blk.m_len}, 
        {"orig_text", toText(*blk.m_uni_hex)},
        {"translated_text", std::string("")},
        {"translated_text_zh", std::string("")},
        {"note", std::string("")}
    };
}

/**
 *  Type 3:relative
 */

/**
 * 
 */
Json 
Scene2Json_full(const Scene &scn) {
    Json j;
    j["md5"] = scn.m_md5;
    auto textblock = scn.m_textblocks.get();
    for(auto iter=textblock->begin(); iter!=textblock->end(); ++iter)
        j["blocks"].push_back(Block2Json_full(*iter));
    return j;
}

Json 
Scene2Json_simple(const Scene &scn) {
    Json j;
    j["md5"] = scn.m_md5;
    auto textblock = scn.m_textblocks.get();
    for(auto iter=textblock->begin(); iter!=textblock->end(); ++iter) {
        if (iter->m_Tl == true)
            j["blocks"].push_back(Block2Json_simple(*iter));
    }
    return j;
}

Json 
Scene2Json_offset(const Scene &scn) {
    Json j;
    j["md5"] = scn.m_md5;
    auto textblock = scn.m_textblocks.get();
    for(auto iter=textblock->begin(); iter!=textblock->end(); ++iter) {
        if (iter->m_Tl == true)
            j["blocks"].push_back(Block2Json_offset(*iter));
    }
    return j;
}

size_t 
writeJson(const Json &j, std::ostream &os) {
    std::string s = j.dump(2);
    os << s << std::endl;
    return s.size();
}

size_t 
writeJson(const Json &j, const char *f) {
    std::ofstream fs(f);
    auto ret = writeJson(j, fs);
    fs.close();
    return ret;
}


