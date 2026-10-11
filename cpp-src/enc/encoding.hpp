#ifndef REXTR_ENC_ENCODING_HPP
#define REXTR_ENC_ENCODING_HPP

#include "enc/code_point.hpp"

#include <istream>
#include <list>
#include <vector>
#include <memory>

struct Range {
    unsigned int start;
    unsigned int end;
    
    Range& operator=(const Range &r) { this->start=r.start; this->end=r.end; return *this; }
};

class Encoding {
    cp_data_type m_fffd; /* represents invalid character */

    // 8 bits
    Range m_b8;
    std::unique_ptr<std::vector<cp_data_type>> m_b8charset2dst;

    // 16 bits i.e. CJK
    Range m_row; /* number of possible values for the 1st byte */
    Range m_col; /* number of possible values for the 2nd byte */
    std::unique_ptr<std::vector<std::vector<cp_data_type>>> m_charset2dst;
    
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
    Encoding() = default;
    Encoding(const Encoding &enc);
    Encoding(
        cp_data_type fffd, 
        Range range_b8, 
        std::unique_ptr<std::vector<cp_data_type>> b8charset2dst,
        Range range_cjk_row, 
        Range range_cjk_col, 
        std::unique_ptr<std::vector<std::vector<cp_data_type>>> charset2dst
    );
    ~Encoding() = default;

    Encoding& operator=(const Encoding &enc);

    CodePoint conv(CodePoint cp, bool cjk_only=0) const;

    Range getRangeB8() const { return m_b8; };
    Range getRangeCJKRow() const { return m_row; };
    Range getRangeCJKCol() const { return m_col; };

    void add(CodePoint from, CodePoint to); /* add */
};

Encoding newEncoding(std::istream &is);
Encoding newEncoding(const std::string &filename);

#endif