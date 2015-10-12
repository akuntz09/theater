from pymongo import Connection, DESCENDING, ASCENDING
import urllib
from xml.dom import minidom
import yahoo

global dictionaryID
dictionaryID="b8e03a99-3d4b-4524-a34a-e10f2f115853"
global dictionaryURL
dictionaryURL = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/%s?key=" + dictionaryID

global conn
conn = Connection().Theater
global database
database = conn.definition

def getDefinitions(word):
	definitions = database.find({'word':word})
	if definitions.count() == 0:
		url = dictionaryURL % word
		
		xml = minidom.parse(urllib.urlopen(url))
		entrylist = xml.getElementsByTagName('entry')
		
		
		definitionList = []
		relatedList = []
		
		relatedCount = 0
		
		for entry in entrylist:
			if word+"[" in entry.attributes['id'].value:
				definition = entry.getElementsByTagName("def")[0]
				for dt in definition.getElementsByTagName("dt"):
					dt=clean_definition_text(dt.childNodes[0].nodeValue)
					for newtext in dt.split(":"):
						if len(newtext) > 5:
							defstruct = {}
							defstruct['word'] = word
							defstruct['definition'] = yahoo.makeText(newtext, 'definition')
							definitionList.append(defstruct)
							#print newtext
							#print
			elif word in entry.attributes['id'].value:
				relatedList.append(entry.attributes['id'].value)
				
		info = {}
		info['definitions'] = definitionList
		info['relatedWords'] = relatedList
		info['word'] = word
		database.insert(info)
		definitions = database.find({'word':word})

	return definitions
	

def clean_definition_text (text):
	text = text.strip(":")
	text = text.strip(" ")
	return text							

if __name__ == '__main__':
	cursor = getDefinitions('hammer')
	for word in cursor:
		defs = word['definitions']
		print defs