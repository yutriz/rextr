#ifndef REXT_UTILS_WB_HXX
#define REXT_UTILS_WB_HXX

#include "src/utils/Wide.hxx"

#include <cstdint>
#include <cstring>
#include <fstream>

/**
 * oops the endian! 
 * n = char numbers 
 *    0x11    char 1
 *    0x1234  char 2
 */
inline void
writeBin_val(std::ostream &os, uint_least32_t val, const short n) {
    char buf[n];
    char *c = reinterpret_cast<char*>(&val);
    for (auto i=0; i<n; ++i)
        buf[n-1-i] = c[i];
    os.write(buf, n);
}

/**
 * "a1" -> 0xa1
 * combine 2 chars(string) to a char(integer) 
 */
inline uint16_t
charCombine(const char* c) {
    int ret;
    char ns[2]; 
    memcpy(ns, c, 2);
    sscanf(ns, "%x", &ret);
    return ret;
}

/**
 * hex string like "0123456789abcdef"
 */
inline size_t 
writeBin_hexStr(std::ostream &os, std::string &str) {
    size_t wb = 0; /* written bytes */
    if (str.size()%2)
        return 0; /* broken */
    const char* cstr = str.c_str();
    while(*cstr) {
        auto c2 = charCombine(cstr);
        writeBin_val(os, c2, 1);
        wb += 1;
        cstr += 2;
    }
    return wb;
}

/**
 * consist of only wide char 
 */
inline size_t
writeBin_wideOnly(std::ostream &os, std::string &str) {
    std::wstring wstr = string2wstring(str);
    size_t wb = 0; /* written bytes */
    for (auto wc:wstr) {
        /* thanks wchar_t = code point */
        writeBin_val(os, wc, sizeof(wc));
        wb += sizeof(wc);
    }
    return wb;
}

inline size_t
writeBin_mixed(std::ostream &os, std::string &str) {
    std::wstring wstr = string2wstring(str);
    size_t wb = 0; /* written bytes */
    for (auto wc:wstr) {
        short n = (static_cast<int>(wc)>>8)? 2:1;
        writeBin_val(os, wc, n);
        wb += n;
    }
    return wb;
}

#endif