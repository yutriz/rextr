#include "enc/encoding.hpp"
#include "utils/exceptions.hpp"

#include <fstream>
#include <string>
#include <tuple>
#include <vector>
#include <memory>

Encoding::Encoding(
    cp_data_type fffd, 
    Range range_b8, 
    std::unique_ptr<std::vector<cp_data_type>> b8charset2dst,
    Range range_cjk_row, 
    Range range_cjk_col, 
    std::unique_ptr<std::vector<std::vector<cp_data_type>>> charset2dst
)
    : m_fffd(fffd)
    , m_b8(range_b8), m_b8charset2dst(std::move(b8charset2dst))
    , m_row(range_cjk_row), m_col(range_cjk_col)
    , m_charset2dst(std::move(charset2dst)) 
{ }

Encoding::Encoding(const Encoding &enc) {
    this->m_fffd = enc.m_fffd; 
    this->m_b8 = enc.m_b8;
    this->m_b8charset2dst = \
        std::make_unique<std::vector<cp_data_type>>(*(enc.m_b8charset2dst));
    this->m_row= enc.m_row;
    this->m_col= enc.m_col;
    this->m_charset2dst = \
        std::make_unique<std::vector<std::vector<cp_data_type>>>(*(enc.m_charset2dst));
    this->m_extras = ExtraConvs(enc.m_extras);
}

Encoding& Encoding::operator=(const Encoding &enc) {
    this->m_fffd = enc.m_fffd; 
    this->m_b8 = enc.m_b8;
    this->m_b8charset2dst = \
        std::make_unique<std::vector<cp_data_type>>(*(enc.m_b8charset2dst));
    this->m_row= enc.m_row;
    this->m_col= enc.m_col;
    this->m_charset2dst = \
        std::make_unique<std::vector<std::vector<cp_data_type>>>(*(enc.m_charset2dst));
    this->m_extras = ExtraConvs(enc.m_extras);

    return *this;
}

/**
 * returns the 1st byte value for a given row 
 */
int Encoding::rowByte(int row) const {
    int ret = row + m_row.start;
    return ret<=m_row.end? ret : -1;
}; 
    
int Encoding::colByte(int col) const {
    int ret = col + m_col.start;
    return ret<=m_col.end? ret : -1;
}

/**
 * converts a 1st byte value to a row, else -1 
 */
int Encoding::byteRow(int byte) const {
    if (m_row.start<=byte && byte <= m_row.end)
        return byte - m_row.start;
    else
        return -1;
}

int Encoding::byteCol(int byte) const {
    if (m_col.start<=byte && byte <= m_col.end)
        return byte - m_col.start;
    else 
        return -1;

}

CodePoint Encoding::conv(CodePoint cp, bool cjk_only) const {
    cp_data_type cp_from = cp.val;
    cp_data_type cp_to = m_fffd;

    // search Extra Convs
    // priority: Extra Conv > b8 and cjk
    for(auto iter=m_extras.begin(); iter!=m_extras.end(); ++iter) {
        if (iter->first == cp) {
            return iter->second; 
        }
    }

    if (!cjk_only && cp.t == CodePointType::B8)
        cp_to = (*m_b8charset2dst)[cp_from];
    
    if (cp.t == CodePointType::CJK) {
        int row = byteRow(cp_from >> 8);
        int col = byteCol(cp_from & 0xff);
        if (row!=-1 && col!=-1)
            cp_to = (*m_charset2dst)[row][col];
    }
    // else if (cp.t == EXT)

    if (cp_to == m_fffd)
        return CodePoint{CodePointType::ERR, 0};
    
    CodePointType cp_type = cp_to<0x100? CodePointType::B8 : CodePointType::CJK;

    return CodePoint{cp_type, cp_to};  
}  


/**
 * no duplicate check 
 * add(src, dst)
 */
void Encoding::add(CodePoint from, CodePoint to) {
    m_extras.push_back(std::make_pair(from, to));
}


static std::tuple<std::unique_ptr<std::vector<cp_data_type>>, std::unique_ptr<std::vector<std::vector<cp_data_type>>>, Range, Range, Range> 
readConversionTable(std::istream &is, const cp_data_type fffd) {
    // b8 range
    unsigned int b8_start = 0x00;
    unsigned int b8_end = 0xff;
    std::unique_ptr<std::vector<cp_data_type>> b8_conversion_table = std::make_unique<std::vector<cp_data_type>>(0x100, fffd);

    // calculate cjk table size
    unsigned int cjk_row_start = 0xff; 
    unsigned int cjk_row_end = 0x00;
    unsigned int cjk_col_start = 0xff;
    unsigned int cjk_col_end = 0x00; 

    // calculate in advance to 
    {
        int row, col;
        std::istream temp(is.rdbuf());
        /* must start with '#' */
        char c = temp.get();
        temp.unget();
        if (c != '#') {
            fprintf(stderr, "Table format invalid, a unicode.org style .TXT file is expected, file should start with '#'\n");
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
            if (sscanf(str.c_str(), "0x%x", &hex_fromcode) != 1) {
                fprintf(stderr, "failed to parse %s\n", str.c_str());
                exit(1);
            }

            // discard codepoints less than 0xff
            if (hex_fromcode < 0xff)
                continue;

            row = hex_fromcode >> 8;
            col = hex_fromcode & 0xff;
            if (0 == row || 0 > col) {
                fprintf(stderr, "0x%x is not a valid value\n", hex_fromcode);
                exit(1);
            } else {
                if (row < cjk_row_start) cjk_row_start = row;
                if (row > cjk_row_end)   cjk_row_end = row;
                if (col < cjk_col_start) cjk_col_start = col;
                if (col > cjk_col_end)   cjk_col_end = col;
            }

            /* discard hex values of tocode */
            std::getline(temp, str);
            if (sscanf(str.c_str(), " 0x%x", &hex_fromcode) != 1) {
                fprintf(stderr, "invalid format of table\n");
                exit(1);
            }
        }

        is.seekg(0, std::ios_base::beg);
    }

    const int cjk_rows = cjk_row_end - cjk_row_start + 1; 
    const int cjk_cols = cjk_col_end - cjk_col_start + 1; 

    std::unique_ptr<std::vector<std::vector<cp_data_type>>> cjk_conversion_table = \
        std::make_unique<std::vector<std::vector<cp_data_type>>>(cjk_rows, std::vector<cp_data_type>(cjk_cols, fffd));

    // read
    {
        char c = is.get();
        is.unget();
        if (c != '#') {
            fprintf(stderr, "cjk table format invalid\n");
            exit(1);
        }

        for (;;) {
            c = is.get();
            if (c == EOF)
                break;
            if (c == '\n' || c == ' ' || c == '\t')
                continue;
            if (c == '#') {
                do {c = is.get();} while (!(c == EOF || c == '\n'));
                continue;
            }
            is.unget();
            std::string str;
            std::getline(is, str, ' ');
            int hex_from;
            if (sscanf(str.c_str(), "0x%x", &hex_from) != 1) {
                fprintf(stderr, "failed to parse %s\n", str.c_str());
                exit(1);
            }

            std::getline(is, str);
            int hex_to;
            if (sscanf(str.c_str(), " 0x%x", &hex_to) != 1) {
                fprintf(stderr, "failed to parse %s\n", str.c_str());
                exit(1);
            }  

            if (hex_from < 0xff) {
                (*b8_conversion_table)[hex_from] = static_cast<cp_data_type>(hex_to);
            } else if (hex_from < 0xffff) {
                int row = (hex_from >> 8) - cjk_row_start;
                int col = (hex_from & 0xff) - cjk_col_start;

                if (row < 0 || col < 0) {
                    fprintf(stderr, "lost entry for %02x %02x\n", row, col);
                    exit(1);
                }

                (*cjk_conversion_table)[row][col] = static_cast<cp_data_type>(hex_to);
            } else {
                fprintf(stderr, "0x%x seems too big to be parsed.\n", hex_from);
                exit(1);
            }
        }
    }

    for (int i=0x00; i<0x100; i++) {
        if ((*b8_conversion_table)[i] != fffd) {
            b8_start = i;
            break;
        }
    }
    for (int i=0xff; i>=0x00; i--) {
        if ((*b8_conversion_table)[i] != fffd) {
            b8_end = i;
            break;
        }
    }

    return std::make_tuple(
        std::move(b8_conversion_table),
        std::move(cjk_conversion_table),
        Range{b8_start, b8_end},
        Range{cjk_row_start, cjk_row_end},
        Range{cjk_col_start, cjk_col_end}
    );
}

// /**
//  *  return a pointer to cp_data_type[0x100]
// */
// static cp_data_type* readB8ConversionTable(std::istream &b8, const cp_data_type fffd, Range &r) {
//     cp_data_type *table_b8 = new cp_data_type[0x100];
//     {
//         for(int i=0; i<0x100; i++) {
//             table_b8[i] = fffd; 
//         }
//         char c = b8.get();
//         b8.unget();
//         if(c != '#') {
//             fprintf(stderr, "8 bits table format invalid\n");
//             exit(1);
//         }
//         for (;;) {
//             c = b8.get();
//             if (c == EOF)
//                 break;
//             if (c == '\n' || c == ' ' || c == '\t')
//                 continue;
//             if (c == '#') {
//                 do { c = b8.get(); } while (!(c == EOF || c == '\n'));
//                 continue;
//             }
//             b8.unget();
//             std::string str;
//             std::getline(b8, str);
//             cp_data_type b8char, b8dst;
//             if (sscanf(str.c_str(), "0x%x 0x%x", &b8char, &b8dst) != 2 
//                 || !(b8char >= 0 && b8char < 0x100))
//                 fprintf(stderr, "0x%x is invalid.\n", b8char);
//             table_b8[b8char] = b8dst;
//         }
//     }

//     // cal size 
//     unsigned int b8_start = 0x00;
//     unsigned int b8_end = 0xff;
//     for (int i=0x00; i<0x100; i++) {
//         if (table_b8[i] != fffd) {
//             b8_start = i;
//             break;
//         }
//     }
//     for (int i=0xff; i>=0x00; i--) {
//         if (table_b8[i] != fffd) {
//             b8_end = i;
//             break;
//         }
//     }

//     r = Range{b8_start, b8_end};
//     return table_b8;
// }

// static cp_data_type** readCJKConversionTable(
//     std::istream &is,
//     const cp_data_type fffd, 
//     Range &rrow, Range &rcol
// ) {
//     // calculate cjk table size
//     unsigned int row_start = 0xff; 
//     unsigned int row_end = 0x00;
//     unsigned int col_start = 0xff;
//     unsigned int col_end = 0x00; 
//     {
//         int row, col;
//         std::istream temp(is.rdbuf());
//         /* must start with '#' */
//         char c = temp.get();
//         temp.unget();
//         if (c != '#') {
//             fprintf(stderr, "cjk table format invalid in cal\n");
//             exit(1);
//         }
//         /* Read a unicode.org style .TXT file. */
//         for (;;) {
//             c = temp.get();
//             if (c == EOF) {
//                 break;
//             }
//             if (c == '\n' || c == ' ' || c == '\t')
//                 continue;
//             if (c == '#') {
//                 do { c =  temp.get(); } while (!(c == EOF || c == '\n'));
//                 continue;
//             }
//             temp.unget();
            
//             std::string str;
//             std::getline(temp, str, ' ');

//             int hex_fromcode;
//             if (sscanf(str.c_str(), "0x%x", &hex_fromcode) != 1)
//                 exit(1);
//             row = hex_fromcode >> 8;
//             col = hex_fromcode & 0xff;
//             if ( 0 == row || 0 > col) {
//                 fprintf(stderr, "0x%x is not a valid value\n", hex_fromcode);
//                 exit(1);
//             } else {
//                 if (row < row_start) row_start = row;
//                 if (row > row_end) row_end = row;
//                 if (col < col_start) col_start = col;
//                 if (col > col_end) col_end = col;
//             }

//             /* discard hex values of tocode */
//             std::getline(temp, str);
//             if (sscanf(str.c_str(), " 0x%x", &hex_fromcode) != 1) {
//                 fprintf(stderr, "invalid format of table\n");
//                 exit(1);
//             }
//         }

//         is.seekg(0, std::ios_base::beg);
//     }

//     // cjk 
//     const int rows = row_end - row_start + 1; 
//     const int cols = col_end - col_start + 1; 

//     cp_data_type **table_cjk = new cp_data_type*[rows];
//     for (int r=0; r<rows; r++) {
//         table_cjk[r] = new cp_data_type[cols];
//         for (int c=0; c<cols; c++)
//             table_cjk[r][c] = fffd;
//     }

//     // read
//     {
//         char c = is.get();
//         is.unget();
//         if (c != '#') {
//             fprintf(stderr, "cjk table format invalid\n");
//             exit(1);
//         }

//         for (;;) {
//             c = is.get();
//             if (c == EOF)
//                 break;
//             if (c == '\n' || c == ' ' || c == '\t')
//                 continue;
//             if (c == '#') {
//                 do {c = is.get();} while (!(c == EOF || c == '\n'));
//                 continue;
//             }
//             is.unget();
//             std::string str;
//             std::getline(is, str, ' ');
//             int hex_fromcode;
//             if (sscanf(str.c_str(), "0x%x", &hex_fromcode) != 1)
//                 exit(1);

//             int row = (hex_fromcode >> 8) - row_start;
//             int col = (hex_fromcode & 0xff) - col_start;

//             if (row < 0 || col < 0) {
//                 fprintf(stderr, "lost entry for %02x %02x\n", row, col);
//                 exit(1);
//             }

//             std::getline(is, str);
//             int hex_to;
//             if (sscanf(str.c_str(), " 0x%x", &table_cjk[row][col]) != 1) {
//                 exit(1);
//             }  
//         }
//     }

//     rrow = Range{row_start, row_end};
//     rcol = Range{col_start, col_end};
//     return table_cjk;
// }

Encoding newEncoding(std::istream &conversions) {
    constexpr cp_data_type fffd = 0xfffd;
    
    // b8
    Range rb8, rrcjk, rccjk;
    std::unique_ptr<std::vector<cp_data_type>> conversion_b8;
    std::unique_ptr<std::vector<std::vector<cp_data_type>>> conversion_cjk;

    std::tie(conversion_b8, conversion_cjk, rb8, rrcjk, rccjk) = readConversionTable(conversions, fffd);

    return Encoding(
        fffd,
        rb8,
        std::move(conversion_b8),
        rrcjk,
        rccjk,
        std::move(conversion_cjk)
    );
}

Encoding newEncoding(const std::string &filename) {
    std::fstream fs{filename, std::fstream::in};
    if (!fs.is_open())
        throw UnexpectedError("file " + filename + " does not exist.");

    return newEncoding(fs);
}