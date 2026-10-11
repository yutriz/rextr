#ifndef REXTR_UTILS_JSON_HPP
#define REXTR_UTILS_JSON_HPP

#include <string>
#include <fstream>

#include <nlohmann/json.hpp>

using Json = nlohmann::ordered_json;

inline Json parseJson(const std::string &file_path) {
    std::ifstream f(file_path);
    Json data = Json::parse(f);

    return data;
}

inline size_t writeJson(const Json &j, std::ostream &os) {
    std::string s = j.dump(2);
    os << s << std::endl;
    return s.size();
}

inline size_t writeJson(const Json &j, const std::string &filename) {
    std::ofstream fs(filename);
    auto ret = writeJson(j, fs);
    fs.close();
    return ret;
}

#endif