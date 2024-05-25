#include "src/repack/ReadR.hxx"
#include "src/utils/Hex.hxx"

#include <fstream>

BlockR_full 
Json2BlockR_full(const Json &j) {
    return 
    BlockR_full(
        j.at("num").get<int>(),
        str2hex_size_t(j.at("offset").get<std::string>().c_str()),
        j.at("len").get<size_t>(), 
        j.at("orig_hex").get<std::string>(),
        j.at("translated").get<bool>(),
        j.at("translated_text").get<std::string>(),
        j.at("translated_text_zh").get<std::string>()
    );
}

SceneR_full
Json2SceneR_full(const Json &j) {
    using BRL =SceneR_full::BlockRList;
    std::unique_ptr<BRL> blks = std::unique_ptr<BRL>(new BRL);

    for (auto &blk : j["blocks"]) {
        if(blk.at("translated").get<bool>() == true)
            blks->push_back(Json2BlockR_full(blk));
    }
    return SceneR_full(j.at("md5").get<std::string>(), blks);
}

SceneR_full readSceneR_full(const char *jf) {
    std::fstream jfp(jf);
    return Json2SceneR_full(Json::parse(jfp));
}

/**
 *  Type 1: Standard
 */

/**
 *  Type 2: offset 
 */
BlockR_offset 
Json2BlockR_offset(const Json &j) {
    return 
    BlockR_offset(
        str2hex_size_t(j.at("offset").get<std::string>().c_str()),
        j.at("len").get<size_t>(), 
        j.at("translated").get<bool>(),
        j.at("translated_text").get<std::string>(),
        j.at("translated_text_zh").get<std::string>()
    );
}

SceneR_offset 
Json2SceneR_offset(const Json &j) {
    using BRL = SceneR_offset::BlockRList;
    std::unique_ptr<BRL> blks = std::unique_ptr<BRL>(new BRL);

    for (auto &blk : j["blocks"]) {
        if(blk.at("translated").get<bool>() == true)
            blks->push_back(Json2BlockR_offset(blk));
    }
    return SceneR_offset(j.at("md5").get<std::string>(), blks);
}

SceneR_offset readSceneR_offset(const char *jf) {
    std::fstream jfp(jf);
    return Json2SceneR_offset(Json::parse(jfp));
}


/**
 * Type 3: relative
 */