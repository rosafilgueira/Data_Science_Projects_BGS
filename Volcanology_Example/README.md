# Automatic Information retrieval and extraction from volcanic ash advisory centers for further analysis

In this directory, I have stored the codes (vaac_preprocess.py and vaac_process.py) for “Automatic Information retrieval and extraction from volcanic ash advisory centers for further analysis” → They have difficulties for downloading all these information automatically  extracting the desired information and putting into a format that is easy for analysis.

The solution adopted in this case, is the implementation of a data-pipeline (vaac_preprocess.py) information extraction workflow that captures and filters the desired information and gathers them in a easy format (json files) for analysis.
An additional python program (vaac_process.py) was created for performing analysis (interpolation) on the extracted data (json files), which creates several output files (csv files) and figures (jpg) as output data. 

## Data science areas
The areas of this project can be classified listed as: Information Extraction; Software engineering; Statistics; Parallel computing; and Parallel Systems.

## Resources used
data-pipeline workflow + python + pandas library 


## Commands for running the programs:  
- dispel4py simple vaac_preprocess.py
- more filtered_261080.json 
- python vaac_process.py
- cd Results

## Notes: 
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
