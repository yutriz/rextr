#ifndef REXT_REPACK_BLOCKR_HXX
#define REXT_REPACK_BLOCKR_HXX

#include <string>

struct BlockR_full {
    int    m_num;
    size_t m_offset;
    size_t m_len; 

    std::string m_orig_hex;
    bool        m_Tl;

    std::string m_translated_text;
    std::string m_translated_text_zh;
   
    explicit 
    BlockR_full(int num, size_t offset, size_t len,
                std::string orig_hex, bool tl,
                std::string translated_text, 
                std::string translated_text_zh):
        m_num(num), m_offset(offset), m_len(len),
        m_orig_hex(orig_hex), m_Tl(tl),
        m_translated_text(translated_text),
        m_translated_text_zh(translated_text_zh) {}
};

/* 
 * Three principle types
 *  1. Standard. Start counting from the start of the file. Sometimes 
 *  known as linear pointers although the term does technically encompass 
 *  the second type.
 *  2. Offset. Start counting from some point in the file (quite often the 
 *  start of the proper data/end of the header).
 *  3. Relative. Start counting from where the actual pointer is at (if the 
 *  pointer reads 30h and is located at 20h the data in question is likely 
 *  at 50h). 
 */

/**
 *  Type 1: Standard
 */

/**
 *  Type 2: offset 
 * 
 *  "offset":             string,
 *  "translated":         bool,
 *  "orig_text":          string,
 *  "translated_text":    string(""),
 *  "translated_text_zh": string(""),
 *  "note",               string("")
 */
struct BlockR_offset {
    size_t m_offset;
    size_t m_len;
    bool   m_Tl;

    std::string m_translated_text;
    std::string m_translated_text_zh;

    explicit
    BlockR_offset(size_t offset, size_t len, bool tl, 
                  std::string translated_text,
                  std::string translated_text_zh):
        m_offset(offset), m_len(len), m_Tl(tl),
        m_translated_text(translated_text),
        m_translated_text_zh(translated_text_zh) {}
};

/**
 *  Type 3: Relative
 */

#endif