#include "utils/binary_io.hpp"
#include "utils/string_utils.hpp"
#include "utils/exceptions.hpp"

#include <cstdint>
#include <cstring>

/**
 * oops the endian! 
 * n = char numbers 
 *    0x11    char 1
 *    0x1234  char 2
 */

void writeIntBinary(
    std::ostream &os, 
    uint_least32_t val, 
    bool is_little_endian,
    const short n
) {
    char buf[n];
    char *c = reinterpret_cast<char*>(&val);

    if (is_little_endian) {
        for (auto i=0; i<n; ++i)
            buf[n-1-i] = c[i];
    } else { // big endian
        for (auto i=0; i<n; ++i)
            buf[n] = c[n];
    }

    os.write(buf, n);
}

/**
 * "a1" -> 0xa1
 * combine 2 chars(string) to a char(integer) 
 */
static uint16_t combineTwoChars(const char* c) {
    int ret;
    char ns[2]; 
    memcpy(ns, c, 2);
    sscanf(ns, "%x", &ret);
    return ret;
}

static uint16_t combineTwoChars(const char c1, const char c2) {
    int ret;
    char ns[2]; 
    ns[0] = c1;
    ns[1] = c2;
    sscanf(ns, "%x", &ret);
    return ret;
}

/**
 * hex string like "0123456789abcdef" => "01 23 45 67 89 ab cd ef"
 */ 
size_t ParseHexPairsAndWriteBinary(
    std::ostream &os, 
    const std::string &str,
    bool is_little_endian
) {
    size_t wb = 0; /* written bytes */

    if (str.size()%2) {
        std::string error_msg = "Hex string " + str + " can not be presented as pairs";
        throw UnexpectedError(error_msg);
    }

    const char* cstr = str.c_str();
    while(*cstr) {
        auto c2 = combineTwoChars(cstr);
        writeIntBinary(os, c2, is_little_endian, 1);
        wb += 1;
        cstr += 2;
    }
    return wb;
}

/**
 * consist of only wide char, unused
 */
size_t writeWideStringBinary(
    std::ostream &os, 
    const std::string &str,
    bool is_little_endian
) {
    std::wstring wstr = stringToWstring(str);
    size_t wb = 0; /* written bytes */
    for (auto wc:wstr) {
        /* thanks to wchar_t = code point */
        writeIntBinary(os, wc, is_little_endian, sizeof(wc)); // sizeof(wc) should be 4
        wb += sizeof(wc);
    }
    return wb;
}

/** 
 * characters that can be represented as char will count 8 bits only
 */
size_t writeStringBinary(
    std::ostream &os, 
    const std::string &str,
    bool is_little_endian
) {
    std::wstring wstr = stringToWstring(str);
    size_t wb = 0; /* written bytes */
    for (auto wc:wstr) {
        short n = (static_cast<int>(wc)>>8)? 2:1;
        writeIntBinary(os, wc, is_little_endian, n);
        wb += n;
    }
    return wb;
}

size_t writeEncodingConvertedStringBinary(
    std::ostream &os, 
    const std::string &str,
    bool is_little_endian,
    Encoding &enc
) {
    std::wstring wstr = stringToWstring(str);
    size_t wb = 0; /* written bytes */
    for (auto wc:wstr) {
        auto t = (static_cast<cp_data_type>(wc)>>8)? CodePointType::CJK : CodePointType::B8;
        auto cp = enc.conv(CodePoint{t, static_cast<cp_data_type>(wc)});
        short n = (cp.t==CodePointType::CJK)? 2:1;
        writeIntBinary(os, cp.val, is_little_endian, n);
        wb += n;
    }
    return wb;
}
