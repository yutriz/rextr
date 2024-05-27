#include "src/repack/FontTable.hxx"

#include <string.h>
#include <iostream>
/** 
 * getopt? no, not for multiple arguments
 */

void Usage() {
    printf("\n");
    printf("Generate character set without duplicates. \n");
    printf("Usage:\n");
    printf("    nodupl -k KEY -c CHARACTER_PER_LINE file1 file2 ...\n");
    exit(0);
}

int main(int argc, char *argv[]) {
    if (argc < 5 || strcmp(argv[1], "-k") || strcmp(argv[3], "-c"))
        Usage();
    
    //
    assert(argv[2]);
    std::string key(argv[2]);
    int cpl = std::stoi(argv[4]);


    CharMap cm;
    for (int arg=5; arg<argc; arg++) 
        renewMap(cm, argv[arg], key);
    
    dumpMap(cm, std::cout, cpl);
}