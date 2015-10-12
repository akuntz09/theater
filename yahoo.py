import feedparser
import urllib2
from bs4 import BeautifulSoup
import re
import string
import sys
import pickle
import operator
import json
from pymongo import Connection, DESCENDING, ASCENDING
import urllib



global conn
conn = Connection().Theater
global database
database = conn.yahoo

global negativeWords
negativeWords = [line.strip() for line in open('negative.txt','r')]
global positiveWords
positiveWords = [line.strip() for line in open('positive.txt','r')]

negativeSet = set(negativeWords)
positiveSet = set(positiveWords)

global pronouns
pronouns=("i","me", "us","my","our","we","his","her","he","she","i've","we've","she's","he's")
pronounSet=set(pronouns)

global relationships
relationships=('boy','girl','friend','friends','lover','wife','husband','mom','dad','mother','father','son','daugther','kid','child','parent','parents','clidren','boss','buddy','bf','bff','gf')
relationshipSet=set(relationships)

global profanity
profanity=('sex','bum', 'shitfaced', 'fucked', 'plastered', 'wasted', 'hammered', 'cheating', 'sex', 'lust','thrust', 'pelvic','breast', 'breasts','anus','arse','arsehole','ass','ass-hat','ass-jabber','ass-pirate','assbag','assbandit','assbanger','assbite','assclown','asscock','asscracker','asses','assface','assfuck','assfucker','assgoblin','asshat','asshead','asshole','asshopper','assjacker','asslick','asslicker','assmonkey','assmunch','assmuncher','assnigger','asspirate','assshit','assshole','asssucker','asswad','asswipe','axwound','bampot','bastard','beaner','bitch','bitchass','bitches','bitchtits','bitchy','blow job','blowjob','bollocks','bollox','boner','brotherfucker','bullshit','bumblefuck','butt plug','butt-pirate','buttfucka','buttfucker','camel toe','carpetmuncher','chesticle','chinc','chink','choad','chode','clit','clitface','clitfuck','clusterfuck','cock','cockass','cockbite','cockburger','cockface','cockfucker','cockhead','cockjockey','cockknoker','cockmaster','cockmongler','cockmongruel','cockmonkey','cockmuncher','cocknose','cocknugget','cockshit','cocksmith','cocksmoke','cocksmoker','cocksniffer','cocksucker','cockwaffle','coochie','coochy','coon','cooter','cracker','cum','cumbubble','cumdumpster','cumguzzler','cumjockey','cumslut','cumtart','cunnie','cunnilingus','cunt','cuntass','cuntface','cunthole','cuntlicker','cuntrag','cuntslut','dago','damn','deggo','dick','dick-sneeze','dickbag','dickbeaters','dickface','dickfuck','dickfucker','dickhead','dickhole','dickjuice','dickmilk','dickmonger','dicks','dickslap','dicksucker','dicksucking','dicktickler','dickwad','dickweasel','dickweed','dickwod','dike','dildo','dipshit','doochbag','dookie','douche','douchebag','douchewaffle','dumass','dumb ass','dumbass','dumbfuck','dumbshit','dumshit','dyke','fag','fagbag','fagfucker','faggit','faggot','faggotcock','fagtard','fatass','fellatio','feltch','flamer','fuck','fuckass','fuckbag','fuckboy','fuckbrain','fuckbutt','fuckbutter','fucked','fucker','fuckersucker','fuckface','fuckhead','fuckhole','fuckin','fucking','fucknut','fucknutt','fuckoff','fucks','fuckstick','fucktard','fucktart','fuckup','fuckwad','fuckwit','fuckwitt','fudgepacker','gay','gayass','gaybob','gaydo','gayfuck','gayfuckist','gaylord','gaytard','gaywad','goddamn','goddamnit','gooch','gook','gringo','guido','handjob','hard on','heeb','hell','ho','hoe','homo','homodumbshit','honkey','humping','jackass','jagoff','jap','jerk off','jerkass','jigaboo','jizz','jungle bunny','junglebunny','kike','kooch','kootch','kraut','kunt','kyke','lardass','lesbian','lesbo','lezzie','mcfagget','mick','minge','mothafucka','mothafuckin','motherfucker','motherfucking','muff','muffdiver','munging','nigaboo','nigga','nigger','niggers','niglet','nutsack','paki','panooch','pecker','peckerhead','penis','penisbanger','penisfucker','penispuffer','piss','pissed','pissflaps','polesmoker','pollock','poon','poonani','poonany','poontang','porchmonkey','porchmonkey','prick','punanny','punta','pussies','pussy','pussylicking','puto','queef','queer','queerbait','queerhole','renob','rimjob','ruski','sandnigger','schlong','scrote','shit','shitass','shitbag','shitbagger','shitbrains','shitbreath','shitcanned','shitcunt','shitdick','shitface','shitfaced','shithead','shithole','shithouse','shitspitter','shitstain','shitter','shittiest','shitting','shitty','shiz','shiznit','skank','skeet','skullfuck','slut','slutbag','smeg','snatch','spic','spick','splooge','spook','suckass','tard','testicle','thundercunt','tit','titfuck','tits','tittyfuck','twat','twatlips','twats','twatwaffle','unclefucker','vag','vagina','vajayjay','vjayjay','wank','wankjob','wetback','whore','whorebag','whoreface','wop')
profanitySet=set(profanity)

global stops
stops=("a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "i", "if", "in", "into", "is", "it", "its", "of", "off", "on", "or", "than", "that", "the", "to", "with")

global freqs
freqs = pickle.load(open('wordFreq.p', 'rb'))

global ranges
ranges={}
ranges["title"]=(1,30)
ranges["question"]=(5,100)
ranges["definition"]=(8,30)
ranges["answer"]=(5,160)
ranges["use"]=(8,30)

def getWordScore(word, emotion):
	sortTerm = 'question.'+emotion
	cursor = database.find({'word':word}).sort(sortTerm, DESCENDING)
	if cursor.count() > 0:
		for doc in cursor:
			val = doc['question'][emotion]
			if val == 0:
				continue
			return val
	else:
		return 0

def getQuestions(word):
	for i in range(1,5):
		try:
			a = 'https://answers.yahoo.com/rss/search?p='+word+'&s='+str(i)
			print a
			d = feedparser.parse(a)
			for entry in d.entries:
				try:
					link = entry['link']
					print entry['title']
					linkCursor = database.find({'link':link, 'word':word})
					if linkCursor.count() == 0:
						post = makeQuestion(link, word)
						print post['title']['text']
						database.insert(post)
						print "inserted"
					else:
						print 'skipped'
				except urllib2.URLError:
					print "error"
					continue
				except UnicodeDecodeError:
					print 'Unicode'
					continue
				print
		except urllib2.URLError:	
			print "Error!"
			continue



def makeQuestion(link, word):
	soup = BeautifulSoup(urllib2.urlopen(link).read())
	post = {}
	
	post['link'] = link
	post['word'] = word
	
	title = str(soup.find('h1')).encode('ascii','ignore').lower()
	title = remove_tags(title)
	
	post['title'] = makeText(title,'title')
	
	
	text = str(soup.find('span',{'class':'ya-q-text'})).encode('ascii','ignore').lower()
	text = remove_tags(text)
	post['question'] = makeText(text, 'question')

	post['answers'] = getAnswers(link+"&page=1", [], soup)
		
	rankQuestion(post)
	
	
	print len(post['answers'])
	return post

def getAnswers(link, allAnswers = [], soup = None):
	try:
		print "getting answers from " + link
	
		if not soup:
			soup = BeautifulSoup(urllib2.urlopen(link).read())
	
	
		answers = soup.findAll('span', {'class':'ya-q-full-text'})
		for answer in answers:
			answer = str(answer).encode('ascii','ignore').lower()
			answer = remove_tags(answer)
			if "http://" in answer or "www." in answer:
				continue
			answer = makeText(answer, 'answer')
			if answer not in allAnswers:
				allAnswers.append(answer)
			else:
				print "dupe"
	
		links = soup.findAll('a', {'class':'Clr-bl'})
		if links:
			next = links[-1]
			nextLink = next['href']
	
			if 'page' in nextLink:
				oldNum = link.split('=')[-1]
				num = nextLink.split('=')[-1]
				#strNum = num.encode('ascii','ignore')
				#print type(strNum)
				if num != oldNum and num != 'O':
					nextLink = link.split('page=')[0]+'page='+str(num)
					getAnswers(nextLink, allAnswers)
			
		return allAnswers
	except:
		print 'answer error'
		return allAnswers
	
	
	
	
def getGoodQuestions(emotion, word):
	questions = database.find({'goodQuestion':True, 'word':word}).sort(emotion, DESCENDING)
	return questions
	
def sortAnswers(answers, emotion):
	sorted = sorted(answers, key=lambda k: k[emotion])
	return sorted

def rankQuestion(post):
	post['goodAnswers'] = []
	post['dirtyAnswers'] = []
	post['snarkyAnswers'] = []
	post['answerScore'] = 0
	post['questionScore'] = 0
	post['titleScore'] = 0
	
	post['goodTitle'] = post['title']['personalBool'] and post['title']['fits']
	post['goodQuestion'] = post['question']['personalBool'] and post['question']['fits']
		
	post['goodAnswers'] = filterGoodAnswers(post['answers'])
	post['dirtyAnswers'] = filterDirtyAnswers(post['answers'])
	post['snarkyAnswers'] = filterSnarkyAnswers(post['answers'])
	post['positiveAnswers'] = filterPositiveAnswers(post['answers'])
	post['negativeAnswers'] = filterNegativeAnswers(post['answers'])
	post['uniqueAnswers'] = filterUniqueAnswers(post['answers'])
	post['lengthAnswers'] = filterLengthAnswers(post['answers'])
	post['googleAnswers'] = filterGoogleAnswers(post['answers'])
	

	
	post['numGoodAnswers'] = len(post['goodAnswers'])
	post['numDirtyAnswers'] = len(post['dirtyAnswers'])
	post['numSnarkyAnswers'] = len(post['snarkyAnswers'])
	post['numPositiveAnswers'] = len(post['positiveAnswers'])
	post['numNegativeAnswers'] = len(post['negativeAnswers'])
	
	
		
	post['answerScore'] = len(post['goodAnswers'])+len(post['dirtyAnswers'])+(len(post['snarkyAnswers']*2))
	post['questionScore'] = post['question']['dirtyScore']+post['question']['snarkyScore']
	post['titleScore'] = post['title']['dirtyScore']+post['title']['snarkyScore']
	return post

def filterGoogleAnswers(answers):
	filtered = []
	for answer in answers:
		if answer['uniqueScore'] < 0 and answer['fits']:
			filtered.append(answer)
	return filtered		

def filterLengthAnswers(answers):
	filtered = []
	for answer in answers:
		if answer['lengthScore'] > 5 and answer['fits']:
			filtered.append(answer)
	return filtered

def filterUniqueAnswers(answers):
	filtered = []
	for answer in answers:
		if answer['uniqueScore'] < 0 and answer['fits']:
			filtered.append(answer)
	return filtered
		
def filterPositiveAnswers(answers):
	filtered = []
	for answer in answers:
		if answer['positiveScore'] > 0 and answer['fits']:
			filtered.append(answer)
	return filtered

def filterNegativeAnswers(answers):
	filtered = []
	for answer in answers:
		if answer['negativeScore'] > 0 and answer['fits']:
			filtered.append(answer)
	return filtered	
	
def filterGoodAnswers(answers):
	filtered = []
	for answer in answers:
		if answer['fits'] and (answer['personalBool'] or answer['relationshipBool']):
			filtered.append(answer)
	return filtered
	
def filterDirtyAnswers(answers):
	filtered = []
	for answer in answers:
		if answer['length'] <25 and answer['dirtyScore'] >1:
			filtered.append(answer)
	return filtered
	
def filterSnarkyAnswers(answers):
	filtered = []
	for answer in answers:
		if answer['length'] <15 and answer['length'] >2:
			filtered.append(answer)
	return filtered


def makeText(givenText,type):
	text = {}
	
	text['text'] = givenText
	text['type'] = type
	
	clean = givenText
	for char in ',;:!?\n\t.\(){}[]':
		clean = clean.replace(char,' ')
	clean=clean.replace("  "," ")

	text['clean'] = clean
	text['tokens'] = clean.split()
	text['length'] = len(text['tokens'])
	#text['tokenSet'] = set(text['tokens'])
	text['stopped'] = remove_stops(text)
	text['stops'] = just_stops(text)
	text['personalBool'] = personal_test(text)
	text['dirtyScore'] = dirty_test(text)
	text['snarkyScore'] = set_snarky(text)
	text['fits'] = range_test(text)
	text['relationshipBool'] = relationship_test(text)
	text['positiveScore'] = positive_test(text)
	text['negativeScore'] = negative_test(text)
	text['uniqueScore'] = unique_test(text)
	text['lengthScore'] = length_test(text)
	text['googleScore'] = google_test(text)
	
	return text
	
def google_test(text):
	try:
		query = urllib.urlencode({'q': text['clean']})
		url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
		search_response = urllib.urlopen(url)
		search_results = search_response.read()
		results = json.loads(search_results)
		data = results['responseData']
		print text['clean']
		if 'estimatedResultCount' in data['cursor'].keys():
			print data['cursor']['estimatedResultCount']
			print
			return int(data['cursor']['estimatedResultCount']) * -1
		else:
			print 0
			print
			return 0
	except TypeError:
		print results
		print text['clean']
		print "Type Error"
		return 0

def length_test(text):
	length = 0.0
	for word in text['stopped']:
		length += len(word)
	if len(text['stopped']) > 0:
		return length/len(text['stopped'])
	return 0

def unique_test(text):
	unique = 0
	total = 0.0
	for word in text['stopped']:
		if word in freqs:
			score = int(freqs[word])
			if score != 0:
				total += 1
			
			unique -= int(freqs[word])
	if total < 5:
		return 0
	return unique/total

def positive_test(text):
	return len(positiveSet.intersection(set(text['tokens'])))
	
def negative_test(text):
	return len(negativeSet.intersection(set(text['tokens'])))

def relationship_test(text):
	text['relationshipN'] = len(relationshipSet.intersection(set(text['tokens'])))
	return text['relationshipN'] > 0

def range_test(text):
	myRange=ranges[text['type']]
	return len(text['tokens']) >= myRange[0] and len(text['tokens']) <= myRange[1] 

def personal_test(text):
	text['personalN'] = len(pronounSet.intersection(set(text['tokens'])))
	return text['personalN'] > 0

def dirty_test(text):
	return len(profanitySet.intersection(set(text['tokens'])))

def	 set_snarky(text):
	if text['length'] < 12 and text['length'] > 2:
		return 1
	else:
		return 0

def remove_stops(text):
	tight=[]
	for token in text['tokens']:
		if not token in stops:
			tight.append(token)
	return tight
	
def just_stops(text):
	myStops=[]
	for token in text['tokens']:
		if token in stops:
			myStops.append(token)
	return myStops

	
	
def remove_tags(s):
	tag = False
	quote = False
	out = ""
	for c in s:
		if c == '<' and not quote:
			tag = True
		elif c == '>' and not quote:
			tag = False
		elif (c == '"' or c == "'") and tag:
			quote = not quote
		elif not tag:
			out = out + c
	return out		 
	
if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf-8')
	#getQuestions("science+fiction")
	#getGoodQuestions('numSnarkyAnswers', 'sexy')