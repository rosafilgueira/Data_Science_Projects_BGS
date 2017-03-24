import numpy
import re
import os
import json
from os import listdir
from os.path import isfile, join
from dispel4py.core import GenericPE
from dispel4py.base import IterativePE, ConsumerPE

def listdirs(folder):
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

class ReadDataPE(IterativePE):
    def __init__(self,root_directory):
        GenericPE.__init__(self)
        self._add_output('output')
        self.root_d=root_directory
    def process(self,inputs):
        years= listdirs(self.root_d)
        self.log("years %s" %years)
        num_years=len(years)
        for y in years:
            if y != 'Results':
                yearpath = y+"/"			
                file_names = [f for f in listdir(yearpath) if isfile(join(yearpath, f))]
                num_files=len(file_names)
                self.log("Number of files %s per year %s" %(num_files,y))		
                for i in file_names:
                    self.write('output', [y, i, num_files, num_years])

class FilterPE(IterativePE):
    def __init__(self):
        IterativePE.__init__(self)

    def _process(self, data):
        yearpath,file,num_files,num_years= data
        vaac_file = yearpath + "/" + file
        lines = [line.rstrip('\n').rstrip('\r').rstrip('') for line in open(vaac_file) if line.strip()]
        fl_value= re.search('FL(.+)', lines[11].strip('ERUPTION DETAILS:'))
        if fl_value:
            fl_data= fl_value.group(1).split()[0]
        else:
            fl_data = "None"

        sub='NXT ADVISORY'
        advice_filter=next((s for s in lines if sub in s),None)
        advice_data = advice_filter.strip('NXT ADVISORY: ')
        if len(advice_data.split("/")) == 2:
            advice_date = advice_data.split("/")[0].strip("LATER THAN ")
            advice_time = advice_data.split("/")[1]
            advice_time= advice_time.strip("Z")
        else:
           advice_date = "None"
           advice_time = "None"
        sub='AVIATION COLOUR CODE:'
        colour_filter=next((s for s in lines if sub in s),None)
        if colour_filter:
            colour_code = colour_filter.split(":")[1]
        else:
            colour_code = "None"
        volcano_data= lines[4].strip('VOLCANO: ')
        volcano_name= volcano_data.split()[0]
        volcano_id = volcano_data.split()[1]
        ##### ID FIX ###################
        if volcano_id != "261080" :
           volcano_id = "261080"
        ################################## 
        dtg_data = lines[2].strip('DTG: ')
        dtg_date = dtg_data.split("/")[0]
        dtg_time = dtg_data.split("/")[1]
        dtg_time = dtg_time.strip("Z")
	
        vaac_filter={'VOLCANO_NAME': volcano_name, 'VOLCANO_ID': volcano_id, 'DATE':dtg_date , 'TIME': dtg_time, 'FL': fl_data, 'ADVICE_DATE': advice_date, 'ADVICE_TIME': advice_time, 'COLOUR_CODE': colour_code}
	
        return(yearpath, volcano_id, vaac_filter,num_files,num_years)


class WriteJsonPE(ConsumerPE):
    def __init__(self):
        ConsumerPE.__init__(self)
        self._add_input ('input', grouping=[1])
        self.storevolcano={'id':'', 'name': '', 'years':''}
        self.volcano_id=''
        self.year_num_files={}
        self.year_cont=0

    def _process(self, data):
        yearpath, volcano_id, vaac_filter, num_files,num_years = data
        self.volcano_id = vaac_filter['VOLCANO_ID']
        if volcano_id not in self.storevolcano['id']:
            self.storevolcano['id']=volcano_id
            self.storevolcano['name']=vaac_filter['VOLCANO_NAME']
            self.storevolcano['years']={}

        if yearpath not in self.storevolcano['years']:
            self.storevolcano['years'][yearpath]=[]
            dtg_fl_ad={}
            dtg_fl_ad['date']= vaac_filter['DATE']
            dtg_fl_ad['time'] = vaac_filter['TIME']
            dtg_fl_ad['fl'] = vaac_filter['FL']
            dtg_fl_ad['advice_date']= vaac_filter['ADVICE_DATE']
            dtg_fl_ad['advice_time']= vaac_filter['ADVICE_TIME']
            self.storevolcano['years'][yearpath].append(dtg_fl_ad)
            self.year_num_files[yearpath]=1
            self.year_cont = self.year_cont + 1
        else:
            dtg_fl_ad={}
            dtg_fl_ad['date']= vaac_filter['DATE']
            dtg_fl_ad['time'] = vaac_filter['TIME']
            dtg_fl_ad['fl'] = vaac_filter['FL']
            dtg_fl_ad['advice_date']= vaac_filter['ADVICE_DATE']
            dtg_fl_ad['advice_time']= vaac_filter['ADVICE_TIME']
            dtg_fl_ad['colour_code']= vaac_filter['COLOUR_CODE']
            self.storevolcano['years'][yearpath].append(dtg_fl_ad)
            if self.year_num_files[yearpath] < (num_files -1):
                self.year_num_files[yearpath]= self.year_num_files[yearpath] + 1
            elif self.year_cont == (num_years):
                self.log("year %s , total file stored %s, total file per year %s" %(yearpath,self.year_num_files[yearpath],num_files))
                name="filtered_%s.json"%(self.volcano_id) 
                with open(name,'w+') as outfile:
                    json.dump(self.storevolcano, outfile)
	

from dispel4py.workflow_graph import WorkflowGraph

graph = WorkflowGraph()
read = ReadDataPE("./")
filter = FilterPE()
writejson = WriteJsonPE()
graph.connect(read, 'output', filter, 'input')
graph.connect(filter, 'output', writejson, 'input')
