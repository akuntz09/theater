import dictScene
import yahooScene
import sys
import yahoo
from pymongo import Connection
import urban
import dict


global conn
conn = Connection().Theater
global database
database = conn.yahoo


class Act:
	def __init__(self,word, numActors, scenes, yahooEmotions):
		self.word = word
		self.numActors = numActors
		self.scenes = scenes
		self.yahooEmotions = yahooEmotions
		
		self.usedDictWords = []
		self.usedYahooWords = []
		self.finalScript = []
		
		self.mostRecentDict = None
		
		for scene in scenes:
			if scene[0] == 'dict' :
				self.mostRecentDict = self.addDictScene('dict', self.word, 1, 3, scene[1])
			if scene[0] == 'urban':
				self.mostRecentDict = self.addDictScene('urban', self.word, 1 ,3, scene[1])
			if scene[0] == 'yahoo':
				self.addYahooScene(self.word, 3, 3)
			if scene[0] == 'related':
				self.addRelatedScene(self.mostRecentDict, scene[1])
				
			
			
	def addYahooScene(self, word, numQuestions, numAnswers):
		yScene = yahooScene.YahooScene(replaceSpace(word), numQuestions, numAnswers, self.yahooEmotions, self.numActors)
		yScene.makeScript()
		self.usedYahooWords.append(replaceSpace(word))
		#print 
		for line in yScene.script:
			self.finalScript.append(line)
		return yScene
		
			
	def addRelatedScene(self, dict, emotion):
		sortedRelated = dict.bestRelatedWord(emotion)
		print sortedRelated
		yScene = self.getBestRelated(sortedRelated, self.numActors)
		if yScene:
			yScene.makeScript()
			for line in yScene.script:
				self.finalScript.append(line)
			return yScene
		
	def addDictScene(self,type, word, numDefs, numRelated, emotion):
		dict = dictScene.DictionaryScene(type, replacePlus(word), self.numActors)
		
		if not dict.defs and dict.relatedWords and dict.relatedWords[0] == word:
			word = dict.relatedWords[0][:-1]
			dict = dictScene.DictionaryScene('dict', dict.relatedWords[0][:-1], self.numActors)
		
		self.usedDictWords.append(word)
		dict.addDefToScript(numDefs)
		dict.addRelatedToScript(numRelated, emotion)
		dict.makeScript()
		for line in dict.script:
			self.finalScript.append(line)
			
		return dict


	def getBestRelated(self, words, numActors):
		if not words:
			return
		for tuple in words:
			if replaceSpace(tuple[0]) not in self.usedYahooWords:
				print tuple[0]
				yScene = yahooScene.YahooScene(dictScene.replaceSpace(tuple[0]), 2, 2, self.yahooEmotions, numActors)
				print "Questions for "+tuple[0] + ' = ' + str(yScene.questions.count())
				if yScene.questions.count() > 0:
					print "Related Word: " + tuple[0]
					self.usedYahooWords.append(replaceSpace(tuple[0]))
					return yScene
	
	def makeFile(self):
		file = open('scripts/'+self.word+'.html','w')
		for line in self.finalScript:
			file.write(line)

def replaceSpace(word):
	return word.replace(' ','+')
	
def replacePlus(word):
	return word.replace('+',' ')

'''	
def getBestRelated(words, numActors):
	if not words:
		return
	for tuple in words:
		yScene = yahooScene.YahooScene(dictScene.replaceSpace(tuple[0]), 2, 2, ['positiveAnswers', 'negativeAnswers'], numActors)
		if yScene.questions.count() > 0:
			print "Related Word: " + tuple[0]
			return yScene

def makeFile(script, name):
	file =open(name+'.html','w')
	for line in script:
		file.write(line)
			
def main():

	finalScript = []

	word = sys.argv[1]
	word = replacePlus(word)
	numActors = sys.argv[2]
	dict = dictScene.DictionaryScene('dict', word, numActors)
	if not dict.defs and dict.relatedWords and dict.relatedWords[0] == word:
		dict = dictScene.DictionaryScene('dict', dict.relatedWords[0][:-1], numActors)
	dict.addDefToScript(1)
	dict.addRelatedToScript(3)
	dict.makeScript()
	for line in dict.script:
		finalScript.append(line)
	
	print "\nFinding Conversations\n"
	yScene = yahooScene.YahooScene(replaceSpace(word), 2, 2, ['positiveAnswers', 'negativeAnswers'], numActors)
	yScene.makeScript()
	#print 
	for line in yScene.script:
		finalScript.append(line)
		
	
	sortedRelated = dict.bestRelatedWord()
	
	secondYahoo = getBestRelated(sortedRelated, 3)	
	if secondYahoo:
		secondYahoo.makeScript()
		for line in secondYahoo.script:

			finalScript.append(line)
	
	
	print "\nUrban Dictionary\n"
	
	dict2 = dictScene.DictionaryScene('urban', word, numActors)
	dict2.addDefToScript(1)
	dict2.addRelatedToScript(3)
	dict2.makeScript()
	
	for line in dict2.script:
		finalScript.append(line)
	
	
	
	
	sortedRelated2 = dict2.bestRelatedWord()
	thirdYahoo = getBestRelated(sortedRelated2, 3)
	thirdYahoo.makeScript()
	
	for line in thirdYahoo.script:
		finalScript.append(line)
		
	
	makeFile(finalScript, sys.argv[1])
		
'''

if __name__ == '__main__':
	#main()
	act = Act(sys.argv[1], sys.argv[2], [['dict', 'uniqueScore'],['yahoo'],['related','uniqueScore'],['urban', 'uniqueScore'],['related','uniqueScore']],['lengthAnswers', 'googleAnswers'])
	act.makeFile()
	