#include "enc/CodePoint.hxx"
#include "repack/FontTable.hxx"
#include "utils/Wide.hxx"
#include "utils/Unicode.hxx"

/**
 * 
 */
int renewMap(CharMap &cm, const Json &jscn, std::string jkey) {
    for (auto &blk : jscn["blocks"]) {
        auto str = blk.at(jkey).get<std::string>();
        auto wstr = string2wstring(str);
        for (auto wc : wstr) {
            // no need add 8 bit Code Point to map
            // if (auto cp = static_cast<cp_basic>(wc); cm.find(cp) == cm.end())
            if (auto cp = static_cast<cp_basic>(wc); cp>=0x100 && cm.find(cp) == cm.end())
                cm.insert({cp, true});
        }
    }
    return cm.size();
}

int renewMap(CharMap &cm, const char* jfscn, std::string jkey) {
    std::ifstream ifs(jfscn);
    assert(ifs);
    Json jscn = Json::parse(ifs);
    return renewMap(cm, jscn, jkey);
}

/**
 * cpl = characters per line 
 */
int dumpMap(const CharMap &cm, std::ostream &os, int cpl) {
    int count = 0;
    for (auto iter=cm.begin(); iter!=cm.end(); ++iter) {
        os << utf8Character_basic(iter->first);
        count++;
        if (!(count%cpl))
            os << "\n";
    }
    return count;
}

int dumpMap(const CharMap &cm, const char *ofile, int cpl) {
    std::ofstream ofs(ofile);
    assert(ofs);
    return dumpMap(cm, ofs, cpl);
}

