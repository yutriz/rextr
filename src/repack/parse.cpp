#include "structure/block.hpp"
#include "repack/parse.hpp"
#include "utils/hex_utils.hpp"

#include <fstream>

RepackBlock parseRepackBlock(const Json &j) {
    auto pointer_type = PointerType::OFFSET; // fixed  

    return RepackBlock(
        j.at(SPEC_KEYNAME_BLOCK_NUM).get<int>(),
        safeConverter(j.at(SPEC_KEYNAME_POINTER_TYPE).get<int>()),
        str2HexSizeT(j.at(SPEC_KEYNAME_OFFSET).get<std::string>().c_str()),
        j.at(SPEC_KEYNAME_LEN).get<size_t>(), 
        std::string(""), // unused, j.at(SPEC_KEYNAME_ORIGNAL_HEX).get<std::string>(),
        j.at(SPEC_KEYNAME_IS_RECOGNIZED).get<bool>(),
        std::string(""), // j.at(SPEC_KEYNAME_RECOGNIZED_TEXT).get<std::string>(),
        j.at(SPEC_KEYNAME_IS_TRANSLATED).get<bool>(),
        j.at(SPEC_KEYNAME_TRANSLATED_TEXT).get<std::string>(),
        j.at(SPEC_KEYNAME_TRANSLATED_TEXT_EN).get<std::string>()
    );
}

RepackScene parseRepackScene(const Json &j) {
    using TRBL = RepackScene::TextRepackBlockList;
    std::unique_ptr<TRBL> blks = std::make_unique<TRBL>();

    for (auto &blk : j[SPEC_KEYNAME_BLOCKS]) {
        if(blk.at(SPEC_KEYNAME_IS_TRANSLATED).get<bool>() == true)
            blks->push_back(parseRepackBlock(blk));
    }

    return RepackScene(
        j.at(SPEC_KEYNAME_MD5SUM).get<std::string>(), 
        blks->size(),
        std::move(blks)
    );
}
