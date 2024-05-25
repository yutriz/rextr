#ifndef REXT_UTILS_WIDE_HXX
#define REXT_UTILS_WIDE_HXX

#include <string>
#include <cassert>

#ifdef _WIN32
#include <windows.h>
// int slength = (int)s.length() + 1;
// int len = WideCharToMultiByte(CP_ACP, 0, s.c_str(), slength, 0, 0, 0, 0);

//     int isize = MultiByteToWideChar();
inline std::wstring 
string2wstring(const std::string &str) {
    if (str.empty())
        return std::wstring(L"");
    
    size_t wcharsNeeded = MultiByteToWideChar(CP_UTF8, 0, 
                            str.data(), (int)str.size(), NULL, 0);
    
    assert(wcharsNeeded != 0);
    wchar_t buffer[wcharsNeeded];
    int wcharsConverted = MultiByteToWideChar(CP_UTF8, 0,
                            str.data(), (int)str.size(), &buffer[0], wcharsNeeded);

    assert(wcharsConverted != 0);

    return std::wstring(&buffer[0], wcharsConverted);
}


inline std::string
wstring2string(const std::wstring &wstr) {
    if (wstr.empty())
        return std::string("");

    size_t charsNeeded = WideCharToMultiByte(CP_UTF8, 0, 
                            wstr.data(), (int)wstr.size(), NULL, 0, NULL, NULL);
    char buffer[charsNeeded];
    int charsConverted = WideCharToMultiByte(CP_UTF8, 0, 
                            wstr.data(), (int)wstr.size(), &buffer[0], charsNeeded, NULL, NULL);
    assert(charsConverted != 0);

    return std::string(&buffer[0], charsConverted);
}


#else
// UNIX 
// codecvt will be deprecated in C++26 
#include <locale>
#include <codecvt>

std::wstring string2wstring(const std::string &str) {
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> conv;
    return conv.from_bytes(str);
}

std::string wstring2string(const std::wstring &wstr) {
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> conv;
    return conv.to_bytes(wstr);
}

#endif
#endif