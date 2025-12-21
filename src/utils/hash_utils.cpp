#include <cassert>
#include <fstream>
#include <iomanip>
#include <openssl/md5.h>

/**
 *  warning: 'unsigned char* MD5(const unsigned c
 *  har*, size_t, unsigned char*)' is deprecated: Since OpenSSL
 *  3.0 [-Wdeprecated-declarations]
 * 
 *  #include <openssl/evp.h>
 *  EVP_Q_digest(NULL, "MD5", NULL, target.c_str(), target.size(), digest, NULL);
 */

#include "utils/hash_utils.hpp"
#include "utils/hex_utils.hpp"

std::string MD5sum(const std::string &fn) {
    std::ifstream f(fn, std::ios::ate | std::ios::binary);
    assert(f.is_open());

    std::ifstream::pos_type fileSize = f.tellg();
    char *memBlock = new char[fileSize];

    f.seekg(0, std::ios::beg);
    f.read(memBlock, fileSize);
    f.close();

    //get md5 sum
    unsigned char result[MD5_DIGEST_LENGTH];
    MD5((unsigned char*) memBlock, fileSize, result);
    delete[] memBlock;
    return hexUchars2Str(result, MD5_DIGEST_LENGTH);
}

