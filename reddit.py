from requests import get
import praw, filters
import pickle

global r
r = praw.Reddit('Theater testing')

def search(query):
    """
    Send query to Reddit search
    """
    reddits = []   
    if query:
        headers = {'User-Agent' : 'Mozilla/5.0'}
        params = {
            'q': query,
            'limit': 10,
            'sort': 'relevance',
            't': 'month'
        }
        r = get('http://www.reddit.com/search.json', params=params,
            headers=headers)
        d = r.json()
        if 'error' in d:
            if d['error'] == 429:
                raise Exception('You are being rate limited by Reddit')
            else:
                raise Exception(d['error'])       
        if 'data' in d and 'children' in d['data']:
            for r in d['data']['children']:
                reddits.append({
                    'id': r['data']['id'],
                    'title': r['data']['title'],
                    'permalink': 'http://www.reddit.com'+r['data']['permalink']
                })   
    return reddits

def getTopLevelQuestion(word, subreddit):
    searchTerm = 'subreddit:'+subreddit+" "+word
    results = search(searchTerm)
    questions = []
    for result in results:
        submission = r.get_submission(url = result['permalink'])
        question = filters.build_Text(submission.title, 'Question')
        print question['Text']
        question['selftext'] = filters.build_Text(submission.selftext, 'Question')
        comments = submission.comments
        for comment in comments:
            if isinstance(comment, praw.objects.Comment):
                question['Answers'].append(comment)
        question = filters.my_rank_question(question)
        if question:
            questions.append(question)
    return questions
    
 
def getNextLevel(question, emotion):
    if emotion == 'Dirty':
        responses = question['DirtyAnswers']
    elif emotion == 'Snarky':
        responses = question['SnarkyAnswers']
    else:
        responses = question['GoodAnswers']
    if not responses:
    	responses = question['GoodAnswers']
    response = responses[0]
    answer = filters.build_Text(response['Text'], 'Answer')
    comments = response['CommentObj'].replies
    for comment in comments:
        if isinstance(comment, praw.objects.Comment):
            answer['Answers'].append(comment)
    answer = filters.my_rank_question(answer)
    return answer
        


def findQuestion(text):
    pass

if __name__ == '__main__':
    
    reddits = pickle.load(open('angry.p', 'rb'))
    for reddit in reddits:
        questions = reddits[reddit]
        sortedQuestions = sorted(questions, key = lambda k: k['selftext']['DirtyScore'])
        sortedQuestions.reverse()
        reddits[reddit] = sortedQuestions
    print reddits['askmen'][1]['Text'] 
    response = reddits['askmen'][1]
    for i in range(3):
        response = getNextLevel(response, 'Dirty')
        print response['Text']
    
  	'''
    reddits = ['askmen','askwomen']
    word = 'angry'
    allQuestions = {}
    for reddit in reddits:
        print reddit
        questions = getTopLevelQuestion(word, reddit)
        allQuestions[reddit] = questions
        print
    pickle.dump(allQuestions, open('angry.p', 'wb'))
    '''  
    
    '''
    r = praw.Reddit('Theater testing')
    results = search('sad reddit:askreddit')
    for result in results:
        print result['permalink']
        submission = r.get_submission(url = result['permalink'])
        question = filters.build_Text(submission.title, 'Question')
        print question['Text']
        print
        comments = submission.comments
        for comment in comments:
            if isinstance(comment, praw.objects.Comment):
                question['Answers'].append(comment)
        question = filters.my_rank_question(question)
        if question:
            print "Good " + str(len(question['GoodAnswers']))
            print "Dirty " + str(len(question['DirtyAnswers']))
            print "Snarky " +str(len(question['SnarkyAnswers']))
            for answer in question['DirtyAnswers']:
                print answer['Text']
                print answer['DirtyScore']
                print
    '''