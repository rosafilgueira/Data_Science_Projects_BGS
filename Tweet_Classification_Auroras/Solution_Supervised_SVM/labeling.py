import csv
import json
import nltk
from nltk.corpus import wordnet
import re
import codecs
import operator  
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.core import GenericPE
from dispel4py.base import IterativePE, ConsumerPE
import bisect
from collections import Counter

class ReadData(GenericPE): 
    def __init__(self):
        GenericPE.__init__(self)
        self._add_output('output')
	self.count = 0

    def process(self, inputs):
	self.log("inputs is %s" % input)
        twitterData= inputs['input']
	filename= ROOT_DIR + twitterData
	with open(filename) as json_data:
            data = json.load(json_data)
	self.log("filename is %s" % filename)
	tweets = data['hits']['hits']

	for tweet in tweets:
            if tweet[u'_source'][u'user'][u'lang'] == 'en' or tweet[u'_source'][u'user'][u'lang']=='en-gb':
                text = coordinates = place = location = ''
        	text = tweet[u'_source'][u'text'].encode('utf-8')
        	if u'coordinates' in tweet[u'_source']:
        	    if tweet[u'_source'][u'coordinates']:
                        coordinates = tweet[u'_source'][u'coordinates'][u'coordinates']
                        print(coordinates)
        	elif u'place' in tweet[u'_source'][u'place']:
                    place = tweet[u'_source'][u'place'][u'full_name'].encode('utf-8')
		    print(place)	
        	elif u'user' in tweet[u'_source'][u'user'][u'location']:
                    location = tweet[u'_source'][u'user'][u'location'].encode('utf-8')
		    print(location)	
 	        self.count += 1	
            	return_tweet={'text':text, 'coordinates':coordinates,'place':place, 'location':location}
                self.write('output',return_tweet)
		self.log("Total tweets found %s" % self.count)

class AgreateData(IterativePE):
    def __init__(self):
        IterativePE.__init__(self)
	self.tweet_info=[]

    def _process(self, data):
	tweet = data
	data_text={}
	data_text['tweet']= tweet['text']
	data_text['label']= ''
	
	self.tweet_info.append(data_text)
	return (self.tweet_info)


class WriteJson(IterativePE):
    def __init__(self):
        IterativePE.__init__(self)
    def _process(self, data):
	tweet_info = data
        name="./Data/labeled_data.json"
	data_twitter={}
	data_twitter['info'] = tweet_info
        with open(name,'w+') as outfile:
	    json.dump(data_twitter, outfile)
	

ROOT_DIR="../Data/"	
tweets= ReadData() 
tweets.name='read'

agregate= AgreateData()

writejson = WriteJson()
graph = WorkflowGraph()

graph.connect(tweets, 'output', agregate, 'input')
graph.connect(agregate, 'output', writejson, 'input')
