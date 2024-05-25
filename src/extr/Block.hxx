#ifndef REXTR_EXTR_BLOCK_HXX
#define REXTR_EXTR_BLOCK_HXX

#include "src/enc/CodePoint.hxx"

#include <string>
#include <list>
#include <memory> 

/**
 * 1. Standard. Start counting from the start of the file. Sometimes known as
 *    linear pointers although the term does technically encompass the second type.
 * 2. Offset. Start counting from some point in the file (quite often the start of
 *    the proper data/end of the header).
 * 3. Relative. Start counting from where the actual pointer is at (if the pointer
 *    reads 30h and is located at 20h the data in question is likely at 50h).
 * 
 *  - GBA and DS ROM hacking guide - 2016 edition.  FAST6191
 */
    
struct BasicBlock {
    int    m_num = 0;
    size_t m_offset;
    size_t m_len; /* block length */

    using CodePointList = std::list<CodePoint>;
    std::unique_ptr<CodePointList> m_orig_hex; /* if translated, this will be replaced when repacking */
    bool        m_Tl;
    std::unique_ptr<CodePointList> m_uni_hex;
    std::string m_translated_text;

    explicit BasicBlock(size_t offset, size_t len, 
                        std::unique_ptr<CodePointList> &orig_hex, bool Tl,
                        std::unique_ptr<CodePointList> &uni_hex, std::string translated_text):
        m_offset(offset), m_len(len),
        m_orig_hex(std::move(orig_hex)), m_Tl(Tl),
        m_uni_hex(std::move(uni_hex)), m_translated_text(translated_text) {}
    
    explicit BasicBlock(int num, size_t offset, size_t len, 
                        std::unique_ptr<CodePointList> &orig_hex, bool Tl,
                        std::unique_ptr<CodePointList> &uni_hex, std::string translated_text):
        m_num(num), m_offset(offset), m_len(len),
        m_orig_hex(std::move(orig_hex)), m_Tl(Tl),
        m_uni_hex(std::move(uni_hex)), m_translated_text(translated_text) {}

    void setNum(int num) {m_num = num;}
};



#endif
