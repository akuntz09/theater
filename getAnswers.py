import feedparser
import urllib2
from bs4 import BeautifulSoup
import re
import string
import sys
import pickle
import operator
from pymongo import Connection, DESCENDING, ASCENDING

def getAnswers(link):
	soup = BeautifulSoup(urllib2.urlopen(link).read())
	
	allAnswers = []
	
	
	answers = soup.findAll('span', {'class':'ya-q-full-text'})
	links = soup.findAll('a', {'class':'Clr-bl'})
	next = links[-1]
	nextLink = next['href']
	
	
	if 'page' in nextLink:
		oldNum = link.split('=')[-1]
		num = nextLink.split('=')[-1]
		if num != oldNum:
			nextLink = link.split('page=')[0]+'page='+str(num)
			print nextLink
			getAnswers(nextLink)
	
		#for answer in answers:
		#print answer

if __name__ == '__main__':
	#getAnswers('https://answers.yahoo.com/question/index?qid=20100609223516AAwPxOt')
	getAnswers('https://answers.yahoo.com/question/index?qid=20130719194841AAYvfO1&page=1')