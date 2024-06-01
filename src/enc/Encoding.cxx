#include "src/enc/Encoding.hxx"
#include "src/enc/B8.hxx"

#include <fstream>
#include <string>

Encoding::Encoding(int isRef, cp_basic fffd, 
                   Range b8, const cp_basic *b8charset2dst, 
                   Range row, Range col, 
                   const cp_basic* const* charset2dst) :
    m_isRef(isRef), m_fffd(fffd), m_b8(b8), m_b8charset2dst(b8charset2dst),
    m_row(row), m_col(col), m_charset2dst(charset2dst) {
}

Encoding::~Encoding(){
    if (! ((m_isRef>>0) & 1))
        delete[] m_b8charset2dst; // b8

    if (! ((m_isRef>>1) & 1)) {
        // cjk
        const int rows = m_row.end - m_row.start + 1; 
        for (int r=0; r<rows; r++) 
            delete[] m_charset2dst[r];
            
        delete[] m_charset2dst;
    } 

}

/* = ref */
Encoding&
Encoding::operator=(const Encoding &enc) {
    this->m_isRef = enc.m_isRef;
    this->m_fffd = enc.m_fffd; 
    this->m_b8 = enc.m_b8;
    this->m_b8charset2dst = enc.m_b8charset2dst;
    this->m_row= enc.m_row;
    this->m_col= enc.m_col;
    this->m_charset2dst= enc.m_charset2dst;
    this->m_extras = ExtraConvs(enc.m_extras);

    return *this;
}

/**
 * returns the 1st byte value for a given row 
 */
int
Encoding::rowByte(int row) const {
    int ret = row + m_row.start;
    return ret<=m_row.end? ret : -1;
}; 
    
int
Encoding::colByte(int col) const {
    int ret = col + m_col.start;
    return ret<=m_col.end? ret : -1;
}

/**
 * converts a 1st byte value to a row, else -1 
 */
int
Encoding::byteRow(int byte) const {
    if (m_row.start<=byte && byte <= m_row.end)
        return byte - m_row.start;
    else 
        return -1;
}

int
Encoding::byteCol(int byte) const {
    if (m_col.start<=byte && byte <= m_col.end)
        return byte - m_col.start;
    else 
        return -1;

}

CodePoint
Encoding::conv(CodePoint cp, bool cjk_only) const {
    cp_basic cp_from = cp.val;
    cp_basic cp_to = m_fffd;

    // search Extra Convs
    // priority: Extra Conv > b8 and cjk
    for(auto iter=m_extras.begin(); iter!=m_extras.end(); ++iter) {
        if (iter->first == cp)
            return iter->second; 
    }

    if (!cjk_only && cp.t == CodePoint_t::B8)
        cp_to = m_b8charset2dst[cp_from];
    
    if (cp.t ==  CodePoint_t::CJK) {
        int row = byteRow(cp_from >> 8);
        int col = byteCol(cp_from & 0xff);
        if (row!=-1 && col!=-1)
            cp_to = m_charset2dst[row][col];
    }
    // else if (cp.t == EXT)

    if (cp_to == m_fffd)
        return CodePoint{CodePoint_t::ERR, 0};
    
    CodePoint_t cp_type = cp_to<0x100? CodePoint_t::B8 : CodePoint_t::CJK;
    return CodePoint{cp_type, cp_to};  
}  


/**
 * no duplicate check 
 * add(src, dst)
 */
void
Encoding::add(CodePoint from, CodePoint to) {
    m_extras.push_back(std::make_pair(from, to));
}

/**
 *  return a pointer to cp_basic[0x100]
*/
static cp_basic*
readTable_B8(std::istream &b8, const cp_basic fffd, Range &r) {
    cp_basic *table_b8 = new cp_basic[0x100];
    {
        for(int i=0; i<0x100; i++) {
            table_b8[i] = fffd; 
        }
        char c = b8.get();
        b8.unget();
        if(c != '#') {
            fprintf(stderr, "8 bits table format invalid\n");
            exit(1);
        }
        for (;;) {
            c = b8.get();
            if (c == EOF)
                break;
            if (c == '\n' || c == ' ' || c == '\t')
                continue;
            if (c == '#') {
                do { c = b8.get(); } while (!(c == EOF || c == '\n'));
                continue;
            }
            b8.unget();
            std::string str;
            std::getline(b8, str);
            cp_basic b8char, b8dst;
            if (sscanf(str.c_str(), "0x%x 0x%x", &b8char, &b8dst) != 2 
                || !(b8char >= 0 && b8char < 0x100))
                fprintf(stderr, "0x%x is invalid.\n", b8char);
            table_b8[b8char] = b8dst;
        }
    }

    // cal size 
    unsigned int b8_start = 0x00;
    unsigned int b8_end = 0xff;
    for (int i=0x00; i<0x100; i++) {
        if (table_b8[i] != fffd) {
            b8_start = i;
            break;
        }
    }
    for (int i=0xff; i>=0x00; i--) {
        if (table_b8[i] != fffd) {
            b8_end = i;
            break;
        }
    }

    r = Range{b8_start, b8_end};
    return table_b8;
}

/**
 * 
 */
static cp_basic** 
readTable_CJK(std::istream &cjk, const cp_basic fffd, Range &rrow, Range &rcol) {
    // calculate cjk table size
    unsigned int row_start = 0xff; 
    unsigned int row_end = 0x00;
    unsigned int col_start = 0xff;
    unsigned int col_end = 0x00; 
    {
        int row, col;
        std::istream temp(cjk.rdbuf());
        /* must start with '#' */
        char c = temp.get();
        temp.unget();
        if (c != '#') {
            fprintf(stderr, "cjk table format invalid in cal\n");
            exit(1);
        }
        /* Read a unicode.org style .TXT file. */
        for (;;) {
            c = temp.get();
            if (c == EOF) {
                break;
            }
            if (c == '\n' || c == ' ' || c == '\t')
                continue;
            if (c == '#') {
                do { c =  temp.get(); } while (!(c == EOF || c == '\n'));
                continue;
            }
            temp.unget();
            
            std::string str;
            std::getline(temp, str, ' ');

            int hex_fromcode;
            if (sscanf(str.c_str(), "0x%x", &hex_fromcode) != 1)
                exit(1);
            row = hex_fromcode >> 8;
            col = hex_fromcode & 0xff;
            if ( 0 == row || 0 > col) {
                fprintf(stderr, "0x%x is not a valid value\n", hex_fromcode);
                exit(1);
            } else {
                if (row < row_start) row_start = row;
                if (row > row_end) row_end = row;
                if (col < col_start) col_start = col;
                if (col > col_end) col_end = col;
            }

            /* discard hex values of tocode */
            std::getline(temp, str);
            if (sscanf(str.c_str(), " 0x%x", &hex_fromcode) != 1) {
                fprintf(stderr, "invalid format of table\n");
                exit(1);
            }
        }

        cjk.seekg(0, std::ios_base::beg);
    }
    // cjk 
    const int rows = row_end - row_start + 1; 
    const int cols = col_end - col_start + 1; 
    // 
    cp_basic **table_cjk = new cp_basic*[rows];
    for (int r=0; r<rows; r++) {
        table_cjk[r] = new cp_basic[cols];
        for (int c=0; c<cols; c++)
            table_cjk[r][c] = fffd;
    }
    // read
    {
        char c = cjk.get();
        cjk.unget();
        if (c != '#') {
            fprintf(stderr, "cjk table format invalid\n");
            exit(1);
        }

        for (;;) {
            c = cjk.get();
            if (c == EOF)
                break;
            if (c == '\n' || c == ' ' || c == '\t')
                continue;
            if (c == '#') {
                do {c = cjk.get();} while (!(c == EOF || c == '\n'));
                continue;
            }
            cjk.unget();
            std::string str;
            std::getline(cjk, str, ' ');
            int hex_fromcode;
            if (sscanf(str.c_str(), "0x%x", &hex_fromcode) != 1)
                exit(1);

            int row = (hex_fromcode >> 8) - row_start;
            int col = (hex_fromcode & 0xff) - col_start;

            if (row < 0 || col < 0) {
                fprintf(stderr, "lost entry for %02x %02x\n", row, col);
                exit(1);
            }

            std::getline(cjk, str);
            if (sscanf(str.c_str(), " 0x%x", &table_cjk[row][col]) != 1) {
                exit(1);
            }  
        }
    }

    rrow = Range{row_start, row_end};
    rcol = Range{col_start, col_end};
    return table_cjk;
}

/**
 * still ugly
 */
Encoding*
newEncoding(std::istream &b8, std::istream &cjk) {
    constexpr cp_basic fffd = 0xfffd;
    
    // b8
    Range rb8{0x00,0xff};
    cp_basic *table_b8 = readTable_B8(b8, fffd, rb8);
 
    Range rrow{0x00,0xff};
    Range rcol{0x00,0xff};

    auto table_cjk = readTable_CJK(cjk, fffd, rrow, rcol);

    // 3 = 0b11
    return new Encoding(3, fffd, rb8, table_b8, rrow, rcol, table_cjk);
}

Encoding*
newEncoding(const char *b8, const char *cjk) {
    std::fstream b8f{b8, std::fstream::in};
    if (!b8f.is_open())
        fprintf(stderr, "failed to open %s.\n", b8);

    std::fstream cjkf{cjk, std::fstream::in};
    if (!cjkf.is_open())
        fprintf(stderr, "failed to open %s.\n", cjk);

    Encoding* enc = newEncoding(b8f, cjkf);
    b8f.close();
    cjkf.close();

    return enc;
}


Encoding*
newEncoding_cjk(const char *cjk) {
    std::fstream cjkf{cjk, std::fstream::in};
    constexpr cp_basic fffd = 0xfffd;
    if (!cjkf.is_open())
        fprintf(stderr, "failed to open %s.\n", cjk);
    
    Range row{0x00,0xff};
    Range col{0x00,0xff};
    auto cjk_table = readTable_CJK(cjkf, fffd, row, col);

    return new Encoding(2, fffd, Range{0x20, 0x7d}, general_8bit, row, col, cjk_table);
}

