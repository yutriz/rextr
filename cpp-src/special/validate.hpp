#ifndef REXTR_REPACK_VALIDATE_HPP
#define REXTR_REPACK_VALIDATE_HPP

#include "structure/scene.hpp"

#include <string>

const std::string SN1_GAME_NAME = "SN1_NDS";


class Validator {
public:
    Validator() = default;
    static int validateScene(const std::string &game, RepackScene &rscn, const std::string &filename);

private:
    static int _validateScene_NDS_SN1(RepackScene &rscn, const std::string &filename);
    // add more 
};

#endif