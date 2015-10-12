from pymongo import Connection, DESCENDING, ASCENDING
import dict
import urban
import random
import yahoo 

global conn
conn = Connection().Theater

class DictionaryScene:
	def __init__(self, source, word, numPeople):
		self.word = word
		self.source = source
		if self.source == 'urban':
			self.database = conn.urban
		elif self.source == 'dict':
			self.database = conn.definition
		self.numPeople = int(numPeople)
		self.speaker = 1
		
		
		self.lines = []
		self.script = []
		
		defObject = self.database.find({'word':word})
		if defObject.count() == 0:
			if self.source == 'urban':
				self.defs = urban.getDefinitions(word)
			elif self.source == 'dict':
				self.defs = dict.getDefinitions(word)
		
		self.defObject = defObject.next()
		self.defs = self.defObject['definitions']
		self.relatedWords = self.defObject['relatedWords']
		
			
	def bestRelatedWord(self, emotion):
		scores = []
		for word in self.relatedWords:
			newWord = replaceSpace(word)
			cursor = conn.yahoo.find({'word':newWord})
		
			if cursor.count() == 0:
				yahoo.getQuestions(newWord)
	
			score = yahoo.getWordScore(newWord, emotion)
			scores.append((replacePlus(newWord), score))
		
		scores = sorted(scores, key=lambda x: x[1])
		scores.reverse()
		if scores:
			return scores
		
	def addDefToScript(self, numDefs):
		for i in range(numDefs):
			if i == len(self.defs):
				return
			
			firstDef = self.defs[i]['definition']
			self.lines.append(self.word + "!")
			self.lines.append('<br>')
		
			randomStopped = list(firstDef['stopped'])
			
			random.shuffle(randomStopped)
			for token in randomStopped:
				self.lines.append(token + "?")
			self.lines.append('<br>')
			self.lines.append(self.word + "?")
			self.lines.append('<br>')
			
			
			for token in firstDef['stops']:
				self.lines.append(token + "?")
			
			self.lines.append('<br>')
			self.lines.append(self.word + "?")
			self.lines.append('<br>')
		
			for token in firstDef['tokens']:
				self.lines.append(token)
			self.lines.append('<br>')
			
			self.lines.append(firstDef['text'])
			self.lines.append('<br>')
			
	def changeSpeaker(self):
		if self.speaker == self.numPeople:
			self.speaker = 1
		else:
			self.speaker += 1
		
	def speak(self, line):
		if line == '<br>':
			finalLine = '<br>'
		else:
			finalLine = "<b>ACTOR " + str(self.speaker) + "</b>: " + line + "<br>"
			self.changeSpeaker()
		return finalLine
		
			
	def makeScript(self):
		for line in self.lines:
			finalLine = self.speak(line)
			if finalLine:
				self.script.append(finalLine)

			
	def addRelatedToScript(self, num, emotion):
		orderedRelated = self.bestRelatedWord(emotion)
		print orderedRelated
		if orderedRelated and len(orderedRelated) >1:
			self.lines.append("RELATED WORDS!<br>")
			for i in range(num):
				if i == len(orderedRelated):
					return
				else:
					self.lines.append(orderedRelated[i][0])
			self.lines.append('<br>')
		
	

def replaceSpace(word):
	return word.replace(' ','+')
	
def replacePlus(word):
	return word.replace('+',' ')
		