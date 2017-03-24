import pandas
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize



class ReadData:
	def read_vaac(self, filename) :
		print('reading %s'% filename)
		with open(filename) as inputfile:
			data_volcano = json.load(inputfile)
			array_volcano=[]
			for i in data_volcano['years']:
				array_volcano.append(json_normalize(data_volcano['years'][i]))
		return array_volcano	

class ProcessData:
	def process_fl(self, array_volcano):
		print array_volcano
		for i in range(len(array_volcano)):
			df=array_volcano[i]
			data = df[['date', 'time', 'fl']]
			data['date'] = pandas.to_datetime(data['date'] + data['time'])
			del data['time']
			data['fl']= data['fl'].convert_objects(convert_numeric=True)
			data.set_index(['date'], inplace=True)
		
			#####interpolation######
			#data.interpolate(method='time', downcast='infer')	
			data.interpolate(method='linear', downcast='infer')	
			##### ploting and storing ####
			plot_name="Results/fl_interpolated_"+str(i)
			file_name="Results/fl_interpolated_"+ str(i)+".csv"
			ax = data.plot(style='k--', colormap = 'summer', markersize=4, label='FL', title='Time Series FL per year', x_compat=True)
			fig = ax.get_figure()
			fig.savefig(plot_name)
			data.to_csv(file_name, encoding='utf-8')
			print data
			#data.to_json(filename)
		
			

if __name__ == '__main__':

	rd = ReadData()
	array_volcano = rd.read_vaac('filtered_261080.json')
	pd = ProcessData()
	pd.process_fl(array_volcano)

