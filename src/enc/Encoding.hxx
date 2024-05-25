#ifndef REXTR_ENC_ENCODING_HXX
#define REXTR_ENC_ENCODING_HXX

#include "src/enc/CodePoint.hxx"

#include <istream>
#include <list>

struct Range {
    unsigned int start;
    unsigned int end;
};

class Encoding {
    bool m_isRef; /* whether to delete tables */
    cp_basic m_fffd; /* represents invalid character */

    // 8 bits
    Range m_b8;
    const cp_basic* m_b8charset2dst;

    // 16 bits i.e. CJK
    Range m_row; /* number of possible values for the 1st byte */
    Range m_col; /* number of possible values for the 2nd byte */
    const cp_basic* const* m_charset2dst;
    
    // extra conversions 
    using ExtraConvs = std::list<std::pair<CodePoint, CodePoint>>;
    ExtraConvs m_extras = {};

    /**
     * further:
     *    1. libiconv-like conversion func (bi-directed, mbtowc, wctomb.)
     *    2. reduce table size (sparse table?)
     */ 

private:
    int rowByte(int row) const; /* returns the 1st byte value for a given row */
    int colByte(int col) const;
    int byteRow(int byte) const;  /* converts a 1st byte value to a row, else -1 */
    int byteCol(int byte) const;

public: 
    Encoding(bool, cp_basic, Range, const cp_basic*, Range, Range, const cp_basic* const*);
    ~Encoding();

    Encoding& operator=(const Encoding &enc);

    CodePoint conv(CodePoint cp, bool cjk_only=0) const;

    Range getRangeB8() const { return m_b8; };
    Range getRangeCjkRow() const { return m_row; };
    Range getRangeCjkCol() const { return m_col; };

    void add(CodePoint from, CodePoint to); /* add */
};

Encoding* newEncoding(std::istream &b8, std::istream &cjk);
Encoding* newEncoding(const char *b8, const char *cjk);


#endif