#ifndef REXT_UTILS_BINARY_HPP
#define REXT_UTILS_BINARY_HPP

#include "enc/encoding.hpp"

#include <string>
#include <fstream>

void writeIntBinary(
    std::ostream &os, 
    uint_least32_t val, 
    bool is_little_endian,
    const short n
);

size_t ParseHexPairsAndWriteBinary(
    std::ostream &os, 
    const std::string &str,
    bool is_little_endian
);

size_t writeWideStringBinary(
    std::ostream &os, 
    const std::string &str,
    bool is_little_endian
);

size_t writeStringBinary(
    std::ostream &os, 
    const std::string &str,
    bool is_little_endian
);


size_t writeEncodingConvertedStringBinary(
    std::ostream &os, 
    const std::string &str,
    bool is_little_endian,
    Encoding &enc
);



#endif