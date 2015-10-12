from pymongo import Connection, DESCENDING, ASCENDING
import getCraigslist
global conn
conn = Connection().Theater

class Scene:
    	def __init__(self, source, length, location = None):

                self.location = location
                self.length = length

                if source == 'craigslist':
                        self.database = conn.allCraigslist

                self.lines = []
                for i in range(length):
                        if self.location:
                                self.lines.append(self.database.find({'city':self.location}))
                        else:
                                self.lines.append(self.database.find())

                self.script = []

        def createContrast(self,emotion, genderOfHigh, genderOfLow):
                for i in range(0,self.length,2):
                        self.lines[i] = self.database.find({emotion:{'$gt':0}, 'posterGender':genderOfHigh, 'lookingFor':genderOfLow,}).sort(emotion,DESCENDING)
                        self.lines[i+1] = self.database.find({emotion:{'$gt':0}, 'posterGender':genderOfLow, 'lookingFor':genderOfHigh}).sort(emotion,ASCENDING)


        def makeScript(self):
                script = []
                for i in range(self.length):
                        possibleLines = self.lines[i]
                        for line in possibleLines:
                                if line  not in script:
                                        script.append(line)
                                        break
                self.script = script
                return script

        def shortenLines(self, script, emotion, length, direction):
                newScript = []
                for line in script:
                        text = line['text']
                        allSentences = text.split('.')
                        if len(allSentences) <= length:
                                line['shortenedText'] = allSentences
                        bestSentences = ''
                        if direction == 'high':
                                bestSentencesScore = 0
                        elif direction == 'low':
                                bestSentencesScore = float('inf')

                        for i in range(len(allSentences)-length):
                                sentences = ''
                                for j in range(length):
                                        sentences += allSentences[i+j]
                                        sentences += '. '
                                cleaned = getCraigslist.makeClean(sentences)
                                tokens = cleaned.split()
                                if len(tokens)>0:
                                        score = len([i for i in tokens if i in emotion])/len(tokens)
                                        if (score >= bestSentencesScore and direction == 'high') or (score <= bestSentencesScore and direction == 'low'):
                                                bestSentences = sentences
                                                bestSentencesScore = score
                        line['shortenedText'] = bestSentences

        def printScript(self):
                for line in self.script:
                        print line['text']
                        print

        def printShortenedScript(self):
                for line in self.script:
                        if 'shortenedText' in line:
                                print line['shortenedText']
                                print
                                
if __name__ == '__main__':
        scene1 = Scene('craigslist', 8)
        scene1.createContrast('dirtyScore', 'm','w')
        scene1.makeScript()
        scene1.shortenLines(scene1.script,'dirtyScore',4,'high')
        scene1.printShortenedScript()
