In svm_model directory I have everything:

Input data stored in ../Label_Data/ directory
0. classification_module
1. train_classifier_svm.py
export PYTHONPATH=$PYTHONPATH:.
> python svm_model/train_classifier_svm.py 
2. show_informative_features.py
> python svm_model/show_informative_features.py 


3. apply_classifier_general.py (I have several versions) -> svm_model/Readme_apply_classifier_versions.txt
Input data stored in ../Data/ directory
> dispel4py simple svm_model.apply_classifier_general -d '{"read" : [ {"input" : "tweets_8_9_May_2016_page_1.json"} ]}' 
	(Store the results in ./Results/prediction_LR.csv )
