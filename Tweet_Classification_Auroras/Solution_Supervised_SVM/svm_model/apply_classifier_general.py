import pickle
import csv
import json
import os
import numpy as np
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
            data['label']= '1'
        else:
            data['label']= '0'
        #self.tweet_info.append(data)
        return (data)



class WriteCSV(GenericPE):
    def __init__(self):
    	GenericPE.__init__(self)
	self._add_input('input', grouping='global')
	self.tweet_info = []
	self.raw_x=[]
	self.all_predictions=[]
    def _process(self, inputs):
	data = inputs['input']
        self.raw_x.append(data['text'])
        self.all_predictions.append(data['label'])
    def _postprocess(self):	
	self.log("all_predictions %s" % self.all_predictions)
	self.log("all_predictions %s" % self.raw_x)
	 
	predictions_human_readable = np.column_stack((np.array(self.raw_x), self.all_predictions))
	out_path = os.path.join(RESULTS_DIR, "prediction_LR.csv")
	print("Saving evaluation to {0}".format(out_path))
	with open(out_path, 'w') as f:
    		csv.writer(f).writerows(predictions_human_readable)


	
#parent = os.path.abspath('..')
ROOT_DIR= "../Data/"
RESULTS_DIR="./Results/"	
tweets= ReadData() 
tweets.name='read'
PATH = "./svm_model/model.pickle"
with open(PATH, 'rb') as f:
    model = pickle.load(f)

classify= ClassifyData(model)
writecsv = WriteCSV()
graph = WorkflowGraph()

graph.connect(tweets, 'output', classify, 'input')
graph.connect(classify, 'output', writecsv, 'input')
