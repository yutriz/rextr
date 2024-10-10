import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os

GEMINIKEY = os.getenv('GEMINIAPI')
genai.configure(api_key=GEMINIKEY)

censor_none = {
    HarmCategory.HARM_CATEGORY_HARASSMENT:  HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_HATE_SPEECH:  HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
}


"""
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

Models:
    models/gemini-1.0-pro
    models/gemini-1.0-pro-001
    models/gemini-1.0-pro-latest
    models/gemini-1.0-pro-vision-latest
    models/gemini-1.5-flash
    models/gemini-1.5-flash-001
    models/gemini-1.5-flash-latest
    models/gemini-1.5-pro
    models/gemini-1.5-pro-001
    models/gemini-1.5-pro-latest
    models/gemini-pro
    models/gemini-pro-vision
"""

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest",
                              safety_settings=censor_none)


# model = genai.GenerativeModel('gemini-1.5-flash')
# response = model.generate_content("What is the meaning of life?")
# print(response.text)

def gemini_translate(src_str, dst_lang):
    prompt_warmup = f"""
    You are a professional translator who is proficient in Japanese and Chinese.
    And I am translating games of Summon Night series. 
    I will give you a paragraph in japanese, and you will read the sentences sentence by sentence,
    then translate them into accurate and understandable {dst_lang} paragraph
    Don't make any explanation, translation is the only thing I want.
    """

    prompt_example = ''
    if dst_lang == 'en':
        prompt_example = f"""
        input: ホントですかぁ？
        output: really? 
        """
    if dst_lang == 'zh':
        prompt_example = f"""
        input: ホントですかぁ？
        output: 真的吗? 
        """

    prompt_text = f"""
    Let's begin !
    Original Paragraph: {src_str}
    
    Your Translation:
    """
    response = model.generate_content(prompt_warmup+prompt_example+prompt_text,
                                      safety_settings=censor_none)
    
    return response.text

