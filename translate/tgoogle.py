from .google_trans_new.google_trans_new import google_translator

translatorG = google_translator()  

def google_translate(src_str, dst_lang):
    return translatorG.translate(src_str, lang_src='ja', lang_tgt=dst_lang) 

# dont use 
def google_translate_bulk(src_str, dst_lang):
    return translatorG.translate(src_str, lang_src='ja', lang_tgt=dst_lang) 
    