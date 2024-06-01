import json

# return str
def toStr(jsonObj):
    return json.dumps(jsonObj, ensure_ascii=False, indent=4)

# return jsonDict
def readJsonAsDict(jsonFile):
    with open(jsonFile, 'r', encoding='utf-8') as file:
        parsed_json = json.load(file)
    return parsed_json

# void 
def writeJsonDict(jsonDict, jsonFile):
    with open(jsonFile, 'w', encoding='utf-8') as file:
        json.dump(jsonDict, file, ensure_ascii=False, indent=4)
