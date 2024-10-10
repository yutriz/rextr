#include "repack/Packing.hxx"
#include "utils/WriteBin.hxx"
#include "utils/Wide.hxx"

#include <cassert>

/**
 * 1. Standard. Start counting from the start of the file. Sometimes known as
 *    linear pointers although the term does technically encompass the second type.
 * 2. Offset. Start counting from some point in the file (quite often the start of
 *    the proper data/end of the header).
 * 3. Relative. Start counting from where the actual pointer is at (if the pointer
 *    reads 30h and is located at 20h the data in question is likely at 50h).
 * 
 *  - GBA and DS ROM hacking guide - 2016 edition.  FAST6191
 */

inline static size_t 
countBytes(const std::string &str) {
    std::wstring wstr = string2wstring(str);
    size_t bytes = 0;
    for (auto wc:wstr) {
        int n = (static_cast<int>(wc)>>8)? 2:1;
        bytes += n;
    }
    return bytes;
}

size_t repack_offset(SceneR_offset &scnro, const char *rawfile, std::ostream &os, 
                     int (*checkFunc)(SceneR_offset&, const char *)) {
    checkFunc(scnro, rawfile);

    std::ifstream rfp(rawfile, std::ios::binary);
    size_t rfp_offset = 0;

    for (auto iter : *(scnro.m_blks)) {
        rfp.seekg(rfp_offset, std::ios::beg);
        const size_t buffer_size = iter.m_offset - rfp_offset;
        char *buffer = new char[buffer_size];
        rfp.read(buffer, buffer_size-1); 
        os.write(buffer, buffer_size-1);

        writeBin_val(os, iter.m_translated_text.length(), 1);
        //os.flush();
        rfp_offset += buffer_size;
        rfp_offset += iter.m_len;

        writeBin_mixed(os, iter.m_translated_text);
        delete[] buffer;
    }

    rfp.seekg(0, std::ios::end);
    size_t fend = rfp.tellg();
    rfp.seekg(rfp_offset, std::ios::beg);
    size_t buffer_size = fend - rfp_offset;
    char buffer[buffer_size];
    rfp.read(buffer, buffer_size);
    os.write(buffer, buffer_size);
    //os.flush();
    rfp_offset += buffer_size;

    return rfp_offset;
}

size_t repack_offset_enc(SceneR_offset &scnro, const char *rawfile, 
                        Encoding &enc, std::ostream &os, 
                        int (*checkFunc)(SceneR_offset&, const char *)) {
    checkFunc(scnro, rawfile);
    
    std::ifstream rfp(rawfile, std::ios::binary);
    size_t rfp_offset = 0;

    for (auto iter : *(scnro.m_blks)) {
        rfp.seekg(rfp_offset, std::ios::beg);
        const size_t buffer_size = iter.m_offset - rfp_offset;
        char *buffer = new char[buffer_size];
        rfp.read(buffer, buffer_size-1); 
        os.write(buffer, buffer_size-1);

        auto len_zh = countBytes(iter.m_translated_text_zh);
        writeBin_val(os, len_zh, 1);

        //os.flush();
        rfp_offset += buffer_size;
        rfp_offset += iter.m_len;

        writeBin_mixed_enc(os, iter.m_translated_text_zh, enc);

        delete[] buffer;
    }

    rfp.seekg(0, std::ios::end);
    size_t fend = rfp.tellg();
    rfp.seekg(rfp_offset, std::ios::beg);
    size_t buffer_size = fend - rfp_offset;
    char buffer[buffer_size];
    rfp.read(buffer, buffer_size);
    os.write(buffer, buffer_size);
    //os.flush();
    rfp_offset += buffer_size;

    return rfp_offset;
}


