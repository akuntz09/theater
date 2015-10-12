import yahoo

from pymongo import Connection, DESCENDING, ASCENDING
global conn
conn = Connection().Theater
global database
database = conn.yahoo


class YahooScene:
	def __init__(self,word, numQuestions, numAnswers, emotions, numPeople):
		self.numQuestions = int(numQuestions)
		self.word = word
		self.numAnswers = int(numAnswers)
		self.emotions = emotions
		
		self.numPeople = int(numPeople)
		self.speaker = 1
		self.questioner = None
		
		self.lines = []
		self.script = []
		
		questions = database.find({'word':word})
		
		if questions.count() == 0:
			print 'here'
			yahoo.getQuestions(word)
			
		self.questions = yahoo.getGoodQuestions('numSnarkyAnswers',self.word).limit(self.numQuestions)

		for question in self.questions:
			self.addQuestionToScript(question, self.emotions)
	
		
	def addAnswerToScript(self, question, emotion):
		answerList = question[emotion]
		sorter = emotion[:-7]+'Score'
		if sorter == 'goodScore':
			answerList = sorted(answerList, key=lambda k: k['dirtyScore'])
			anserList.reverse()
		else:
			answerList = sorted(answerList, key=lambda k: k[sorter])
			answerList.reverse()
		for i in range(len(answerList)):
			if answerList[i] not in self.lines:
				#answerList[i]['text'] = emotion  + " " + str(len(answerList))+ " " + answerList[i]['text']
				self.lines.append(answerList[i])
				break
				
	def addQuestionToScript(self, question, emotions):
		self.lines.append(question['title'])
		self.lines.append(question['question'])
		
		emotion = 0
		
		for i in range(self.numAnswers):
			if emotion == len(emotions):
				emotion = 0
			
			self.addAnswerToScript(question, emotions[emotion])
			emotion += 1
			
	
	def changeSpeaker(self):
		if self.speaker == self.numPeople:
			self.speaker = 1
		else:
			self.speaker += 1
	
	def speak(self, line, change = False):
		if line == '<br>':
			finalLine =  '<br>'
		else:
			finalLine = "<b>ACTOR " + str(self.speaker) + "</b>: " + line + "<br>"
			if change:
				self.changeSpeaker()
		return finalLine
	
	def makeScript(self):
		for line in self.lines:
			if line['type'] == 'title':
				finalLine = self.speak("QUESTION: " + line['text'])
				self.questioner = self.speaker
				self.script.append(finalLine)
			if line['type'] == 'question':
				finalLine = self.speak(line['text'], True)
				while self.speaker == self.questioner:
					self.changeSpeaker()
				self.script.append(line['text']+'<br>')
				self.script.append('<br>')
			if line['type'] == 'answer':
				finalLine = self.speak(line['text'], True)
				while self.speaker == self.questioner:
					self.changeSpeaker()
				self.script.append(finalLine)		
				self.script.append('<br>')
			
		
		


if __name__ == '__main__':
	scene = YahooScene("sexy",3,3,['positiveAnswers','snarkyAnswers'],3)
	scene.printScript()