#ifndef REXT_UTILS_UNICODE_HXX
#define REXT_UTILS_UNICODE_HXX
// ref: http://www.zedwood.com/article/cpp-utf8-char-to-codepoint

#include <cstdint>
#include <string>

/* convert Code Point to Character */
inline std::string 
utf8Character_basic(int cp) {
    char c[5]={ 0x00,0x00,0x00,0x00,0x00 };
    if     (cp<=0x7F) { c[0] = cp;  }
    else if(cp<=0x7FF) { c[0] = (cp>>6)+192; c[1] = (cp&63)+128; }
    else if(0xd800<=cp && cp<=0xdfff) {} //invalid block of utf8
    else if(cp<=0xFFFF) { c[0] = (cp>>12)+224; c[1]= ((cp>>6)&63)+128; c[2]=(cp&63)+128; }
    else if(cp<=0x10FFFF) { c[0] = (cp>>18)+240; c[1] = ((cp>>12)&63)+128; c[2] = ((cp>>6)&63)+128; c[3]=(cp&63)+128; }
    return std::string(c);
}

/* Character to Code Point */
inline int_least32_t 
utf8CodePoint_basic(const std::string &u) {
    int l = u.length();
    if (l<1) return 0xfffff; unsigned char u0 = u[0]; if (u0>=0   && u0<=127) return u0;
    if (l<2) return 0xfffff; unsigned char u1 = u[1]; if (u0>=192 && u0<=223) return (u0-192)*64 + (u1-128);
    if (u[0]==0xed && (u[1] & 0xa0) == 0xa0) return 0xfffff; //code points, 0xd800 to 0xdfff
    if (l<3) return 0xfffff; unsigned char u2 = u[2]; if (u0>=224 && u0<=239) return (u0-224)*4096 + (u1-128)*64 + (u2-128);
    if (l<4) return 0xfffff; unsigned char u3 = u[3]; if (u0>=240 && u0<=247) return (u0-240)*262144 + (u1-128)*4096 + (u2-128)*64 + (u3-128);
    return 0xfffff;
}

#endif