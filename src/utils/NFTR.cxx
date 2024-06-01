#include <fstream>
#include <unordered_map>
#include <cstdint>

// http://problemkaputt.de/gbatek.htm#dscartridgenitrofontresourceformat

// int >= 16 bits

using u = uint8_t;

struct H_NFTR {
    bool LE;
    int version;
    size_t decomp_size;
    int chunk_size; /* Offset to "FNIF" Chunk, aka Size of "RTFN" Chunk (0010h) */
    int num_chunks;    /* Total number of following Chunks (0003h+NumCharMaps) (0018h)*/
};

struct H_FNIF {
    int chunk_size;
    
}