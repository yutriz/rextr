#include "src/extr/Read.hxx"
#include "src/utils/Hash.hxx"

#include <istream>
#include <cassert>

/**
 *  return: 
 *      1 recognized
 *      0 unrecognized
 *     -1 eof reached
 */
static int 
readOne(CodePoint &src, CodePoint &dst, std::istream &is, 
        const Encoding &enc, bool cjk_only=0) {

    cp_basic c1 = static_cast<cp_basic>(is.get());
    if (is.eof()) 
        return -1;

    if (auto cp = enc.conv(CodePoint{CodePoint_t::B8, c1}, cjk_only); 
        cp.t != CodePoint_t::ERR) { 
        src = CodePoint{CodePoint_t::B8, c1};
        dst = cp;
        return 1;
    } 

    auto pos = is.tellg();
    cp_basic c2 = static_cast<cp_basic>(is.get());
    if (is.eof()) {
        is.clear();
        is.seekg(pos);
        src = CodePoint{CodePoint_t::B8, c1};
        return 0;
    } 

    cp_basic cp_val = (c1<<8) + static_cast<cp_basic>(c2);
    if (auto cp = enc.conv(CodePoint{CodePoint_t::CJK, cp_val}, cjk_only); 
        cp.t != CodePoint_t::ERR) {
        src = CodePoint{CodePoint_t::CJK, cp_val};
        dst = cp;
        return 1;
    }
    
    is.unget();
    // else EXT 

    src = CodePoint(CodePoint_t::B8, c1);
    dst = CodePoint{CodePoint_t::ERR, 0};
    return 0;
}

BasicBlock
newBlock(std::istream &is, const Encoding &enc, bool cjk_only, int minimum_len) {
    using CPL = BasicBlock::CodePointList;
    std::unique_ptr<CPL> cpl    = std::unique_ptr<CPL>(new CPL{});
    std::unique_ptr<CPL> cpl_tl = std::unique_ptr<CPL>(new CPL{});

    size_t len = 0;
    auto pos_start = is.tellg();

    CodePoint src = CodePoint{CodePoint_t::ERR, 0xfffd};
    CodePoint dst = CodePoint{CodePoint_t::ERR, 0xfffd};

    auto first_state = readOne(src, dst, is, enc, cjk_only);
    if (src.t == CodePoint_t::B8)
        len += 1;
    else if (src.t == CodePoint_t::CJK)
        len += 2;

    cpl->push_back(src);
    if (first_state == 1) 
        cpl_tl->push_back(dst);
    
    for(;;) {
        auto state = readOne(src, dst, is, enc, cjk_only);
        // eof
        if (state == -1)
            break;
        // type first cp
        if (first_state == state) {
            cpl->push_back(src);
            if (state == 1) 
                cpl_tl->push_back(dst);
            if (src.t == CodePoint_t::B8)
                len += 1;
            else if (src.t == CodePoint_t::CJK)
                len += 2;
        } else {
            is.unget();
            if (src.t == CodePoint_t::CJK)
                is.unget();
            if (src.t == CodePoint_t::EXT)
                is.unget();
            break;
        }
    }

    bool isTl = (first_state == 1 && len > minimum_len)? true:false;
    return BasicBlock(static_cast<size_t>(pos_start), len, cpl, 
                      isTl, cpl_tl, std::string(""));
}

Scene
newScene(const char *filename, const Encoding &enc, bool cjk_only, int minimum_len) {
    std::ifstream fp(filename, std::ios::binary | std::ios_base::in);
    assert(fp);

    using TBL = Scene::TextBlockList;
    std::unique_ptr<TBL> tbl = std::unique_ptr<TBL>(new TBL{});
    size_t num_blocks = 0;

    while(fp) {
        tbl->push_back(newBlock(fp, enc, cjk_only));
        num_blocks++;
        tbl.get()->back().setNum(num_blocks);
    }

    fp.close();
    
    return Scene(MD5sum(filename), num_blocks, tbl);
}

