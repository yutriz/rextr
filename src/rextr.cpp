#include "enc/encoding.hpp"
#include "enc/code_point.hpp"
#include "enc/shift_jis.hpp"
#include "extr/extract.hpp"
#include "extr/dump.hpp"
#include "repack/parse.hpp"
#include "repack/repack.hpp"
#include "utils/filepath_utils.hpp"
#include "utils/json_utils.hpp"
#include "utils/thread_pool.hpp"
#include "utils/exceptions.hpp"

#include <cxxopts.hpp>
#include <iostream>
#include <string>
#include <thread>
#include <sstream>
#include <utility> // for std::pair

std::vector<std::pair<CodePoint, CodePoint>> parseAdditionalConversions(const std::string& input_string) {
    std::vector<std::pair<CodePoint, CodePoint>> conversions;

    std::stringstream ss(input_string);
    std::string conv;

    // split by `,`to get individual conv
    while (std::getline(ss, conv, ',')) {
        if (conv.empty()) 
            continue; 

        std::stringstream ss_child(conv);
        std::string src_hex_str, dst_hex_str;

        // 2. Split by Colon (`:`) to separate key and value
        if (std::getline(ss_child, src_hex_str, ':') && std::getline(ss_child, dst_hex_str, ':')) {
            try {
                // 3. Convert from Hex (Base 16) to Integer
                // std::stoi(str, nullptr, 16) handles the "0x" prefix automatically.
                int src = std::stoi(src_hex_str, nullptr, 16);
                int dst = std::stoi(dst_hex_str, nullptr, 16);
                
                // 4. Store the Pairs
                
                conversions.push_back(std::make_pair(CodePoint(src), CodePoint(dst)));

            } catch (const std::exception& e) {
                // Handle potential errors like invalid hex strings
                std::cerr << "Error converting hex string: " << e.what() 
                          << " (Src: " << src_hex_str << ", Dst: " << dst_hex_str << ")\n";
            }
        }
    }

    return conversions;
}

int main(int argc, char** argv)
{
    cxxopts::Options options("rextr", "rom extraction and repacking tool");

    options.add_options()
        ("e,extract", "do extraction", cxxopts::value<bool>()->implicit_value("true")->default_value("false"))
        ("r,repack", "do repacking", cxxopts::value<bool>()->implicit_value("true")->default_value("false"))
        ("c,conversion", "code point conversion file for extraction/repacking", cxxopts::value<std::string>())
        ("threads", "maximum threads", cxxopts::value<int>()->default_value("4"))
        ("raws", "raw files", cxxopts::value<std::vector<std::string>>())
        ("cjk_only", "extract double bytes characters only", cxxopts::value<bool>()->implicit_value("true")->default_value("true"))
        ("a,additional_conversion", "e.g. 0x0a:0x0a,0xff:0xff",  cxxopts::value<std::string>()->default_value("0x0a:0x0a"))
        ("h,help", "Print usage")
    ;

    options.positional_help("<raw files>");
    options.parse_positional({"raws"});

    auto result = options.parse(argc, argv);

    if (result.count("help")) {
      std::cout << options.help() << std::endl;
      exit(0);
    }

    if ( (result.count("extract") == 0 && result.count("repack")) || \
         (result.count("extract") && result.count("repack")) ) {
        std::cout << "Please specify one operation(extract or repack)." << std::endl;
        exit(0);
    }

    int threads = result["threads"].as<int>();
    ThreadPool thread_pool(threads);
    std::vector<std::future<void>> results;

    std::vector<std::string> raws = result["raws"].as<std::vector<std::string>>();

    if (result.count("extract")) {
        Encoding enc;
        auto conversion_filepath = result["conversion"].as<std::string>();

        if (conversion_filepath.empty()) 
            enc = getDefaultShiftJISEncoding();
        else
            enc = newEncoding(conversion_filepath);
        
        auto additional_convs = result["additional_conversion"].as<std::string>();
        if (!additional_convs.empty()) {
            auto convs = parseAdditionalConversions(additional_convs);
            for (auto &conv: convs) {
                enc.add(conv.first, conv.second);
            }
        }

        bool cjk_only = result["cjk_only"].as<bool>();

        for (auto raw: raws) {
            std::cout << raw <<std::endl;
            results.emplace_back(
                thread_pool.enqueue(
                    [raw, &enc, cjk_only] {
                        Scene scn = newSceneFromFile(raw, enc, cjk_only);
                        Json dumped = dumpScene(scn);
                        std::string dump_file_name = getDumpedFileName(raw);
                        writeJson(dumped, dump_file_name);

                        std::cout << "dumped to " << dump_file_name << ".\n";
                    }
                )
            );
        }

        thread_pool.wait_until_empty();
        thread_pool.wait_until_nothing_in_flight();

        for(auto& r: results)
            r.get();
    }

    if (result.count("repack")) {
        auto conversion_filepath = result["conversion"].as<std::string>();
        if (conversion_filepath.empty()) 
            throw UnexpectedError("A code point conversion is necessary for repacking.");
        
        Encoding enc = newEncoding(conversion_filepath);

        for (auto& raw: raws) {
            results.emplace_back(
                thread_pool.enqueue(
                    [raw, &enc] () {
                        std::string dump_file_name = getDumpedFileName(raw);
                        Json translated_scn_json = parseJson(dump_file_name);
                        RepackScene translated_scn = parseRepackScene(translated_scn_json);
                        std::ofstream output_stream(raw);
                        repack(
                            translated_scn, 
                            enc,
                            raw,
                            output_stream
                        );
                    }
                )
            );
        }

        thread_pool.wait_until_empty();
        thread_pool.wait_until_nothing_in_flight();

        for(auto& r: results)
            r.get();
    }

    return 0;
}
