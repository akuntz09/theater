import urllib2
from bs4 import BeautifulSoup
import re
import string
import sys
import pickle
import operator
from pymongo import Connection, DESCENDING, ASCENDING

reload(sys)
sys.setdefaultencoding('utf-8')

global conn
conn = Connection().Theater
global database
database = conn.chicagoCraigslist

global pronouns
pronouns=("i","me", "us","my","our","we","his","her","he","she","i've","we've","she's","he's")
pronounSet=set(pronouns)

global relationships
relationships=('boy','girl','friend','friends','lover','wife','husband','mom','dad','mother','father','son','daugther','kid','child','parent','parents','clidren','boss','buddy','bf','bff','gf')
relationshipSet=set(relationships)

global profanity
profanity=('sex','bum', 'shitfaced', 'fucked', 'plastered', 'wasted', 'hammered', 'cheating', 'sex', 'lust','thrust', 'pelvic','breast', 'breasts','anus','arse','arsehole','ass','ass-hat','ass-jabber','ass-pirate','assbag','assbandit','assbanger','assbite','assclown','asscock','asscracker','asses','assface','assfuck','assfucker','assgoblin','asshat','asshead','asshole','asshopper','assjacker','asslick','asslicker','assmonkey','assmunch','assmuncher','assnigger','asspirate','assshit','assshole','asssucker','asswad','asswipe','axwound','bampot','bastard','beaner','bitch','bitchass','bitches','bitchtits','bitchy','blow job','blowjob','bollocks','bollox','boner','brotherfucker','bullshit','bumblefuck','butt plug','butt-pirate','buttfucka','buttfucker','camel toe','carpetmuncher','chesticle','chinc','chink','choad','chode','clit','clitface','clitfuck','clusterfuck','cock','cockass','cockbite','cockburger','cockface','cockfucker','cockhead','cockjockey','cockknoker','cockmaster','cockmongler','cockmongruel','cockmonkey','cockmuncher','cocknose','cocknugget','cockshit','cocksmith','cocksmoke','cocksmoker','cocksniffer','cocksucker','cockwaffle','coochie','coochy','coon','cooter','cracker','cum','cumbubble','cumdumpster','cumguzzler','cumjockey','cumslut','cumtart','cunnie','cunnilingus','cunt','cuntass','cuntface','cunthole','cuntlicker','cuntrag','cuntslut','dago','damn','deggo','dick','dick-sneeze','dickbag','dickbeaters','dickface','dickfuck','dickfucker','dickhead','dickhole','dickjuice','dickmilk','dickmonger','dicks','dickslap','dicksucker','dicksucking','dicktickler','dickwad','dickweasel','dickweed','dickwod','dike','dildo','dipshit','doochbag','dookie','douche','douchebag','douchewaffle','dumass','dumb ass','dumbass','dumbfuck','dumbshit','dumshit','dyke','fag','fagbag','fagfucker','faggit','faggot','faggotcock','fagtard','fatass','fellatio','feltch','flamer','fuck','fuckass','fuckbag','fuckboy','fuckbrain','fuckbutt','fuckbutter','fucked','fucker','fuckersucker','fuckface','fuckhead','fuckhole','fuckin','fucking','fucknut','fucknutt','fuckoff','fucks','fuckstick','fucktard','fucktart','fuckup','fuckwad','fuckwit','fuckwitt','fudgepacker','gay','gayass','gaybob','gaydo','gayfuck','gayfuckist','gaylord','gaytard','gaywad','goddamn','goddamnit','gooch','gook','gringo','guido','handjob','hard on','heeb','hell','ho','hoe','homo','homodumbshit','honkey','humping','jackass','jagoff','jap','jerk off','jerkass','jigaboo','jizz','jungle bunny','junglebunny','kike','kooch','kootch','kraut','kunt','kyke','lardass','lesbian','lesbo','lezzie','mcfagget','mick','minge','mothafucka','mothafuckin','motherfucker','motherfucking','muff','muffdiver','munging','nigaboo','nigga','nigger','niggers','niglet','nutsack','paki','panooch','pecker','peckerhead','penis','penisbanger','penisfucker','penispuffer','piss','pissed','pissflaps','polesmoker','pollock','poon','poonani','poonany','poontang','porchmonkey','porchmonkey','prick','punanny','punta','pussies','pussy','pussylicking','puto','queef','queer','queerbait','queerhole','renob','rimjob','ruski','sandnigger','schlong','scrote','shit','shitass','shitbag','shitbagger','shitbrains','shitbreath','shitcanned','shitcunt','shitdick','shitface','shitfaced','shithead','shithole','shithouse','shitspitter','shitstain','shitter','shittiest','shitting','shitty','shiz','shiznit','skank','skeet','skullfuck','slut','slutbag','smeg','snatch','spic','spick','splooge','spook','suckass','tard','testicle','thundercunt','tit','titfuck','tits','tittyfuck','twat','twatlips','twats','twatwaffle','unclefucker','vag','vagina','vajayjay','vjayjay','wank','wankjob','wetback','whore','whorebag','whoreface','wop')
profanitySet = set(profanity)

global stops
stops=("a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "i", "if", "in", "into", "is", "it", "its", "of", "off", "on", "or", "than", "that", "the", "to", "with")

global morning
morning = ('coffee','bagel','morning','sunrise','train','subway','breakfast','newspaper', 'tired', 'yawn', 'yawning')
morningSet = set(morning)

global afternoon
afternoon = ('work','lunch','afternoon','cafeteria')
afternoonSet = set(afternoon)

global night
night = ('bar','drink','dinner','night','beer','gym', 'wine')
nightSet = set(night)

global lateNight
lateNight = ('club','drunk','late night','2am','3am','4am')
lateNightSet = set(lateNight)

def getInfo(link):
    soup = BeautifulSoup(urllib2.urlopen(link).read())
    post = {}
    
    title = str(soup.find('span', {'class':'postingtitletext'})).encode('ascii','ignore').lower()
    title = removeTags(title)
    #print removeTags(post['title'])

    post['title'] = title
    
    regex = re.compile('[mMfFwW]4[mMfFwW]')
    match = regex.search(title)
    
    if match:
        looking = match.group()
        print looking
        if looking[0] == 'm' or looking[0] == 'M':
            post['posterGender'] = 'm'
        else:
            post['posterGender'] = 'w'
        if looking[2] == 'm' or looking[2] == 'M':
            post['lookingFor'] = 'm'
        else:
            post['lookingFor'] = 'w'
    else:
        post['posterGender'] = 'N/A'
        post['lookingFor'] = 'N/A'
    
    
    text = str(soup.find('section', {'id':'postingbody'})).encode('ascii','ignore').lower()
    text = removeTags(text)
    pretty = makePretty(text)
    post['text'] = pretty
    
    clean = makeClean(pretty)
    post['clean'] = clean
    
    post['tokens'] = post['clean'].split()
    post['length'] = len(post['tokens'])
    post['stopped'] = removeStops(post['tokens'])
    
    post['dirtyScore'] = dirtyTest(post)
    post['snarkyScore'] = setSnarky(post)
    
    
    time = str(soup.find('time')).encode('ascii','ignore').lower()
    time = removeTags(time)
    post['time'] = time
    
    post['morningScore'] = setMorning(post)
    post['afternoonScore'] = setAfternoon(post)
    post['nightScore'] = setNight(post)
    post['lateNightScore'] = setLateNight(post)	
    
    #print post['tokens']
    #print post['stopped']
    post['link'] = link
    return post
    
def setSnarky(post):
    if post['length'] < 12 and post['length'] >2:
        return 12-post['length']
    else:
        return 0
    
def setMorning(post):
    tokenSet = set(post['tokens'])
    return float(len([i for i in tokenSet if i in morningSet]))/len(tokenSet)
    
def setAfternoon(post):
    tokenSet = set(post['tokens'])
    return float(len([i for i in tokenSet if i in afternoonSet]))/len(tokenSet)
    
def setNight(post):
    tokenSet = set(post['tokens'])
    return float(len([i for i in tokenSet if i in nightSet]))/len(tokenSet)
    
def setLateNight(post):
    tokenSet = set(post['tokens'])
    return float(len([i for i in tokenSet if i in lateNightSet]))/len(tokenSet)
    
def dirtyTest(post):
    tokenSet = set(post['tokens'])
    return float(len([i for i in tokenSet if i in profanitySet]))/len(tokenSet)
    
def removeStops(tokens):
    tight=[]
    for token in tokens:
        if not token in stops:
            tight.append(token)
    return tight
    
def makePretty(text):
    for char in '\n\t':
        text = text.replace(char, ' ')
    return text.strip()

def makeClean(clean):
    for char in ',;:!?\n\t.\(){}[]':  
        clean = clean.replace(char,' ')
    clean=clean.replace("  "," ")
    return clean
        
def removeTags(s):
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
    
def getAllLinks(city):
    i = 0
    allLinks = []
    while True:
        print i
        search = 'http://'+city+'.craigslist.org/search/mis?s='+str(i)
        
        soup = BeautifulSoup(urllib2.urlopen(search).read())
        links = soup.find_all('a')
        
        hdrlnk = False
        for link in links:
            linkClass = link.get('class')
            if linkClass and 'hdrlnk' in linkClass:
                hdrlnk = True
                post = 'http://'+city+'.craigslist.org'+link.get('href')
                allLinks.append(post)
                
                #return allLinks
                
        if not hdrlnk:
            return allLinks
        
        i += 100

def makeScript(posts):
    script = []
    sortedByMorning = sorted(posts, key = lambda k:k['morningScore'])
    sortedByMorning.reverse()
    morningPost = sortedByMorning[0]
    
    person2 = morningPost['lookingFor']
    person1 = morningPost['posterGender']
    
    print person1
    print person2
    
    script.append(morningPost['clean'])
    
    times = ['afternoonScore','nightScore','lateNightScore']
    poster = 2
    
    for i in range(len(times)):
    
        mySorted = sorted(posts, key = lambda k:k[times[i]])
        mySorted.reverse()
    
        if person1 != 'N/A':
            found = False
            for post in mySorted:
                if (poster == 2 and post['posterGender'] == person2 and post['lookingFor'] == person1) or (poster == 1 and post['posterGender'] == person1 and post['lookingFor'] == person2):
                    if post['clean'] not in script:
                        script.append(post['clean'])
                        print post['posterGender']
                        print post['lookingFor']
                        print
                        found = True
                        break
            if not found:
                for post in mySorted:
                    if post['clean'] not in script:
                        script.append(post['clean'])
                        break
            if poster == 2:
                poster = 1
            else:
                poster = 2
        else:
            for post in mySorted:
                if post['clean'] not in script:
                    script.append(post[0]['clean'])
                    break
        
    

    return script

def createEmotionArc(emotion,direction,length, startingPoster, startingLookingFor, starting = 'average', jumpMultiplier = 0):

	allPosts = database.find({emotion:{'$gt':0}}).sort(emotion, ASCENDING)
	emotionScores = []
	
	for post in allPosts:
		emotionScores.append(post[emotion])
		
	sumEmotion = 0.0
	sumDistance = 0.0
	for i in range(len(emotionScores)):
		sumEmotion += emotionScores[i]
		if i>0:
			sumDistance += emotionScores[i] - emotionScores[i-1]
	
		
	averageDistance = sumDistance/(len(emotionScores)-1)
	averageEmotion = sumEmotion/len(emotionScores)
	
	arc = []

	temp = startingPoster
	startingPoster = startingLookingFor
	startingLookingFor = temp
	
	for i in range(length):
		temp = startingPoster
		startingPoster = startingLookingFor
		startingLookingFor = temp
		posts = database.find({emotion:{'$gt':0},'posterGender':startingPoster, 'lookingFor':startingLookingFor})
		
		if direction == 'up':
			posts.sort(emotion, ASCENDING)
		elif direction == 'down':
			posts.sort(emotion, DESCENDING)
		arc.append(posts)
			
	lines = []
	
	prev = averageEmotion
	if starting == 'extreme':
		if direction == 'up':
			prev = 0
		if direction == 'down':
			prev = 1		
			
	
	for lineOptions in arc:
		if direction == 'up':
			prev = prev + jumpMultiplier*averageDistance
		elif direction == 'down':
			prev = prev - jumpMultiplier*averageDistance
			
		added = False
		for post in lineOptions:
			if ((direction == 'up' and post[emotion] >= prev) or (direction == 'down' and post[emotion] <= prev)) and post not in lines:
				lines.append(post)
				prev = post[emotion]
				added = True
				break
		if not added:
			for post in lineOptions:
				if post not in lines:
					lines.append(post)
					prev = post[emotion]
					added = True
					break
		#if not added and lineOptions.count()>0:
		#	print lineOptions[0]
		#	lines.append(lineOptions[0])
		#	prev = post[emotion]
				
				
	for line in lines:
		print line[emotion]
		print line['text']
		print
		
	
		
		
		

def findNextLineOptions(poster, lookingFor, emotion = None, time = None):
    if emotion:
        posts = database.find({time:{'$gt':0}, emotion:{'$gt':0},'posterGender':poster, 'lookingFor':lookingFor})
    else:   
        posts = database.find({time:{'$gt':0}, 'posterGender':poster, 'lookingFor':lookingFor})
    posts.sort(time, DESCENDING)
    for post in posts:
        print post[time]
        print post['text']
        print

if __name__=='__main__':
    
    
        
    '''
    #pickle.dump(posts, open('chicagoTest.p','wb'))
    

    #posts = pickle.load(open('chicagoTest.p','rb'))
    
    for post in posts:
        database.insert(post)
        
    
    script = makeScript(posts)
    for line in script:
        print line
        print
    
    
    time = 'lateNightScore'
    sortedPosts = sorted(posts, key = lambda k:k[time])
    sortedPosts.reverse()
    for i in range(10):
        post = sortedPosts[i]
        print post['title']
        print post['text']
        print post[time]
        print post['dirtyScore']
        print
    
    '''
    #print "UP"
    createEmotionArc('dirtyScore','down',5,'m','w', 'extreme',5)
    #print
    #print
    #print "DOWN"
    #createEmotionArc('dirtyScore','down',4,'m','w','average',10)
    #findNextLineOptions('m','w', 'dirtyScore','morningScore')
    