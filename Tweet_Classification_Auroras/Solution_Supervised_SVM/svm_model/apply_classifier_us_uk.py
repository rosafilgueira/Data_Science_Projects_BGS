import pickle
import csv
import json
import os

from svm_model.classification_module import NLTKPreprocessor , identity 
from sklearn.base import BaseEstimator, TransformerMixin

import re
import codecs
import operator  
import sys
sys.path.pop(0)
#reload(sys)
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
        twitterData= inputs['input']
        filename= ROOT_DIR + twitterData
        with open(filename) as json_data:
            data = json.load(json_data)
        tweets = data['hits']['hits']

        for tweet in tweets:
            try:
                if tweet[u'_source'][u'user'][u'lang'] == 'en' or tweet[u'_source'][u'user'][u'lang']=='en-gb':
                    text = coordinates = place = location = country = ''
                    text = tweet[u'_source'][u'text'].encode('utf-8')
                    if u'coordinates' in tweet[u'_source']:
                        if tweet[u'_source'][u'coordinates']:
                            coordinates = tweet[u'_source'][u'coordinates'][u'coordinates']
                    if u'place' in tweet[u'_source']:
                        if tweet[u'_source'][u'place']:
                            place = tweet[u'_source'][u'place'][u'full_name'].encode('utf-8')
                            if tweet[u'_source'][u'place'][u'country_code']:
                                country = tweet[u'_source'][u'place'][u'country_code'].encode('utf-8')
                    if u'user' in tweet[u'_source']:
                        if u'location' in tweet[u'_source'][u'user']:
			    if tweet[u'_source'][u'user'][u'location']:
                                location = tweet[u'_source'][u'user'][u'location'].encode('utf-8')
                    self.count += 1	
                    return_tweet={'text':text, 'coordinates':coordinates,'place':place, 'location':location, 'country':country}
                    self.write('output',return_tweet)
            except ValueError:
                 continue
        self.log("Total of tweets counted %s" % self.count)
	

class ClassifyData(IterativePE):
    def __init__(self, model):
        IterativePE.__init__(self)
        self.tweet_info=[]
	self.model = model

    def _process(self, data):
        classification = self.model.predict([data['text']])
        if classification[0] == 0:
            data['label']= 'Aurora'
        else:
            data['label']= 'Other'
        #self.tweet_info.append(data)
        return (data)


class FindLocation(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input ('input')
        self._add_output('output_auroras_us')
        self._add_output('output_auroras_uk')
        self._add_output('output_auroras_no_us_uk')
        self._add_output('output_others')
        self.UK_countries={}
        self.US_states={}
        uk_filename= "uk-countries.json"
        us_filename= "us-states.json"
        self.US_states=self.load_states(us_filename)
        self.UK_countries=self.load_countries(uk_filename)
    def _process(self, inputs):
        data = inputs['input']
	if data['label'] == 'Aurora':
            state = self.find_country(data)
            if state :
		country = 'GB'
                self.write('output_auroras_uk', [data, state, country])
            else:
                state = self.find_state(data)
                if state:
		    country = 'US'
                    self.write('output_auroras_us', [data, state , country])
            	else:
                    self.write('output_auroras_no_us_uk', [data])
	else:
            self.write('output_others', [data])

    def find_country(self, tweet):
        if tweet[u'location']:
            location = tweet['location']
            location = " " + location + " "
            country_name = [s for s in self.UK_countries['name'] if s.lower() in location.lower()]
	    if country_name:
	        return country_name[0]
        elif tweet['place']:
            place = tweet['place']
            place = " "+place+" "
            country_name = [s for s in self.UK_countries['name'] if s.lower() in place.lower()]
	    if country_name:
	    	return country_name[0]
        elif tweet['country']:
            country = tweet['country']
            country = " "+country+" "
            country_name = [s for s in self.UK_countries['name'] if s.lower() in country.lower()]
	    if country_name:
	    	return country_name[0]
	return ''
        
    def find_state(self, tweet):
        ## Then look at the place attribute
        if tweet[u'location']:
            location = tweet['location']
            location = " " + location + " "
	    #self.log("I am going to check - Location %s" % location.lower())
            state_abbr = [s for s in self.US_states['abbr'] if " "+s+" " in location.lower() ]
            state_name = [s for s in self.US_states['name'] if s.lower() in location.lower()]
            if state_abbr:
	        #self.log(" State abbr %s - Location %s" % (state_abbr, location ))	
                return state_abbr[0]
            elif state_name:
                state_idx = self.US_states['name'].index(state_name[0])
	        #self.log(" State name is %s - state_idx %s - Location %s" % (state_name, state_idx, location ))	
                return self.US_states['abbr'][state_idx]
        
        elif tweet[u'place']:
            place = tweet['place']
            place = " "+place+" "
            state_abbr = [s for s in self.US_states['abbr'] if " "+s+" " in place.lower()]
            state_name = [s for s in self.US_states['name'] if s.lower() in place.lower()]
            if state_abbr:
	        #self.log(" State abbr %s - Place %s" % (state_abbr, place ))	
                return state_abbr[0]
            elif state_name:
                state_idx = self.US_states['name'].index(state_name[0])
	        #self.log(" State name is %s - state_idx %s - Place %s" % (state_name, state_idx, place ))	
                return self.US_states['abbr'][state_idx]

	elif tweet[u'country']:
            country = tweet['place']
            country = " "+place+" "
            state_abbr = [s for s in self.US_states['abbr'] if " "+s+" " in country.lower()]
            state_name = [s for s in self.US_states['name'] if s.lower() in country.lower()]
            if state_abbr:
	        #self.log(" State abbr %s - Country %s" % (state_abbr, country ))	
                return state_abbr[0]
            elif state_name:
                state_idx = self.US_states['name'].index(state_name[0])
	        #self.log(" State name is %s - state_idx %s - Country %s" % (state_name, state_idx, country ))	
                return self.US_states['abbr'][state_idx]
        ## Finally look at the coordinates attribute
        elif tweet['coordinates']:
           coord = tweet['coordinates']
           return self.coord2state(coord)
        return ''

    def load_states(self, us_file):
        US_states = {'name': [], 'abbr': [], 'coord': []}
        filename= ROOT_DIR + us_file
        states_file = open(filename, "r")
        features = json.load(states_file)[u'features']
        for f in features:
            US_states['name'].append(f[u'properties'][u'name'].encode('utf-8'))
            US_states['abbr'].append(f[u'properties'][u'state'].encode('utf-8'))
            coord = f[u'geometry'][u'coordinates'][0]
            if len(coord)==1: coord = coord[0]
            US_states['coord'].append(coord)
        return US_states        
    
    def load_countries(self, uk_file):
        UK_countries = {'name': []}
        filename= ROOT_DIR + uk_file
	print("filename is %s" % filename)
        countries_file = open(filename, "r")
        features = json.load(countries_file)[u'features']
        for f in features:
            UK_countries['name'].append(f['properties']['ctry14nm'].encode('utf-8'))
        return UK_countries        

    def coord2state(self,coord):
        ## Check if the given location is within the state boundaries
        picked = []
        for i in range(len(self.US_states['name'])):
            ## Calculate the boundary box of the state
            xy = self.US_states['coord'][i]
            xmin = min(xy, key=lambda x:x[0])
            xmax = max(xy, key=lambda x:x[0])
            ymin = min(xy, key=lambda x:x[1])
            ymax = max(xy, key=lambda x:x[1])
            ## Check if the location is inside the box
            if (coord[0] >= xmin) and (coord[0] <= xmax) and (coord[1] >= ymin) and (coord[1] <= ymax):
                picked.append(i)

        if len(picked) == 0:
             return ''

        if len(picked) == 1:
            return self.US_states['abbr'][picked[0]]

        ## If multiple states are found, pick the one that has
        ## the shortest distance from its center to the location
        d = []
        for k in picked:
            xcenter = 0.5 * sum(x for x,y in self.US_states['coord'][k])
            ycenter = 0.5 * sum(y for x,y in self.US_states['coord'][k])
            d.append( (x-xcenter)**2+(y-ycenter)**2 )
        idx = d.index(min(d))
        return self.US_states['abbr'][idx]



class MapAurora(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input ('input', grouping=[1])
        self._add_output('output')
	self.aurora ={}
        self.max_aurora = None,-5000
    def _process(self, inputs):
        tweet, state , country = inputs['input']
	if state not in self.aurora:
            self.aurora[state] = 1 
        else:
            self.aurora[state] += 1
         
        self.write('output', [state, self.aurora[state], country])

class ReduceAuroraLocation(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input ('input', grouping='global')
        self.state = None
        self.auroriess={} #pair state, aurora_score
        self.top_number = 5  
        self.top_states = []
        self.top_scores = []
	self.total_tweets = 0
	self.country = ''
    def _process(self, inputs):
        state, aurora_score, country = inputs['input']
	self.country = country
	self.total_tweets += 1
        self.auroriess[state]=aurora_score 
        try:
            state_index = self.top_states.index(state)
            del self.top_states[state_index]
            del self.top_scores[state_index]
        except ValueError:
            pass
        index = bisect.bisect_left(self.top_scores, aurora_score)
        self.top_scores.insert(index, aurora_score)
        self.top_states.insert(index, state)
        if len(self.top_scores) > self.top_number:
            self.top_scores.pop(0)
            self.top_states.pop(0)
        self.score = self.top_scores[0]
    def _postprocess(self):	
	count = 0
	self.log("--->!!!Total Aurora-tweets from %s is %s !!!<----" % (self.country, self.total_tweets))
        for (aurora_score, state) in zip(self.top_scores, self.top_states):
            self.log("Top:%s----> state = %s, Aurora_score = %s, total_tweets = %s"  % (count, state, aurora_score, self.total_tweets))
            count += 1

class ReduceAuroraNoUsUk(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input ('input', grouping='global')
        self.total_tweets = 0
    def _process(self, inputs):
        tweet = inputs['input'][0]
	self.total_tweets += 1
	if tweet['coordinates']:
		self.log("Coordinates are: %s" % tweet['coordinates'])
	elif tweet['location']:
		self.log("Location is: %s" % tweet['location'])
	elif tweet['country']:
		self.log("Country is: %s" % tweet['country'])
	elif tweet['place']:
		self.log("Place is: %s" % tweet['place'])
	else:
		self.log("No information about this tweet")	

    def _postprocess(self):	
	self.log("--->!!!Total Aurora-tweets from Non-US-UK is %s !!!<----" % self.total_tweets)





class ReduceOthers(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input ('input', grouping='global')
        self.total_tweets = 0
    def _process(self, inputs):
	self.total_tweets += 1
    def _postprocess(self):	
	self.log("****Total Other-tweets %s******" % self.total_tweets)

class WriteJson(GenericPE):
    def __init__(self):
    	GenericPE.__init__(self)
	self._add_input('input', grouping='global')
	self.tweet_info = []
    def _process(self, inputs):
        self.tweet_info.append(inputs['input'])

    def _postprocess(self):	
	name=RESULTS_DIR+"Auto_classification_8_9_May_2016_us_uk.json"
        data_twitter={}
        data_twitter['info'] = self.tweet_info
        with open(name,'w+') as outfile:
            json.dump(data_twitter, outfile)
	

ROOT_DIR="../Data/"
RESULTS_DIR="./Results/"	
tweets= ReadData() 
tweets.name='read'
PATH = "./svm_model/model.pickle"
with open(PATH, 'rb') as f:
    model = pickle.load(f)

classify= ClassifyData(model)
findlocation=FindLocation()

mapaurora_us=MapAurora()
reduceaurora_us=ReduceAuroraLocation()

mapaurora_uk=MapAurora()
reduceaurora_uk=ReduceAuroraLocation()

reduceaurora_no_us_uk=ReduceAuroraNoUsUk()
reduceothers=ReduceOthers()


writejson = WriteJson()

graph = WorkflowGraph()

graph.connect(tweets, 'output', classify, 'input')
graph.connect(classify, 'output', findlocation, 'input')
graph.connect(findlocation, 'output_auroras_us', mapaurora_us, 'input')
graph.connect(findlocation, 'output_auroras_uk', mapaurora_uk, 'input')
graph.connect(findlocation, 'output_auroras_no_us_uk', reduceaurora_no_us_uk, 'input')
graph.connect(findlocation, 'output_others', reduceothers, 'input')
graph.connect(mapaurora_us, 'output', reduceaurora_us, 'input')
graph.connect(mapaurora_uk, 'output', reduceaurora_uk, 'input')
graph.connect(classify, 'output', writejson, 'input')
