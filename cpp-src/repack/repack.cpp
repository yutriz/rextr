#include "repack/repack.hpp"
#include "special/validate.hpp"
#include "utils/binary_io.hpp"
#include "utils/string_utils.hpp"

#include <cassert>

/**
 * 1. Standard. Start counting from the start of the file. Sometimes known as
 *    linear pointers although the term does technically encompass the second type.
 * 2. Offset. Start counting from some point in the file (quite often the start of
 *    the proper data/end of the header).
 * 3. Relative. Start counting from where the actual pointer is at (if the pointer
 *    reads 30h and is located at 20h the data in question is likely at 50h).
 * 
 *  - GBA and DS ROM hacking guide - 2016 edition
 */

// legacy
#define REPACK_ENGLISH false
#define GAME_NAME "SN1_NDS"

size_t repack(
    RepackScene &rscn, 
    Encoding &enc, 
    const std::string &origin_filepath,
    const std::string &output_filepath, 
    bool is_little_endian, 
    bool do_validation
) {
    if (do_validation) {
        Validator::validateScene(GAME_NAME, rscn, origin_filepath);
    }

    std::vector<char> chunk_data; // char or unsigned char doesn't matter

    std::ifstream ifs(origin_filepath, std::ios::binary);
    chunk_data.assign( 
        std::istreambuf_iterator<char>(ifs),
        std::istreambuf_iterator<char>()   
    );
    ifs.close();

    size_t r_offset = 0; // raw file ptr offset
    
    auto ofs = std::ofstream(output_filepath, std::ios::binary);

    for (auto iter=rscn.m_textblocks->begin(); iter!=rscn.m_textblocks->end(); ++iter) {
        size_t buffer_size = iter->m_offset - r_offset;
        
        ofs.write(chunk_data.data()+sizeof(char)*r_offset, buffer_size-1);
        r_offset += buffer_size;

        if(!REPACK_ENGLISH) {
            auto len_zh = countBytes(iter->m_translated_text);
            writeIntBinary(ofs, len_zh, is_little_endian, 1);

            writeEncodingConvertedStringBinary(
                ofs, 
                iter->m_translated_text, 
                is_little_endian,
                enc
            );
            r_offset += iter->m_len; // origin 
        } else {
            auto len_en = countBytes(iter->m_translated_text_en);
            writeIntBinary(ofs, len_en, is_little_endian, 1);

            writeEncodingConvertedStringBinary(
                ofs, 
                iter->m_translated_text_en, 
                is_little_endian,
                enc
            );
            r_offset += iter->m_len; 
        }
    }

    size_t end = chunk_data.size();
    size_t buffer_size = end - r_offset;
    ofs.write(chunk_data.data()+sizeof(char)*r_offset, buffer_size);
    //os.flush();
    r_offset += buffer_size;

    return r_offset;
}


