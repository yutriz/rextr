#include <stdexcept>

class NotImplemented : public std::logic_error {
public:
    NotImplemented() : std::logic_error("Not yet implemented") { };
}; 


class UnexpectedError : public std::runtime_error{
public:
    UnexpectedError(const std::string &error_message) : std::runtime_error(error_message) { };
}; 