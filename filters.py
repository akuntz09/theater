import string
from nltk.stem.porter import *

# We need a set of tests and filters that can be used to evaluate different types of 
# text that we wil be using.  These will all be associated with text objects.  A text 
# object has the following features:
#   Text: unprocessed text
#   Type: The type of text it is 
#   Tokens: tokenized version of the text everything in lower case
#   Stopped: a ist of tokenized text with all stop words removed
#   TokenSet: the list of Tokens stored as a set
#   Clean: version of the text with extraneous characters removed
#   PersonalN: number of personal pronouns in the Text
#   Personal: a Bool that is set to True if there are personal pronouns in the set
#   Fits: a Bool that reflects whether a price of text is the right size (dependent on the type of text)
#   Length: how many words are in the text (approximate off of tokenizing)
#   Dirty: the number of dirty words in the text
#   Interesting: score ranking how interesting it is (dependent on the type of text)

# While not a tester, we need to be able to build a Text object.  To do so, we need the text
# and the type.  This build the object and then returns it

global stemmer
stemmer = PorterStemmer()

def build_Text(text, type):
    text=text.encode('ascii', 'ignore')
    text=remove_tags(text)
    Text={}
    pretty=text
    for char in '\n\t':  
        pretty = pretty.replace(char,' ')
    Text["Text"]=pretty.strip()
    Text["Type"]=type
    clean=text
    for char in ',;:!?\n\t.\(){}[]':  
        clean = clean.replace(char,' ')
    clean=clean.replace("  "," ")
    Text["Clean"]=clean.lower()
    Text["Tokens"]=Text["Clean"].split()
    if type == "Question" or type=="Title":
        Text["Clean"] = Text["Clean"].strip()+"?"
    Text["Length"]=len(Text["Tokens"])
    Text["TokenSet"]=set(Text["Tokens"])
    Text["Stopped"]=remove_stops(Text["Tokens"])
    Text['StemmedTokens'] = stem_set(Text['Tokens'])
    Text["Stops"]=just_stops(Text["Tokens"])
    Text["PersonalBool"]=personal_test(Text)
    Text["DirtyScore"]=dirty_test(Text)
    Text["SnarkyScore"]=set_snarky(Text)
    Text["Fits"]=range_test(Text)
    Text["RelationshipBool"]=relationship_test(Text)
    Text['Answers'] = []
    Text['CommentObj'] = None
#    Text["InterestingScore"]=0
    return Text

# Words are also structured will all have four elements:
#   Word: the word itself
#   Questions: questions associated with the word
#   Rank: where in a list it was found
#   Interesting: score ranking how interesting it is based on questions

# build_Word assumes that words are coming from somewhat messy spaces

# Finally, when a word is grabbed, the questions associated with it are pulled from
# Yahoo or the cache

def build_Word(word, rank):
    word=word.encode('ascii', 'ignore')
    Word = {}
    Word["Word"]=word
    Word["Rank"]=rank
    Word["InterestingScore"]=0
    Word["Questions"]=CQuest.get_questions(word)
    return Word


# All of these tests assume this structure

global pronouns
pronouns=("i","me", "us","my","our","we","his","her","he","she","i've","we've","she's","he's")
pronounSet=set(pronouns)

global relationships
relationships=('boy','girl','friend','friends','lover','wife','husband','mom','dad','mother','father','son','daugther','kid','child','parent','parents','clidren','boss','buddy','bf','bff','gf')
relationshipSet=set(relationships)

global profanity
global stemmedProfanity
stemmedProfanity = []
profanity=('sex','bum', 'shitfaced', 'fucked', 'plastered', 'wasted', 'hammered', 'cheating', 'sex', 'lust','thrust', 'pelvic','breast', 'breasts','anus','arse','arsehole','ass','ass-hat','ass-jabber','ass-pirate','assbag','assbandit','assbanger','assbite','assclown','asscock','asscracker','asses','assface','assfuck','assfucker','assgoblin','asshat','asshead','asshole','asshopper','assjacker','asslick','asslicker','assmonkey','assmunch','assmuncher','assnigger','asspirate','assshit','assshole','asssucker','asswad','asswipe','axwound','bampot','bastard','beaner','bitch','bitchass','bitches','bitchtits','bitchy','blow job','blowjob','bollocks','bollox','boner','brotherfucker','bullshit','bumblefuck','butt plug','butt-pirate','buttfucka','buttfucker','camel toe','carpetmuncher','chesticle','chinc','chink','choad','chode','clit','clitface','clitfuck','clusterfuck','cock','cockass','cockbite','cockburger','cockface','cockfucker','cockhead','cockjockey','cockknoker','cockmaster','cockmongler','cockmongruel','cockmonkey','cockmuncher','cocknose','cocknugget','cockshit','cocksmith','cocksmoke','cocksmoker','cocksniffer','cocksucker','cockwaffle','coochie','coochy','coon','cooter','cracker','cum','cumbubble','cumdumpster','cumguzzler','cumjockey','cumslut','cumtart','cunnie','cunnilingus','cunt','cuntass','cuntface','cunthole','cuntlicker','cuntrag','cuntslut','dago','damn','deggo','dick','dick-sneeze','dickbag','dickbeaters','dickface','dickfuck','dickfucker','dickhead','dickhole','dickjuice','dickmilk','dickmonger','dicks','dickslap','dicksucker','dicksucking','dicktickler','dickwad','dickweasel','dickweed','dickwod','dike','dildo','dipshit','doochbag','dookie','douche','douchebag','douchewaffle','dumass','dumb ass','dumbass','dumbfuck','dumbshit','dumshit','dyke','fag','fagbag','fagfucker','faggit','faggot','faggotcock','fagtard','fatass','fellatio','feltch','flamer','fuck','fuckass','fuckbag','fuckboy','fuckbrain','fuckbutt','fuckbutter','fucked','fucker','fuckersucker','fuckface','fuckhead','fuckhole','fuckin','fucking','fucknut','fucknutt','fuckoff','fucks','fuckstick','fucktard','fucktart','fuckup','fuckwad','fuckwit','fuckwitt','fudgepacker','gay','gayass','gaybob','gaydo','gayfuck','gayfuckist','gaylord','gaytard','gaywad','goddamn','goddamnit','gooch','gook','gringo','guido','handjob','hard on','heeb','hell','ho','hoe','homo','homodumbshit','honkey','humping','jackass','jagoff','jap','jerk off','jerkass','jigaboo','jizz','jungle bunny','junglebunny','kike','kooch','kootch','kraut','kunt','kyke','lardass','lesbian','lesbo','lezzie','mcfagget','mick','minge','mothafucka','mothafuckin','motherfucker','motherfucking','muff','muffdiver','munging','nigaboo','nigga','nigger','niggers','niglet','nutsack','paki','panooch','pecker','peckerhead','penis','penisbanger','penisfucker','penispuffer','piss','pissed','pissflaps','polesmoker','pollock','poon','poonani','poonany','poontang','porchmonkey','porchmonkey','prick','punanny','punta','pussies','pussy','pussylicking','puto','queef','queer','queerbait','queerhole','renob','rimjob','ruski','sandnigger','schlong','scrote','shit','shitass','shitbag','shitbagger','shitbrains','shitbreath','shitcanned','shitcunt','shitdick','shitface','shitfaced','shithead','shithole','shithouse','shitspitter','shitstain','shitter','shittiest','shitting','shitty','shiz','shiznit','skank','skeet','skullfuck','slut','slutbag','smeg','snatch','spic','spick','splooge','spook','suckass','tard','testicle','thundercunt','tit','titfuck','tits','tittyfuck','twat','twatlips','twats','twatwaffle','unclefucker','vag','vagina','vajayjay','vjayjay','wank','wankjob','wetback','whore','whorebag','whoreface','wop')
for word in profanity:
    stemmedProfanity.append(stemmer.stem(word))
stemmedProfanitySet = set(stemmedProfanity)
profanitySet=set(profanity)

global stops
stops=("a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "i", "if", "in", "into", "is", "it", "its", "of", "off", "on", "or", "than", "that", "the", "to", "with")

global ranges
ranges={}
ranges["Title"]=(1,30)
ranges["Question"]=(5,100)
ranges["Definition"]=(8,30)
ranges["Answer"]=(5,160)
ranges["Use"]=(8,30)

# personal_test calculates the number of personal pronouns in the text.  It sets both
# Personal and PersonalB

def personal_test(Text):
    Text["PersonalN"]=len(pronounSet.intersection(Text["TokenSet"]))
    return Text["PersonalN"] > 0

# dirty_test calculates the number of dirty words in the text.  

def dirty_test(Text):
    return len(stemmedProfanitySet.intersection(Text["StemmedTokens"]))

# relationship_test calculates the number of relationships words in the text.  

def relationship_test(Text):
    Text["RelationshipN"]=len(relationshipSet.intersection(Text["TokenSet"]))
    return Text["RelationshipN"] > 0



# range_test calculates whether the text is within the right range for the kind of text 
# that it is

def range_test(Text):
    myRange=ranges[Text["Type"]]
    return len(Text["Tokens"]) >= myRange[0] and len(Text["Tokens"]) <= myRange[1] 


# Good_question checks to see if a question is worthy of our interest.  The factors are:
#   Personal in title or question
#   Right length of elements
#   If these work then collect the right answers

# Right now, a good answer has to be personal and the right size.
  
def my_rank_question(question):
    question["GoodAnswers"]=[]
    question["DirtyAnswers"]=[]
    question["SnarkyAnswers"]=[]    
    question["InterestingQuestions"]=[]
    question["AnswerScore"]=0
    question["QuestionScore"]=0
    
    goodQuestion=question["Fits"]

    question['GoodAnswers'] = filter_good_answers(question['Answers'])
    question["DirtyAnswers"]=filter_dirty_answers(question["Answers"])       
    question["SnarkyAnswers"]=filter_snarky_answers(question["Answers"])
        
    question["AnswerScore"]=len(question["GoodAnswers"])+len(question["DirtyAnswers"])+(len(question["SnarkyAnswers"]*2))       
    question["QuestionScore"]=question["DirtyScore"]+question["SnarkyScore"]
 
    return question
            
def filter_good_answers(answers):
    filtered=[]
    for comment in answers:
        answer = build_Text(comment.body, 'Answer')
        if answer["Fits"] and (answer["PersonalBool"] or answer["RelationshipBool"]):
            answer['CommentObj'] = comment
            filtered.append(answer)
    return filtered

# A dirty answer has to have two pieces of profanity and be fairly short.
    
def filter_dirty_answers(answers):
    filtered=[]
    for comment in answers:
        answer = build_Text(comment.body, 'Answer')
        if answer["Length"] < 25 and (answer["DirtyScore"] > 1):
            answer['CommentObj'] = comment
            filtered.append(answer)
    sortedFiltered = sorted(filtered, key=lambda k: k['DirtyScore'])
    sortedFiltered.reverse()
    return sortedFiltered    
                    
# A snarky answer has to be really short.
    
def filter_snarky_answers(answers):
    filtered=[]
    for comment in answers:
        answer = build_Text(comment.body, 'Answer')
        if answer["Length"] < 15 and answer > 2:
            answer['CommentObj'] = comment
            filtered.append(answer)
    sortedFiltered = sorted(filtered, key=lambda k: k['SnarkyScore'])
    sortedFiltered.reverse()
    return sortedFiltered    
    
# A snarky answer has to be really short.
    
def  set_snarky(Text):
    if Text["Length"] < 12 and Text["Length"] > 2:
        return 12-Text['Length']
    else:
        return 0
         
# remove_stops takes all of the stops words out of a tokenized set
 
def remove_stops(tokens):
    tight=[]
    for token in tokens:
        if not token in stops:
            tight.append(token)
    return tight

# remove_stops takes all of the stops words out of a tokenized set
 
def just_stops(tokens):
    myStops=[]
    for token in tokens:
        if token in stops:
            myStops.append(token)
    return myStops
    
def stem_set(words):
    stemmed = []
    for word in words:
        stemmed.append(stemmer.stem(word))
    return stemmed
 
   
# remove_tags removes all of the HTML tags from string.  

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
    