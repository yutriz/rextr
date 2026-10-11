#ifndef REXTR_UTILS_FILEPATH_HPP
#define REXTR_UTILS_FILEPATH_HPP

#include <filesystem>
#include <string>

std::string getParentDir(const std::string &filepath);
std::string getFileName(const std::string &filepath);
std::string getFileExtension(const std::string &filepath);
std::string getFileStem(const std::string &filepath);
std::string getDumpedFileName(const std::string &filepath);

#endif