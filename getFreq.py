import pickle

file = open('freq.txt', 'rb')
dict = {}
for line in file:
	split = line.split('\t')
	dict[split[1].lower()] = int(split[3])
	
#print dict['the']
pickle.dump(dict, open('wordFreq.p', 'wb'))
