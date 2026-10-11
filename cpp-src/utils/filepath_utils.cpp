#include "utils/filepath_utils.hpp"

#include <filesystem>

namespace fs = std::filesystem;

std::string getParentDir(const std::string &filepath) {
    fs::path p(filepath);

    return p.parent_path();
}

std::string getFileName(const std::string &filepath) {
    fs::path p(filepath);

    return p.filename();
}

std::string getFileExtension(const std::string &filepath) {
    fs::path p(filepath);

    return p.extension();
}

std::string getFileStem(const std::string &filepath) {
    fs::path p(filepath);

    return p.stem();
}

std::string getDumpedFileName(const std::string &filepath) {
    std::string parent_dir = getParentDir(filepath);
    std::string file_stem = getFileStem(filepath);
    std::string file_extension = getFileExtension(filepath);

    std::string dumped_json_filepath = fs::path(parent_dir) / (file_stem+".recog.json");

    return dumped_json_filepath;
}