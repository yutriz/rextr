#include "utils/string_utils.hpp"

#ifdef _WIN32
#include <windows.h>
#else // UNIX 
#include <locale>
#include <codecvt> // codecvt will be deprecated in C++26 
#endif

std::wstring stringToWstring(const std::string &str) {
#ifdef _WIN32
    // int slength = (int)s.length() + 1;
    // int len = WideCharToMultiByte(CP_ACP, 0, s.c_str(), slength, 0, 0, 0, 0);

    //     int isize = MultiByteToWideChar();
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
#else
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> conv;
    return conv.from_bytes(str);
#endif
}

std::string wstringToString(const std::wstring &wstr) {
#ifdef _WIN32
    if (wstr.empty())
        return std::string("");

    size_t charsNeeded = WideCharToMultiByte(CP_UTF8, 0, 
                            wstr.data(), (int)wstr.size(), NULL, 0, NULL, NULL);
    char buffer[charsNeeded];
    int charsConverted = WideCharToMultiByte(CP_UTF8, 0, 
                            wstr.data(), (int)wstr.size(), &buffer[0], charsNeeded, NULL, NULL);
    assert(charsConverted != 0);

    return std::string(&buffer[0], charsConverted);
#else
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> conv;
    return conv.to_bytes(wstr);
#endif
}

size_t countBytes(const std::string &str) {
    std::wstring wstr = stringToWstring(str);
    size_t bytes = 0;
    for (auto wc:wstr) {
        int n = (static_cast<int>(wc)>>8)? 2:1;
        bytes += n;
    }
    return bytes;
}