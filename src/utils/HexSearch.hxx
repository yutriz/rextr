#include <fstream>
#include <iostream>
#include <unitypes.h>
#include "./Hex.hxx"

void findAdjcant_2Bytes(std::istream &is, int times) {
    uint32_t last = 0x10000;
    short count = 0;
    size_t offset = 0;
    uint32_t c1, c2;
    while(!is.eof()) {
        c1 = is.get();
        if(!is.eof()) {
            c2 = is.get();
        } else {
            break;
        }
        uint32_t u16 = (c1<<8) + c2;

        // std::cout << std::hex<<u16 <<"\n";
        // ignore "00 00"
        if (u16 == 0 || u16==0x0101 || u16==0xffff) {
            count = 0;
            continue;
        }
            
        if (u16 == last) {
            count++;
        } else {
            last = u16;
            count = 0;
        }
        if (count == 3) {
            auto single = hex2str(u16, 4);
            std::cout << "at offset: " << hex2String_long(offset) <<
                ", " << single << " appears " << times << "times\n";
            count = 0;
        }
        offset+=2; 
    }
}