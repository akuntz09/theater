import praw

r = praw.Reddit(user_agent='Test Script')
subs = r.get_subreddit('hearthstone').get_top(limit=10)
for sub in subs:
	print sub
	comments = sub.comments
	for comment in comments:
		print comment
	break