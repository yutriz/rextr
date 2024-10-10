import deepl
import os

DEEPLKEY = os.getenv('DEEPLAPIKEY')
translator_deepl = deepl.Translator(DEEPLKEY)

# todo: add glossary 
def deepl_translate(src_str, dst_lang):
    return translator_deepl.translate_text(src_str, 
                                           source_lang='ja', 
                                           target_lang=dst_lang,
                                           preserve_formatting=True,
                                           formality='prefer_less'
                                           ).text


