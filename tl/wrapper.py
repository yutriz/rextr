import textwrap

def wrapper_en(str, width=20):
    return textwrap.fill(str, width=width)

def wrapper_zh(str, width=10):
    return textwrap.fill(str, width=width)