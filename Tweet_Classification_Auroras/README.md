# GeoSocial-Aurora


The “GeoSocial-Aurora” project is starting to explore the usefulness of social media for scientific survey and analysis with the release of GeoSocial-Aurora, a web-mapping tool that searches for tweets related to aurora sightings and locates them as markers on a map. During the last years, tweets that contain “aurora borealis” terms (or similar) have been stored in a BGS facility.  In addition, the tweets that do not contain any stop-words are plotted in a web map. However, not all these tweets are related with aurora borealis.  Therefore, a ML classification technique needs to be applied before plotting those tweets in the map. 

ii. Solution(s) adopted.  I have applied two  Machine learning classifier approaches:

	a) Using a supervised method and Logistic Regression algorithm. Previously, label manually 1200 tweets between auroras and 	others.The, the classifier was trained and tested using the label data, getting an accuracy of 90 %. Finally, I applied the 		classifier against a large number of tweets, and made some statistics. 
	
	b) Using deep-Neural Networks Neural Networks (rf-cnn-text-classification-tf) with TensorFlow strategy for doing the same classification, and compare techniques. This code is a branch of the original code developed by Denny Britz at https://github.com/dennybritz/cnn-text-classification-tf

iii. Data Science areas:  Data Mining + Machine Learning + Software tools + Parallel Computing + Parallel Systems

iv. Resources:  data-pipeline (dispel4py) + Python + TensorFlow + NLTK and Scikit-Learn+ BGS CLUSTER/Jazmin

