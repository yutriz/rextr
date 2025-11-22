#ifndef REXTR_STRUCTURE_BLOCK_HPP
#define REXTR_STRUCTURE_BLOCK_HPP

#include "enc/code_point.hpp"
#include "enc/unicode.hpp"

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
    
enum class PointerType {
    STANDARD,
    OFFSET,
    RELATIVE,
    UNKNOWN
};

inline PointerType safeConverter(int type_id) {
    switch(static_cast<PointerType>(type_id)) {
    case PointerType::STANDARD:
        return PointerType::STANDARD;
    case PointerType::OFFSET:
        return PointerType::OFFSET;
    case PointerType::RELATIVE:
        return PointerType::RELATIVE;
    default:
        return PointerType::UNKNOWN;
    }
}


struct Block {
    int         m_num = 0; // idx 
    PointerType m_pointer_type;
    size_t      m_offset;
    size_t      m_len; /* block length */

    using CodePointList = std::list<CodePoint>;

    std::unique_ptr<CodePointList>  m_orig_hex; /* if translated, this will be replaced when repacking */
    bool                            m_recog; // is recognized(must be recongnized or not 
    bool                            m_tl; // is translated(must be recongnized or not 
    std::string                     m_recognized_text; // text converted by encoding
    std::unique_ptr<CodePointList>  m_uni_hex; // unicode code points converted by encoding

    explicit Block(
        PointerType pointer_type,
        size_t offset, 
        size_t len, 
        std::unique_ptr<CodePointList> orig_hex, 
        bool recog,
        std::string recogn_text,
        std::unique_ptr<CodePointList> uni_hex,
        bool tl
    )
        : m_pointer_type(pointer_type)
        , m_offset(offset)
        , m_len(len)
        , m_orig_hex(std::move(orig_hex))
        , m_recog(recog)
        , m_recognized_text(recogn_text)
        , m_uni_hex(std::move(uni_hex))
        , m_tl(tl)
    { }
    
    explicit Block(
        int num,
        PointerType pointer_type,
        size_t offset, 
        size_t len, 
        std::unique_ptr<CodePointList> orig_hex, 
        bool recog,
        std::string recogn_text,
        std::unique_ptr<CodePointList> uni_hex,
        bool tl
    )
        : m_num(num)
        , m_pointer_type(pointer_type)
        , m_offset(offset)
        , m_len(len)
        , m_orig_hex(std::move(orig_hex))
        , m_recog(recog)
        , m_recognized_text(recogn_text)
        , m_uni_hex(std::move(uni_hex))
        , m_tl(tl)
    { }

    void setNum(int num) {m_num = num;}

    /** 
     * 0x30 -> 0
     * 0x3042 -> あ
     */
    static std::string UnicodeCodePointToText(const std::list<CodePoint> &unicode_codepints){
        std::string ret("");
        for(auto iter=unicode_codepints.begin(); iter!=unicode_codepints.end(); ++iter) {
            ret += UTF8Character(*iter);
        }
        return ret;
    }
};

struct RepackBlock : public Block {
    std::string m_recognized_text;
    std::string m_recognized_text_zh;
   
    explicit RepackBlock(
        int num, 
        PointerType pointer_type,
        size_t offset,
        size_t len,
        std::string orig_hex, // ignored 
        bool recog,
        std::string recogn_text,
        bool tl,
        std::string translated_text, 
        std::string translated_text_en
    )
        : Block(
            num, 
            pointer_type, 
            offset, 
            len, 
            _empty_code_point_list(), 
            recog, 
            recogn_text,
            _empty_code_point_list(), tl)
        , m_recognized_text(translated_text)
        , m_recognized_text_zh(translated_text_en) 
    { }

private: 
    static std::unique_ptr<CodePointList> _empty_code_point_list() {
        std::unique_ptr<CodePointList> cpl = std::make_unique<CodePointList>();

        return cpl;
    }
};

const std::string SPEC_KEYNAME_BLOCK_NUM              = "num";
const std::string SPEC_KEYNAME_POINTER_TYPE           = "pointer_type";
const std::string SPEC_KEYNAME_OFFSET                 = "offset";
const std::string SPEC_KEYNAME_LEN                    = "len";
const std::string SPEC_KEYNAME_ORIGNAL_HEX            = "orig_hex";
const std::string SPEC_KEYNAME_IS_RECOGNIZED          = "recognized";
const std::string SPEC_KEYNAME_IS_TRANSLATED          = "translated";
const std::string SPEC_KEYNAME_RECOGNIZED_TEXT        = "recogn_text";
const std::string SPEC_KEYNAME_RECOGNIZED_UNICODE_HEX = "recogn_text_unicode_hex";
const std::string SPEC_KEYNAME_TRANSLATED_TEXT        = "translated_text";
const std::string SPEC_KEYNAME_TRANSLATED_TEXT_EN     = "translated_text_en";
const std::string SPEC_KEYNAME_LABEL                  = "label";
const std::string SPEC_KEYNAME_NOTE                   = "note";

#endif