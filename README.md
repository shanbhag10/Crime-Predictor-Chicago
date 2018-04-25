# Crime Predictor: Chicago

## Pre-requisites

* Third party Python modules
  * [panadas](https://pandas.pydata.org/pandas-docs/stable/install.html)
  * [numpy](https://pypi.org/project/numpy/)
  * [tabulate](https://pypi.org/project/tabulate/)

## STEP 1: Clone the repository

Please run the command ``git clone https://github.com/shanbhag10/Crime-Predictor-Chicago.git``

## STEP 2: Change the directory to scripts

Please run the command ``cd <PATH_OF_CLONE_FOLDER>/Crime-Predictor-Chicago/scripts``

## STEP 3: Pre process raw data [ONLY IF REQUIRED]

Please run the command ``python3 preProcessData.py ../config/<PRE_PROCESS_FILE>.config ../config/<MAIN_PROCESS_FILENAME>.config``

Example:

``python3 preProcessData.py ../config/preprocess_all.config ../config/main.config``

The structure of <PRE_PROCESS_FILE>.config is as follows

First Line: ``<OUTPUT_FILE_FOR_MAIN_ALGO>``
Second Line``<RAW_FILE_PATH>,<ROW_FILTER_KEY>,<COL_NAME_HAVING_THE_FILTER_KEY>,<COL_NAME_FOR_LATITUDE>,<COL_NAME_FOR_LONGITUDE>``

For multiple files put each entry on a new line

**NOTE**: The ROW_FILTER_KEY and COL_NAME_HAVING_THE_FILTER_KEY can be empty if you don't want to filter rows

Example content:

../data/input/allFeatures.csv
../data/overlap/crime.csv,HOMICIDE,PRIMARY DESCRIPTION,LATITUDE,LONGITUDE<br>
../data/overlap/bars.csv,,,LATITUDE,LONGITUDE<br>
../data/overlap/church.csv,,,"LAT","LONG"<br>
../data/overlap/library.csv,,,LAT,LONG<br>
../data/overlap/school.csv,,,Lat,Long<br>
../data/overlap/police.csv,,,LATITUDE,LONGITUDE<br>

## STEP 4: Create the <MAIN_PROCESS_FILENAME> [ONLY IF Pre processing step is skipped]

Create a file <MAIN_PROCESS_FILENAME>.config in the config directory with the names of clean combined input file separated by ','

Example Content:

``../data/input/allFeatures.csv
``

Please make sure that the file above only has a UID, latitude, longitude and Feature values for each record for the corresponding feature in a new line

Example input file content: ../data/input/allFeatures.csv

1,41.86922,-87.66249,bars<br>
2,41.86923,-87.66249,bars<br>
3,41.86921,-87.66248,school<br>
4,41.86923,-87.66248,school<br>
5,41.86920,-87.66247,police

## STEP 5: Run the Main algorithm

Run the following command

``python3 colocationAlgo.py ../config/<MAIN_PROCESS_FILENAME>.config > ../data/output/<OUTPUT_FILE_NAME>.txt``

Example:

``python3 colocationAlgo.py ../config/main.config > ../data/output.txt``
