In this directory, I have stored the codes (vaac_preprocess.py and vaac_process.py) for “Automatic Information retrieval and extraction from volcanic ash advisory centers for further analysis” → They have difficulties for downloading all these information automatically (from ftp servers, where are many directories per year, an each of them contains several text files), extracting the desired information and putting into a format that is easy for analysis.
The solution adopted in this case, is the implementation of a data-pipeline (vaac_preprocess.py) information extraction workflow that captures and filters the desired information and gathers them in a easy format (json files) for analysis.
An additional python program (vaac_process.py) was created for performing analysis (interpolation) on the extracted data (json files), which creates several output files (csv files) and figures (jpg) as output data. 

The daata science areas of this project can be classified listed as: Information Extraction; Software engineering; Statistics; Parallel computing; and Parallel Systems.

Resource used: data-pipeline workflow + python + pandas library 


Commands for running the programs:  
>> dispel4py simple vaac_preprocess.py
>> more filtered_261080.json 
>> python vaac_process.py
>> cd Results
>> ls 
fl_interpolated_0.csv
fl_interpolated_1.csv
fl_interpolated_2.csv
fl_interpolated_3.csv
fl_interpolated_4.csv
fl_interpolated_0.png
fl_interpolated_1.png
fl_interpolated_2.png
fl_interpolated_3.png
fl_interpolated_4.png

Notes: 
Structure of the filtered_261080.json file is:
 {“id”: id_volcano , 
  “name”: name_volcano, 
  “years”:{ 
 2010 :[ {“date”: date, “time”: time, “fl”: fl, “advice_time”: advice_time, “advice_date”: advice_date, “colour_code": colour_code }, 
              {“date”: date, “time”: time, “fl”: fl, “advice_time”: advice_time, “advice_date”: advice_date, “colour_code": colour_code },  …. ]

2015:[ {“date”: date, “time”: time, “fl”: fl, “advice_time”: advice_time, “advice_date”: advice_date, “colour_code": colour_code }, 
              {“date”: date, “time”: time, “fl”: fl, “advice_time”: advice_time, “advice_date”: advice_date, “colour_code": colour_code },  …. ]
}


The vaac_process.py generates plots and time-series cvs files, per year, to analyse the Fl values. 
