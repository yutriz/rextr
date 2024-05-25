#ifndef REXTR_CMD_OPTS_HXX
#define REXTR_CMD_OPTS_HXX

#include <unistd.h>
#include <getopt.h>
#include <iostream>
#include <string>

/**
 *  long  opt: const char*
 * 	short opt: char
 * 	has value: bool
 * 	val  type: const char*
 * 	desc	 : const char* 
 */
struct OptionDef {
	const char *long_option;
	char short_option;
	bool has_value = false;
    const char *value_type;
	const char *desc;
};

void PrintOpts(const OptionDef &opt) {
    if(opt.has_value)
	    printf("  -%c, --%-8s%-8s%s\n",
		        opt.short_option,
		        opt.long_option,
                opt.value_type,
		        opt.desc);
	else
		printf("  -%c, --%-8s%-8s%s\n",
		        opt.short_option,
		        opt.long_option,
                "",
		        opt.desc);
}

inline std::string 
addSuffix(std::string str, std::string suff) {
	return str+suff;
}



#endif

