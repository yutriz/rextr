import tl.tgemini as tgemini
import tl.tgoogle as tgoogle
import tl.tdeepl as tdeepl
import tl.json_parse as jp

import os 
import time
import argparse
import wrapper

request_interval = 2

# return: string
def preprocess(str, removeNewline=True):
    ret = str
    # better remove 
    if removeNewline:
        ret = ret.replace('\n', '')
    return ret

def rename(filename):
    root, ext = os.path.splitext(filename)
    return root + ".mtl.json"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="input json file")
    parser.add_argument("-e", "--engine", default="deepl", help="translate engine: google, gemini, deepl")
    parser.add_argument("-l", "--lang", default="zh", help="en/zh/all")
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    args = parser.parse_args()
    return args

# return jsonDict
def translate(jsonFile, tl_func, dst_lang='zh', verbose=False):
    assert(dst_lang == 'all' or dst_lang=='en' or dst_lang=='zh')
    
    jsonDict = jp.readJsonAsDict(jsonFile)
    print('curretn file: ', jsonFile)
    print('total objects: ', len(jsonDict['blocks']))

    newJsonFile = rename(jsonFile)
    count = 0
    for i in jsonDict["blocks"]:
        src_str = preprocess(i["orig_text"])
        # resume 
        if (dst_lang=='all' or dst_lang=='en') and len(i["translated_text"])==0:
            i["translated_text"] = wrapper.wrapper_en(tl_func(src_str, 'en-us'))
        if (dst_lang=='all' or dst_lang=='zh') and len(i["translated_text_zh"])==0:
            i["translated_text_zh"] = wrapper.wrapper_zh(tl_func(src_str, 'zh'))
        # verbose
        if verbose:
            print("ja:", i["orig_text"])
            print("en:", i["translated_text"])
            print("zh:", i["translated_text_zh"])
        count = count + 1
        print("{:03d}/{:03d} done".format(count, len(jsonDict['blocks'])))
        jp.writeJsonDict(jsonDict,  newJsonFile)
        time.sleep(request_interval)
    return jsonDict

# return jsonDict
# list<str> tl_func_bulk(list<str> orig_texts, string dst_lang)
# def translate_bulk(jsonFile, target_lang, tl_func_bulk, remove_newline=False, do_wrap=False):
#     # print info
#     jsonDict = jp.readJsonAsDict(jsonFile)
#     print('curretn file: ', jsonFile)
#     blk_len = len(jsonDict['blocks'])
#     print('total objects: ', blk_len)

#     for i in range(0, blk_len, 30):
#         orig_texts = []
#         end = min(i+30, blk_len)
#         for j in range(i, end):
#             orig_text = removeNewline(jsonDict['blocks'][j]['orig_text'], remove_newline)
#             orig_texts.append(orig_text)
        
#         # request
#         # why tl_result is a string ! ?
#         time.sleep(interval)
#         tl_result = tl_func_bulk(orig_texts, target_lang)
#         tl_result= json.loads(tl_result) 
#         for k in range(0, 30):
#             jsonDict['blocks'][i+k]['translated_text'] = wrapper(tl_result[k], do_wrap)

#         # visual ?
#         print(tl_result)
        
#         # write every bulk request  
#         jp.writeJsonDict(jsonDict, rename(jsonFile))
#     return jsonDict

if __name__=="__main__":
    args = parse_args()
    jsonFile = args.input
    lang = args.lang
    vbs = args.verbose
    engine = args.engine

    tl_func = tdeepl.deepl_translate
    if engine == "google":
        tl_func = tgoogle.google_translate
    elif engine == "gemini":
        tl_func = tgemini.gemini_translate
    elif engine == "deepl":
        tl_func = tdeepl.deepl_translate

    jsonDict = translate(jsonFile, tl_func, dst_lang=lang, verbose=vbs)
    jp.writeJsonDict(jsonDict, rename(jsonFile))
