from pymongo import Connection, DESCENDING, ASCENDING
import urllib
from xml.dom import minidom
import yahoo
import json

global conn
conn = Connection().Theater
global database
database = conn.urban

def getDefinitions(given):
    definitions = database.find({'word':given})
    print definitions.count() == 0
    if definitions.count() == 0:
        print 'here'
        url = "http://api.urbandictionary.com/v0/define?term=%s" % given

        definitionList = []
        similars=[]

        jsondata = json.load(urllib.urlopen(url))
    
        for word in jsondata["tags"]:
            similars.append(word)

        print jsondata['list']
        for element in jsondata["list"]:
            definition={}
            defText=clean_string(element["definition"])
            useText=clean_string(element["example"])
            if not multiple_defs(defText) and not useText == defText:
                definition["definition"]=yahoo.makeText(defText, "definition")
                definition["use"]=yahoo.makeText(clean_string(useText), "use")
                if definition["definition"]["fits"]:
                    definitionList.append(definition)
                
        info = {}
        info['definitions'] = definitionList
        info['relatedWords'] = similars
        info['word'] = given
        database.insert(info)
        definitions = database.find({'word':given})

    return definitions
    

def clean_string(string):
    string= string.encode('ascii', 'ignore')
    for char in '[](){}\n\r':  
        string = string.replace(char,' ')
    return string
    
def multiple_defs(string):
    if "1." in string:
        return True         

if __name__ == '__main__':
    cursor = getDefinitions('sex')
    print cursor.count()
    for word in cursor:
        defs = word['definitions']
        for a in defs:
            print a['definition']['text']
            print a['use']['text']
            print