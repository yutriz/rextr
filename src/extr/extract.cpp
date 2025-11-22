#include "extr/extract.hpp"
#include "utils/hash_utils.hpp"

#include <istream>
#include <iostream>
#include <cassert>
#include <stdexcept>

#define PRINT_RECOGNIZED_TEXT true

enum class RFLAG {
    RECOGN,
    UNRECOGN,
    CHUNK_END
};

/**
 *  return: 
 *      1 recognized
 *      0 unrecognized
 *     -1 eof reached
 */
static RFLAG readOne(
    CodePoint &src, 
    CodePoint &dst, 
    std::vector<unsigned char> &chunk,
    size_t &current_pos, // will access this pos
    size_t chunk_end_pos, // dont call it every time
    const Encoding &enc,
    bool cjk_only=0
) {

    bool b8_detected = false;
    bool cjk_detected = false;
    
    if (current_pos >= chunk_end_pos) 
        return RFLAG::CHUNK_END;

    cp_data_type c1 = static_cast<cp_data_type>(chunk[current_pos]);

    current_pos++;

    auto cp1 = enc.conv(CodePoint{CodePointType::B8, c1}, cjk_only); 
    
    if (cp1.t != CodePointType::ERR) { 
        b8_detected = true;
    } 
    
    if (current_pos >= chunk_end_pos) {
        src = CodePoint{CodePointType::B8, c1};
        return RFLAG::UNRECOGN;
    }

    cp_data_type c2 = static_cast<cp_data_type>(chunk[current_pos]);

    cp_data_type cp2_val = (c1<<8) + static_cast<cp_data_type>(c2);
    current_pos++;

    auto cp2 = enc.conv(CodePoint{CodePointType::CJK, cp2_val}, cjk_only);
    if (cp2.t != CodePointType::ERR) {
        cjk_detected = true;
    }

    if (cjk_detected) {
        src = CodePoint{CodePointType::CJK, cp2_val};
        dst = cp2;
        return RFLAG::RECOGN;
    }

    current_pos--;
    
    if (b8_detected) {
        src = CodePoint{CodePointType::B8, c1};
        dst = cp1;
        return RFLAG::RECOGN;
    }

    src = CodePoint(CodePointType::B8, c1);
    dst = CodePoint{CodePointType::ERR, 0};
    return RFLAG::UNRECOGN;
}

Block newBlock(
    std::vector<unsigned char> &chunk, 
    size_t &current_pos,
    size_t end_pos,
    const Encoding &enc,
    bool cjk_only, 
    int minimum_len
) {

    using CPL = Block::CodePointList;
    std::unique_ptr<CPL> cpl       = std::make_unique<CPL>();
    std::unique_ptr<CPL> cpl_recog = std::make_unique<CPL>();

    size_t len = 0;
    size_t pos_start = current_pos;

    CodePoint src = CodePoint{CodePointType::ERR, 0xfffd};
    CodePoint dst = CodePoint{CodePointType::ERR, 0xfffd};

    auto first_state = readOne(src, dst, chunk, current_pos, end_pos, enc, cjk_only);

    if (src.t == CodePointType::B8)
        len += 1;
    else if (src.t == CodePointType::CJK)
        len += 2;

    cpl->push_back(src);
    if (first_state == RFLAG::RECOGN) 
        cpl_recog->push_back(dst);
    
    for(;;) {
        auto state = readOne(src, dst, chunk, current_pos, end_pos, enc, cjk_only);
        // eof
        if (state == RFLAG::CHUNK_END)
            break;
        // type of first cp
        if (first_state == state) {
            cpl->push_back(src);
            if (state == RFLAG::RECOGN) 
                cpl_recog->push_back(dst);
            if (src.t == CodePointType::B8)
                len += 1;
            else if (src.t == CodePointType::CJK)
                len += 2;
        } else {
            current_pos--;
            if (src.t == CodePointType::CJK)
                current_pos--;
            // unused
            // if (src.t == CodePointType::EXT)
            //     current_pos--;
            break;
        }
    }

    bool is_recogn = (first_state == RFLAG::RECOGN && len > minimum_len)? true:false;
    
    if (is_recogn && PRINT_RECOGNIZED_TEXT) {
        // \n to literal "\n"
        std::string recognzed_str = Block::UnicodeCodePointToText(*cpl_recog);

        std::string lf = "\n";
        std::string literal = "\\n";
        size_t pos = 0;
        while ((pos = recognzed_str.find(lf, pos)) != std::string::npos) {
            recognzed_str.replace(pos, lf.length(), literal);
            
            pos += literal.length();
        }
        std::cout << "recognized text: " << recognzed_str << std::endl;
    }

    return Block(
        PointerType::OFFSET,
        pos_start, 
        len, 
        std::move(cpl), 
        is_recogn, 
        std::string(""),// do it when dumping to json
        std::move(cpl_recog), 
        false
    );
}

Scene newSceneFromFile(const std::string &filename, const Encoding &enc, bool cjk_only, int minimum_len) {
    std::ifstream fs(filename, std::ios::binary | std::ios_base::in);
    
    if (!fs) {
        throw std::runtime_error("Error: Could not open file '" + filename + "'.");
    }


    // safe: char to unsigned char 
    std::vector<unsigned char> chunk_data( (std::istreambuf_iterator<char>(fs)), // most vexing parse
                                            std::istreambuf_iterator<char>()  );

    using TBL = Scene::TextBlockList;
    std::unique_ptr<TBL> tbl = std::make_unique<TBL>();

    size_t num_blocks = 0;

    size_t current_pos = 0;
    size_t end_pos = chunk_data.size();

    while(current_pos < end_pos) {
        tbl->push_back(
            newBlock(chunk_data, current_pos, end_pos, enc, cjk_only, minimum_len)
        );

        num_blocks++;
        tbl.get()->back().setNum(num_blocks);
    }

    fs.close();
    
    return Scene(MD5sum(filename), num_blocks, std::move(tbl));
}

