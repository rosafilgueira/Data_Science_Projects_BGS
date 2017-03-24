import sys
import requests
import os
import urllib2
import urllib
from bs4 import BeautifulSoup

######## Parameter to search events  #################
starttime ='2016-08-15T00%3A00%3A00'
endtime = '2017-02-07T23%3A59%3A59'
minmag = '5'
maxmag = '10'
##############################################


########## Download a list of events according to the parameters ################
url_search ='http://webservices.ingv.it/fdsnws/event/1/query?starttime=%s&endtime=%s&minmag=%s&maxmag=%s&mindepth=-10&maxdepth=1000&minlat=35&maxlat=49&minlon=5&maxlon=20&minversion=100&orderby=time-asc&format=text&limit=10000' % (starttime, endtime, minmag, maxmag)

data = urllib2.urlopen(url_search)
total_lines = data.read().splitlines(True)
count_events = 0
list_events =[]

for line in total_lines:
	if count_events > 0 :
	    event = line.split("|")[0]
	    list_events.append(event)
	
	count_events = count_events +1	
	
################################################################################

######## Download relevant information from each event ######################

location_magnitude = {}
for event in list_events:
    print ("Download data from event %s", event)	
    url_event = 'http://cnt.rm.ingv.it/en/event/%s' % str(event)
    html = urllib.urlopen(url_event).read()
    soup = BeautifulSoup(html)
   
    location_magnitude[event] = []
    table = soup.find('table', attrs={'class':'display table table-hover'})
    rows = table.find_all('tr')

    ####### Elements stored in location_magnitude ##############
    ###Type,Date_and_Time, Latitude, Longitude, Magnitude, Depth, Published_time, Autor, Location_ID
    for row in rows:
        cols = row.find_all('td')
        cols = [str(ele.text.strip()) for ele in cols]
        location_magnitude[event].append([ele for ele in cols if ele]) # Get rid of empty values
    print location_magnitude[event]
    print ("\n")	   

#######Not needed ####### For saving in a file #############
#testfile = urllib.URLopener()
#file_name = "list_events.txt"
#testfile.retrieve(url_search, file_name)
##############################################
